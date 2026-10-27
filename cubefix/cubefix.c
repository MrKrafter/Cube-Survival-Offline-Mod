// Cube Survival: LDoE offline fix.
// The game talks to Kefir's servers through 5 Request classes (GetRequest, GetWWWRequest, PostRequest,
// GetByteRequest, GetWWWByteRequest). Their servers are gone, so we replace those classes' Load/CheckLoaded/
// GetResponse/GetByteResponse/GetError with a tiny in-process "server" that answers by URL:
//   config (voxel_config.json?ts=) -> config pointing every service at http://cube.offline/...
//   /ping                         -> current unix time
//   /refs                         -> embedded references blob (same format the server sent: xor 0x63 + lz4)
//   /battle/1/                    -> {"uid","auth"} (new offline account)
//   .../get                       -> "" (game falls back to the local save)
//   .../set, transactions         -> {"result":"ok"}
//   anything else                 -> "" (feature just fails quietly)
// Also skips the Google Play OBB downloader (OBB data is packed into the APK).
#include <android/log.h>
#include <dlfcn.h>
#include <link.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <time.h>
#include <unistd.h>
#include <jni.h>

#define LOG(...) __android_log_print(ANDROID_LOG_INFO, "cubefix", __VA_ARGS__)

// RVAs in libil2cpp.so (Cube Survival 1.0.4, versionCode 26)
enum {
    RVA_GetByteRequest_Load = 0x19A6288, RVA_GetByteRequest_CheckLoaded = 0x19A6300,
    RVA_GetByteRequest_GetResponse = 0x19A6414, RVA_GetByteRequest_GetError = 0x19A653C,
    RVA_GetByteRequest_GetByteResponse = 0x19A6628,
    RVA_GetRequest_Load = 0x19A676C, RVA_GetRequest_CheckLoaded = 0x19A6B18,
    RVA_GetRequest_GetResponse = 0x19A6C2C, RVA_GetRequest_GetError = 0x19A6D54,
    RVA_GetWWWByteRequest_Load = 0x19A6F20, RVA_GetWWWByteRequest_CheckLoaded = 0x19A6F98,
    RVA_GetWWWByteRequest_GetResponse = 0x19A6FC8, RVA_GetWWWByteRequest_GetByteResponse = 0x19A6FF0,
    RVA_GetWWWByteRequest_GetError = 0x19A70CC,
    RVA_GetWWWRequest_Load = 0x19A72CC, RVA_GetWWWRequest_CheckLoaded = 0x19A7658,
    RVA_GetWWWRequest_GetResponse = 0x19A7688, RVA_GetWWWRequest_GetError = 0x19A77A4,
    RVA_PostRequest_Load = 0x19A79B0, RVA_PostRequest_CheckLoaded = 0x19A7C10,
    RVA_PostRequest_GetResponse = 0x19A7D24, RVA_PostRequest_GetError = 0x19A7F00,
    RVA_GooglePlayDownloader_RunningOnAndroid = 0x1EC4DA4,
};
// Request field offsets
#define REQ_URL 0x18

extern const unsigned char cube_refs[];
extern const unsigned int cube_refs_size;

typedef struct Il2CppString { void *klass, *monitor; int32_t length; uint16_t chars[]; } Il2CppString;
typedef struct Il2CppArray { void *klass, *monitor, *bounds; int32_t max_length; uint8_t data[]; } Il2CppArray;

// mods.c
void mods_install(uintptr_t base, void *(*sym)(const char *));
void mods_jni(JavaVM *vm);

static uintptr_t g_base;
static void *g_il2cpp;
static Il2CppString *(*p_string_new)(const char *);
static void *(*p_array_new)(void *klass, uintptr_t n);
static void *(*p_class_from_name)(void *image, const char *ns, const char *name);
static void *(*p_get_corlib)(void);
static void *g_byte_class;

static const char *OFF = "http://cube.offline/";

static void url_of(void *req, char *out, size_t cap) {
    Il2CppString *s = *(Il2CppString **)((char *)req + REQ_URL);
    size_t n = 0;
    if (s)
        for (int i = 0; i < s->length && n + 1 < cap; i++) out[n++] = s->chars[i] < 128 ? (char)s->chars[i] : '?';
    out[n] = 0;
}

static int ends_with(const char *s, const char *t) {
    size_t a = strlen(s), b = strlen(t);
    return a >= b && !strcmp(s + a - b, t);
}

static char *g_config;

static const char *config_json(void) {
    if (g_config) return g_config;
    const char *ver =
        "{\"platform\":[\"android\",\"ios\",\"amazon\",\"editor\"],\"maintenance\":[],"
        "\"battle_url\":[\"http://cube.offline/battle/\"],\"main_url\":[\"http://cube.offline/main/\"],"
        "\"raid_locations_url\":[\"http://cube.offline/raid/\"],\"data_crc\":[],\"wait_save_time\":2.7,"
        "\"ping_urls\":[\"http://cube.offline/ping\"],\"ads_lang\":[],\"reference_urls\":[\"http://cube.offline/refs\"],"
        "\"show_patch_note\":false,\"patch_note\":0,\"crc_path\":[],\"patch_note_urls\":[]}";
    size_t one = strlen(ver) + 16, cap = 64 + one * 301;
    char *b = malloc(cap), *p = b;
    p += sprintf(p, "{\"versions\":{");
    for (int v = 0; v <= 300; v++) p += sprintf(p, "%s\"%d\":%s", v ? "," : "", v, ver);
    sprintf(p, "}}");
    g_config = b;
    return b;
}

static char g_reply[256];

static const char *answer(void *req) {
    char url[512];
    url_of(req, url, sizeof url);
    const char *r = "";
    if (!strncmp(url, OFF, strlen(OFF))) {
        const char *path = url + strlen(OFF);
        char *q = strchr(path, '?');
        if (q) *q = 0;
        if (!strncmp(path, "ping", 4)) {
            snprintf(g_reply, sizeof g_reply, "%lld", (long long)time(NULL));
            r = g_reply;
        } else if (!strncmp(path, "battle/", 7)) {
            snprintf(g_reply, sizeof g_reply, "{\"uid\":\"off%08lx%04x\",\"auth\":\"offline\"}",
                     (unsigned long)time(NULL), (unsigned)(getpid() & 0xffff));
            r = g_reply;
        } else if (ends_with(path, "/get")) {
            r = "";
        } else if (ends_with(path, "/set") || strstr(path, "transactions_")) {
            r = "{\"result\":\"ok\"}";
        }
    } else if (strstr(url, "?ts=") || strstr(url, "voxel_config")) {
        r = config_json();
    }
    LOG("request %s -> %.80s", url, r);
    return r;
}

// byte[] needs System.Byte's class; resolved lazily (corlib is only available after il2cpp_init).
static void *byte_class(void) {
    if (!g_byte_class) g_byte_class = p_class_from_name(p_get_corlib(), "System", "Byte");
    return g_byte_class;
}

static void h_Load(void *self, void *method) { (void)self; (void)method; }
static int h_CheckLoaded(void *self, double dt, void *method) { (void)self; (void)dt; (void)method; return 1; }
static void *h_GetError(void *self, void *method) { (void)self; (void)method; return NULL; }
static void *h_GetResponse(void *self, void *method) { (void)method; return p_string_new(answer(self)); }

static void *h_GetByteResponse(void *self, void *method) {
    (void)method;
    char url[512];
    url_of(self, url, sizeof url);
    const unsigned char *src;
    size_t n;
    if (strstr(url, "cube.offline/refs")) {
        src = cube_refs, n = cube_refs_size;
    } else {
        const char *s = answer(self);
        src = (const unsigned char *)s, n = strlen(s);
    }
    LOG("bytes %s -> %zu", url, n);
    Il2CppArray *a = p_array_new(byte_class(), n);
    memcpy(a->data, src, n);
    return a;
}

static int h_RunningOnAndroid(void *method) { (void)method; return 0; }

// Overwrite an ARM-mode function entry with "ldr pc,[pc,#-4]; .word target".
static void hook(uintptr_t rva, void *fn) {
    uint32_t *p = (uint32_t *)(g_base + rva);
    uintptr_t page = (uintptr_t)p & ~(uintptr_t)4095;
    mprotect((void *)page, 8192, PROT_READ | PROT_WRITE | PROT_EXEC);
    p[0] = 0xe51ff004;
    p[1] = (uint32_t)(uintptr_t)fn;
    mprotect((void *)page, 8192, PROT_READ | PROT_EXEC);
    __builtin___clear_cache((char *)p, (char *)(p + 2));
}

static void *il2cpp_sym(const char *name) { return dlsym(g_il2cpp, name); }

// Called once libil2cpp.so is loaded (from JNI_OnLoad here, or by the 64-bit loader).
__attribute__((visibility("default"))) int cubefix_install(void *il2cpp_handle) {
    if (g_base) return 0;
    void *h = il2cpp_handle ? il2cpp_handle : dlopen("libil2cpp.so", RTLD_NOW);
    if (!h) { LOG("dlopen libil2cpp failed: %s", dlerror()); return -1; }
    void *sym = dlsym(h, "il2cpp_init");
    Dl_info di;
    if (!sym || !dladdr(sym, &di)) { LOG("no il2cpp_init"); return -1; }
    p_string_new = dlsym(h, "il2cpp_string_new");
    p_array_new = dlsym(h, "il2cpp_array_new");
    p_class_from_name = dlsym(h, "il2cpp_class_from_name");
    p_get_corlib = dlsym(h, "il2cpp_get_corlib");
    g_base = (uintptr_t)di.dli_fbase;
    LOG("libil2cpp base %p", (void *)g_base);

    static const struct { uintptr_t rva; void *fn; } H[] = {
        {RVA_GetByteRequest_Load, h_Load}, {RVA_GetByteRequest_CheckLoaded, h_CheckLoaded},
        {RVA_GetByteRequest_GetResponse, h_GetResponse}, {RVA_GetByteRequest_GetError, h_GetError},
        {RVA_GetByteRequest_GetByteResponse, h_GetByteResponse},
        {RVA_GetRequest_Load, h_Load}, {RVA_GetRequest_CheckLoaded, h_CheckLoaded},
        {RVA_GetRequest_GetResponse, h_GetResponse}, {RVA_GetRequest_GetError, h_GetError},
        {RVA_GetWWWByteRequest_Load, h_Load}, {RVA_GetWWWByteRequest_CheckLoaded, h_CheckLoaded},
        {RVA_GetWWWByteRequest_GetResponse, h_GetResponse}, {RVA_GetWWWByteRequest_GetByteResponse, h_GetByteResponse},
        {RVA_GetWWWByteRequest_GetError, h_GetError},
        {RVA_GetWWWRequest_Load, h_Load}, {RVA_GetWWWRequest_CheckLoaded, h_CheckLoaded},
        {RVA_GetWWWRequest_GetResponse, h_GetResponse}, {RVA_GetWWWRequest_GetError, h_GetError},
        {RVA_PostRequest_Load, h_Load}, {RVA_PostRequest_CheckLoaded, h_CheckLoaded},
        {RVA_PostRequest_GetResponse, h_GetResponse}, {RVA_PostRequest_GetError, h_GetError},
        {RVA_GooglePlayDownloader_RunningOnAndroid, h_RunningOnAndroid},
    };
    for (size_t i = 0; i < sizeof H / sizeof H[0]; i++) hook(H[i].rva, H[i].fn);
    LOG("hooks installed");
    g_il2cpp = h;
    mods_install(g_base, il2cpp_sym);
    return 0;
}

JNIEXPORT jint JNI_OnLoad(JavaVM *vm, void *reserved) {
    (void)reserved;
    cubefix_install(NULL);
    mods_jni(vm);
    return JNI_VERSION_1_6;
}
