// Cube Survival mod menu, native side of cube.mod.ModMenu (Java).
// The menu opens from Settings -> Support; its switches toggle the il2cpp hooks installed here.
// Hooks that still need the original function get a trampoline (first 2 instructions + jump back).
#include <android/log.h>
#include <dirent.h>
#include <jni.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <time.h>
#include <unistd.h>

#define LOG(...) __android_log_print(ANDROID_LOG_INFO, "cubemod", __VA_ARGS__)

// Shared with ModMenu.java
enum mod_id {
    MOD_SPEED, MOD_GOD, MOD_DUPE, MOD_FREE_SHOP, MOD_FREE_TRAVEL, MOD_UNLOCK, MOD_FREE_CRAFT, MOD_NO_ADS,
    MOD_NO_DURABILITY, MOD_INSTANT_WORK, MOD_ONE_HIT, MOD_FAST_ATTACK, MOD_INSTANT_LOOT, MOD_BUNKER,
    MOD_UNLOCK_RESEARCH, MOD_NOCLIP, MOD_FREEZE_EVENTS, MOD_FREE_ASSEMBLY, MOD_HIDE_UI, MOD_COUNT
};

// RVAs in libil2cpp.so (Cube Survival 1.0.4, versionCode 26)
enum {
    RVA_SettingsDialog_OnSupportButtonClick = 0x12DB7B8,
    RVA_LocalizationManager_get_CurrentLanguageCode = 0x1C517CC,
    RVA_ConsumableResource_get_Amount = 0x2035790, RVA_ConsumableResource_Update = 0x20357D0,
    RVA_ConsumableResource_get__amount = 0x20356E8, RVA_ConsumableResource_set__amount = 0x2035710,
    RVA_CharacterController_SimpleMove = 0x22E5E34, RVA_Component_get_transform = 0x207A570,
    RVA_Transform_get_position = 0x226DB34, RVA_Transform_set_position = 0x226DBF4, RVA_Time_get_deltaTime = 0x226CA50,
    RVA_WeaponAttackAction_OnInit = 0x1D163AC, RVA_WeaponAttackAction_CalculateDamage = 0x1D1862C,
    RVA_DurabilityInventoryStack_ChangeDurability = 0x1D4A72C,
    RVA_Workbench_MoveProgress = 0x1D11930,
    RVA_UnlockLootObjectAction_OnUpdate = 0x1D22D08,
    RVA_CodeLocation_CheckCode = 0x17E2DDC, RVA_BunkerComputerController_CheckUse = 0x16BB420,
    RVA_Research_Check = 0x2031498, RVA_ResearchRequirement_Check = 0x2028B70, RVA_LevelRequirement_Check = 0x2026AC0,
    RVA_ActionDescription_ctor = 0x19AC548, RVA_ActionDescription_Make = 0x19ACAB0, RVA_Arguments_ctor = 0x19B5700,
    RVA_GlobalMapMovement_Update = 0x1D31F7C, RVA_GlobalMapMovement_CallEventSpawned = 0x1D35D20,
    RVA_Player_get_TimeNow = 0x19E3230, RVA_Player_get_GlobalMapMovement = 0x19E0284,
    RVA_GlobalMapEvent_Set = 0x1D28C64,
    RVA_GameManager_get_Player = 0x2387BB4,
    RVA_MoveAction_GetSpeed = 0x17F6A1C, RVA_MovePathAction_GetSpeed = 0x17F71A0,
    RVA_HealthController_Attach = 0x143F2E8,
    RVA_LimitedResource_get_Amount = 0x20379EC, RVA_LimitedResource_set_Amount = 0x20379F0,
    RVA_Inventories_CheckSplit_cmp = 0x1D3E20C,                                    // cmp r0,#1 (count > 1)
    RVA_Inventories_Split_left = 0x1D3EA88, RVA_Inventories_Split_left2 = 0x1D3EB14, // amount taken off the source
    RVA_PaymentsManager_BuyItem = 0x188CC38, RVA_PaymentsManager_CallComplete = 0x188E598,
    RVA_TransactionManager_AddTransaction = 0x19ABC00, RVA_TransactionManager_UseAllUnusedTransaction = 0x19AB8A8,
    RVA_StaticResourcePrice_Check = 0x1FD42F4, RVA_StaticResourcePrice_Pay = 0x1FD4518,
    RVA_InventoryStacksPrice_Check = 0x1FD2CCC, RVA_InventoryStacksPrice_Pay = 0x1FD322C,
    RVA_GlobalMapMovement_GetBoostPrice = 0x1D32DF0, RVA_GlobalMapMovement_get_BoostEnergyPrice = 0x1D32484,
    RVA_GlobalMapLocationDescription_ctor = 0x1D29864,
    RVA_GlobalMapEvent_Update = 0x1D2879C, RVA_GlobalMapEvent_get_TsNow = 0x1D2869C, RVA_GlobalMapEvent_SetTs = 0x1D28EC4,
    RVA_GlobalMapEventPointContainer_SetFormatedTime = 0x1778870,
    RVA_PvpLocationLoader_CallFailed = 0x19A12A8, RVA_GlobalMapController_OnPvpLocationLoadCompleted = 0x17751E8,
    RVA_GameSceneManager_SwitchLevel = 0x239C634, RVA_GameSceneManager_OnShown = 0x23A547C,
    RVA_CryptoManager_GetDataFiles = 0x2398C28,
    RVA_AdsManager_ShowRewardedAd = 0x2395204, RVA_AdsManager_HandleShowResult = 0x2395348,
    RVA_Advertisement_get_isInitialized = 0x22D8A20, RVA_Advertisement_get_isSupported = 0x22D8B3C,
    RVA_Advertisement_IsReady = 0x22D9818,
    RVA_PlayGamesPlatform_Authenticate = 0x1C38610,
    RVA_BuildingCollection_get_IsBuilded = 0x1F83034,
    RVA_InventoryPanelController_UpdateItems = 0x168E480, RVA_CharacterModel_get_Inventories = 0x17D7BE8,
    RVA_Object_Instantiate_parent = 0x21B24D8, RVA_Transform_get_parent = 0x226E9E0,
    RVA_Object_FindObjectsOfType = 0x21B19C0, RVA_Resources_FindObjectsOfTypeAll = 0x21BD5C4,
RVA_Component_get_gameObject = 0x207A5E0,
    RVA_GameObject_GetComponent = 0x207A680, RVA_GameObject_AddComponent = 0x20817C4,
    RVA_Canvas_get_isRootCanvas = 0x22E2324, RVA_CanvasGroup_get_alpha = 0x22E3030, RVA_CanvasGroup_set_alpha = 0x22E30A0,
    RVA_Object_get_name = 0x21AF7C0, RVA_Behaviour_get_enabled = 0x2075EA4, RVA_Behaviour_set_enabled = 0x2075F14,
};
// Field offsets
#define GM_PLAYERS_MANAGER 0x54
#define GM_TRANSACTION_MANAGER 0x5C
#define PLAYER_CHARACTER 0x2C
#define HC_HEALTH_RESOURCE 0x1C
#define HC_IS_PLAYER 0x4C
#define RES_ID 0x10       // Resource._id
#define CONS_MAXIMUM 0x24 // ConsumableResource._maximum
#define PM_MANAGER 0x18
#define PM_COMPLETE 0x24
#define PM_FAIL 0x28
#define SRP_RESOURCE 0xC
#define LOC_REQUIREMENTS 0x10 // _requirement, _walkRequirement, _runRequirement
#define DESC_ID 0x8 // Description._id
#define CM_PATH_SAVE 0x18 // CryptoManager._pathSave (<files>/asn.fdat)
#define EV_NAME 0x8 // Identified._id
#define EV_DESCRIPTION 0x24
#define EV_TS 0x28 // end of the event
#define EVD_LOCATIONS 0x10 // GlobalMapEventDescription._locations (List<string>)
#define EVD_LEVEL 0x20
#define ADS_ACTION 0x24
#define ADS_FAIL_ACTION 0x28
#define SHOW_RESULT_FINISHED 2
#define WAA_ATTACK_DAMAGE_TIME 0x40 // WeaponAttackAction._attackDamageSpeed (seconds to the hit)
#define WAA_ATTACK_ENDING_TIME 0x44
#define WAA_IS_PLAYER 0x60
#define WAA_RECHARGE_TIME 0x74
#define RESEARCH_IS_BOUGHT 0x1C
#define GMM_PLAYER 0x20
#define GMM_ROAD 0x58 // List<RoadPart>
#define GMM_IS_MOVING 0x64
#define GMM_START_TS 0x50
#define ROAD_TS_START 0x18
#define ROAD_TS_END 0x20
#define IPC_ITEMS 0x28  // InventoryPanelController._items (its container's slot list)
#define INVS_PARTS 0x18 // Inventories.InventoryParts (List<IInventory>)
#define INV_CELLS 0x10  // Inventory.Cells (List<IInventoryCell>)
#define LIST_ITEMS 0x8
#define LIST_SIZE 0xC
#define LIST_VERSION 0x10
#define ARRAY_LENGTH 0xC
#define ARRAY_DATA 0x10
#define SPAWNED_EVENT_TIME (3 * 3600.0)
#define MIN_SANE_TS 1e9               // game clock (unix seconds) before it is set
#define MAX_EVENT_LEFT (60 * 86400.0) // no real event lasts this long
#define ONE_HIT_DAMAGE 1000000
#define FAST_ATTACK_SCALE 0.1f

typedef struct Il2CppString { void *klass, *monitor; int32_t length; uint16_t chars[]; } Il2CppString;

static uintptr_t g_base;
static volatile int g_opt[MOD_COUNT] = {[MOD_SPEED] = 10};

static void *(*il2cpp_domain_get_)(void);
static void **(*il2cpp_domain_get_assemblies_)(void *domain, size_t *size);
static void *(*il2cpp_assembly_get_image_)(void *assembly);
static const char *(*il2cpp_image_get_name_)(void *image);
static void *(*il2cpp_class_from_name_)(void *image, const char *ns, const char *name);
static void *(*il2cpp_class_get_field_from_name_)(void *klass, const char *name);
static void (*il2cpp_field_static_get_value_)(void *field, void *out);
static void *(*il2cpp_object_get_class_)(void *obj);
static const char *(*il2cpp_class_get_name_)(void *klass);
static uint32_t (*il2cpp_gchandle_new_)(void *obj, int pinned);
static void *(*il2cpp_string_new_)(const char *s);
static void *(*il2cpp_object_new_)(void *klass);
static void *(*il2cpp_array_new_)(void *element_class, uint32_t length);
static void *(*il2cpp_class_get_element_class_)(void *klass);
static const void *(*il2cpp_class_get_type_)(void *klass);
static void *(*il2cpp_type_get_object_)(const void *type);

#define FIELD(obj, off, type) (*(type *)((char *)(obj) + (off)))
#define FN(rva) ((void *)(g_base + (rva)))

// ---- code patching ----

static void write_code(uint32_t *p, const uint32_t *words, int n) {
    uintptr_t page = (uintptr_t)p & ~(uintptr_t)4095;
    mprotect((void *)page, 8192, PROT_READ | PROT_WRITE | PROT_EXEC);
    for (int i = 0; i < n; i++) p[i] = words[i];
    mprotect((void *)page, 8192, PROT_READ | PROT_EXEC);
    __builtin___clear_cache((char *)p, (char *)(p + n));
}

// Instructions that can't be copied into a trampoline as is.
static int pc_relative(uint32_t i) {
    if (i >> 28 == 0xF || ((i >> 25) & 7) == 5) return 1;                  // unconditional space, b/bl
    if (((i >> 16) & 0xF) == 15 || ((i >> 12) & 0xF) == 15) return 1;      // Rn / Rd is pc
    return ((i >> 25) & 7) == 0 && (i & 0xF) == 15;                         // Rm is pc
}

static uint32_t *g_tramp;
static int g_ntramp;

// Redirect the function at rva to fn; returns a callable original, or NULL (hook not installed).
static void *hook(uintptr_t rva, void *fn) {
    uint32_t *p = (uint32_t *)(g_base + rva);
    if (pc_relative(p[0]) || pc_relative(p[1]) || g_ntramp * 16 >= 4096) {
        LOG("hook %#x: prologue %08x %08x not relocatable", (unsigned)rva, p[0], p[1]);
        return NULL;
    }
    uint32_t *t = g_tramp + g_ntramp++ * 4;
    t[0] = p[0], t[1] = p[1], t[2] = 0xe51ff004, t[3] = (uint32_t)(uintptr_t)(p + 2);
    __builtin___clear_cache((char *)t, (char *)(t + 4));
    uint32_t j[2] = {0xe51ff004, (uint32_t)(uintptr_t)fn};
    write_code(p, j, 2);
    return t;
}

// ---- il2cpp helpers ----

static void *csharp_image(void) {
    static void *img;
    size_t n = 0;
    if (img) return img;
    void **as = il2cpp_domain_get_assemblies_(il2cpp_domain_get_(), &n);
    for (size_t i = 0; i < n; i++) {
        void *im = il2cpp_assembly_get_image_(as[i]);
        if (!strcmp(il2cpp_image_get_name_(im), "Assembly-CSharp.dll")) return img = im;
    }
    return NULL;
}

static void *game_manager(void) {
    static void *field;
    if (!field) {
        void *k = csharp_image() ? il2cpp_class_from_name_(csharp_image(), "Assets.Core.Manager", "GameManager") : NULL;
        if (k) field = il2cpp_class_get_field_from_name_(k, "Instance");
        if (!field) return NULL;
    }
    void *gm = NULL;
    il2cpp_field_static_get_value_(field, &gm);
    return gm;
}

static void *player_character(void) {
    static void *(*get_player)(void *, void *);
    if (!get_player) get_player = FN(RVA_GameManager_get_Player);
    void *gm = game_manager();
    if (!gm || !FIELD(gm, GM_PLAYERS_MANAGER, void *)) return NULL;
    void *player = get_player(gm, NULL);
    return player ? FIELD(player, PLAYER_CHARACTER, void *) : NULL;
}

static int str_is(Il2CppString *s, const char *t) {
    if (!s || s->length != (int32_t)strlen(t)) return 0;
    for (int i = 0; i < s->length; i++)
        if (s->chars[i] != (uint8_t)t[i]) return 0;
    return 1;
}

static void str_ascii(Il2CppString *s, char *out, size_t cap) {
    size_t n = 0;
    if (s)
        for (int i = 0; i < s->length && n + 1 < cap; i++) out[n++] = s->chars[i] < 128 ? (char)s->chars[i] : '?';
    out[n] = 0;
}

static const char *class_name(void *obj) {
    return obj ? il2cpp_class_get_name_(il2cpp_object_get_class_(obj)) : "";
}

// System.Collections.Generic.List<T> of references: element i, or NULL.
static int list_size(void *list) {
    return list && !strcmp(class_name(list), "List`1") ? FIELD(list, LIST_SIZE, int32_t) : 0;
}
static void *list_get(void *list, int i) {
    return ((void **)((char *)FIELD(list, LIST_ITEMS, void *) + ARRAY_DATA))[i];
}

typedef struct { float x, y, z; } Vec3;

// ---- menu ----

static JavaVM *g_vm;
static jclass g_menu;
static jmethodID g_menu_open;

static void h_OnSupportButtonClick(void *self, void *mi) {
    (void)self, (void)mi;
    static Il2CppString *(*lang_code)(void *);
    JNIEnv *env;
    if (!g_menu) return;
    // The menu follows the game's language setting, not the system locale.
    lang_code = FN(RVA_LocalizationManager_get_CurrentLanguageCode);
    Il2CppString *lang = lang_code(NULL);
    jboolean ru = lang && lang->length >= 2 && lang->chars[0] == 'r' && lang->chars[1] == 'u';
    if ((*g_vm)->GetEnv(g_vm, (void **)&env, JNI_VERSION_1_6) != JNI_OK &&
        (*g_vm)->AttachCurrentThread(g_vm, &env, NULL) != JNI_OK)
        return;
    (*env)->CallStaticVoidMethod(env, g_menu, g_menu_open, ru);
    if ((*env)->ExceptionCheck(env)) (*env)->ExceptionClear(env);
}

// ---- speed ----

static float (*o_MoveAction_GetSpeed)(void *, void *, void *);
static float (*o_MovePathAction_GetSpeed)(void *, void *, void *);
// Character whose joystick move is in progress: MoveActionView asks GetSpeed right before CharacterController.SimpleMove.
static void *volatile g_move_char;

static float scale_speed(float s, void *character) {
    int m = g_opt[MOD_SPEED];
    return m > 10 && character && character == player_character() ? s * m / 10.0f : s;
}
static float h_MoveAction_GetSpeed(void *self, void *character, void *mi) {
    g_move_char = character;
    return scale_speed(o_MoveAction_GetSpeed(self, character, mi), character);
}
static float h_MovePathAction_GetSpeed(void *self, void *character, void *mi) {
    g_move_char = NULL;
    return scale_speed(o_MovePathAction_GetSpeed(self, character, mi), character);
}

// ---- noclip: the player's joystick move shifts the transform directly, so colliders don't stop it ----

static int (*o_SimpleMove)(void *, Vec3, void *);

static int h_SimpleMove(void *cc, Vec3 speed, void *mi) {
    static void *(*get_transform)(void *, void *);
    static Vec3 (*get_position)(void *, void *);
    static void (*set_position)(void *, Vec3, void *);
    static float (*delta_time)(void *);
    void *c = g_move_char;
    g_move_char = NULL;
    if (!g_opt[MOD_NOCLIP] || !c || c != player_character()) return o_SimpleMove(cc, speed, mi);
    get_transform = FN(RVA_Component_get_transform), get_position = FN(RVA_Transform_get_position);
    set_position = FN(RVA_Transform_set_position), delta_time = FN(RVA_Time_get_deltaTime);
    void *tr = get_transform(cc, NULL);
    if (!tr) return o_SimpleMove(cc, speed, mi);
    Vec3 p = get_position(tr, NULL);
    float dt = delta_time(NULL);
    p.x += speed.x * dt, p.z += speed.z * dt; // height stays: no gravity, no falling through the floor
    set_position(tr, p, NULL);
    return 1;
}

// ---- god mode: the player's health never goes down ----

static void *volatile g_player_health;
static void (*o_HealthController_Attach)(void *, void *, void *);
static void (*o_LimitedResource_set_Amount)(void *, double, void *);

static void h_HealthController_Attach(void *hc, void *model, void *mi) {
    o_HealthController_Attach(hc, model, mi);
    if (model && (FIELD(hc, HC_IS_PLAYER, uint8_t) || model == player_character())) {
        g_player_health = FIELD(hc, HC_HEALTH_RESOURCE, void *);
        LOG("player health resource %p", g_player_health);
    }
}

static void h_LimitedResource_set_Amount(void *res, double v, void *mi) {
    static double (*get_amount)(void *, void *);
    if (!get_amount) get_amount = FN(RVA_LimitedResource_get_Amount);
    if (g_opt[MOD_GOD] && res && res == g_player_health && v < get_amount(res, NULL)) return;
    o_LimitedResource_set_Amount(res, v, mi);
}

// Hunger and thirst are ConsumableResources that grow from 0 (fed) to 100 over time; god mode keeps them at 0.
// After each Update the private _amount goes back to 0. Not through set_Amount: that also moves the resource's
// clock to now, and the catch-up loop that runs when a location loads then never finishes. The HUD reads get_Amount.
static double (*o_ConsumableResource_get_Amount)(void *, void *);
static void (*o_ConsumableResource_Update)(void *, double, void *);

static int is_need(void *res) {
    Il2CppString *id = FIELD(res, RES_ID, Il2CppString *);
    return str_is(id, "hunger") || str_is(id, "thirst");
}
static double h_ConsumableResource_get_Amount(void *res, void *mi) {
    return g_opt[MOD_GOD] && is_need(res) ? 0 : o_ConsumableResource_get_Amount(res, mi);
}
static void game_tick(void);

static void h_ConsumableResource_Update(void *res, double ts, void *mi) {
    static double (*get_amount)(void *, void *);
    static void (*set_amount)(void *, double, void *);
    game_tick();
    o_ConsumableResource_Update(res, ts, mi);
    if (!g_opt[MOD_GOD] || !is_need(res)) return;
    get_amount = FN(RVA_ConsumableResource_get__amount), set_amount = FN(RVA_ConsumableResource_set__amount);
    if (get_amount(res, NULL) > 0) set_amount(res, 0, NULL);
}

// ---- one hit kills, fast attacks: the player's weapon actions ----

static int (*o_CalculateDamage)(void *, void *, int, void *);
static void (*o_WeaponAttackAction_OnInit)(void *, void *);

static int h_CalculateDamage(void *action, void *target, int critical, void *mi) {
    if (g_opt[MOD_ONE_HIT] && FIELD(action, WAA_IS_PLAYER, uint8_t)) return ONE_HIT_DAMAGE;
    return o_CalculateDamage(action, target, critical, mi);
}
// OnInit turns the weapon's times into this swing's hit, ending and recharge delays.
static void h_WeaponAttackAction_OnInit(void *action, void *mi) {
    o_WeaponAttackAction_OnInit(action, mi);
    if (!g_opt[MOD_FAST_ATTACK] || !FIELD(action, WAA_IS_PLAYER, uint8_t)) return;
    FIELD(action, WAA_ATTACK_DAMAGE_TIME, float) *= FAST_ATTACK_SCALE;
    FIELD(action, WAA_ATTACK_ENDING_TIME, float) *= FAST_ATTACK_SCALE;
    FIELD(action, WAA_RECHARGE_TIME, float) *= FAST_ATTACK_SCALE;
}

// ---- infinite durability: tools, weapons and armor never wear down ----

static int (*o_ChangeDurability)(void *, int, void *);

static int h_ChangeDurability(void *stack, int diff, void *mi) {
    return g_opt[MOD_NO_DURABILITY] && diff < 0 ? 0 : o_ChangeDurability(stack, diff, mi);
}

// ---- instant production: workbenches get a huge time step, so every possible craft completes now ----
// Fuel workbenches burn fuel by real time outside MoveProgress, so fuel still lasts as long as before.

static void (*o_MoveProgress)(void *, double, void *);

static void h_MoveProgress(void *wb, double delta, void *mi) {
    o_MoveProgress(wb, g_opt[MOD_INSTANT_WORK] ? delta + 1e7 : delta, mi);
}

// ---- instant looting: chest/door unlock actions finish on their first update ----

static void (*o_UnlockLootObjectAction_OnUpdate)(void *, double, void *);

static void h_UnlockLootObjectAction_OnUpdate(void *action, double dt, void *mi) {
    o_UnlockLootObjectAction_OnUpdate(action, g_opt[MOD_INSTANT_LOOT] ? dt + 1e6 : dt, mi);
}

// ---- Bunker Alfa: any code opens it, and the computer can restart the run at any time ----
// Normally the bunker stays "unlocked" 24 h after the computer is used and the computer is idle until then.

static int (*o_CheckCode)(void *, void *, void *);
static int (*o_BunkerComputer_CheckUse)(void *, void *);

static int h_CheckCode(void *loc, void *code, void *mi) {
    return g_opt[MOD_BUNKER] || o_CheckCode(loc, code, mi);
}
static int h_BunkerComputer_CheckUse(void *ctl, void *mi) {
    return g_opt[MOD_BUNKER] || o_BunkerComputer_CheckUse(ctl, mi);
}

// ---- researches: any research can be learned at any level, for free; recipes ignore research requirements ----
// The craft list locks a research by its level requirement through a LevelRequirementObserver, which takes the
// initial state from LevelRequirement.Check. Level requirements gate almost nothing but researches.

static int (*o_Research_Check)(void *, void *, void *);
static int (*o_ResearchRequirement_Check)(void *, void *, void *, void *);
static int (*o_LevelRequirement_Check)(void *, void *, void *, void *);

static int h_LevelRequirement_Check(void *req, void *entity, void *args, void *mi) {
    return g_opt[MOD_UNLOCK_RESEARCH] || o_LevelRequirement_Check(req, entity, args, mi);
}

static int h_Research_Check(void *r, void *player, void *mi) {
    return g_opt[MOD_UNLOCK_RESEARCH] ? !FIELD(r, RESEARCH_IS_BOUGHT, uint8_t) : o_Research_Check(r, player, mi);
}
static int h_ResearchRequirement_Check(void *req, void *entity, void *args, void *mi) {
    return g_opt[MOD_UNLOCK_RESEARCH] || o_ResearchRequirement_Check(req, entity, args, mi);
}

// ---- cut content: the patched references add actions "cubemod_give_<item>"; the menu runs them on the player ----

#define MAX_ACTIONS 512
static void *g_actions[MAX_ACTIONS];
static int g_nactions;
static char g_action_req[96]; // action id to run, taken by the next game tick
static volatile int g_action_lock;
static void (*o_ActionDescription_ctor)(void *, void *, void *, void *);

static void h_ActionDescription_ctor(void *a, void *id, void *node, void *mi) {
    o_ActionDescription_ctor(a, id, node, mi);
    Il2CppString *s = FIELD(a, DESC_ID, Il2CppString *);
    static const char P[] = "cubemod_";
    if (!s || s->length < (int)sizeof P - 1 || g_nactions >= MAX_ACTIONS) return;
    for (int i = 0; i < (int)sizeof P - 1; i++)
        if (s->chars[i] != (uint8_t)P[i]) return;
    il2cpp_gchandle_new_(a, 0);
    g_actions[g_nactions++] = a;
}

static void run_action(const char *id) {
    static void *(*get_player)(void *, void *);
    static void (*make)(void *, void *, void *, void *);
    static void (*args_ctor)(void *, void *);
    get_player = FN(RVA_GameManager_get_Player), make = FN(RVA_ActionDescription_Make);
    args_ctor = FN(RVA_Arguments_ctor);
    void *action = NULL, *gm = game_manager();
    for (int i = 0; i < g_nactions && !action; i++)
        if (str_is(FIELD(g_actions[i], DESC_ID, Il2CppString *), id)) action = g_actions[i];
    void *player = gm && FIELD(gm, GM_PLAYERS_MANAGER, void *) ? get_player(gm, NULL) : NULL;
    static void *args_class;
    if (!args_class && csharp_image())
        args_class = il2cpp_class_from_name_(csharp_image(), "Assets.Core.Models.Arguments", "Arguments");
    if (!action || !player || !args_class) {
        LOG("action %s: action %p player %p", id, action, player);
        return;
    }
    void *args = il2cpp_object_new_(args_class);
    args_ctor(args, NULL);
    make(action, player, args, NULL);
    LOG("action %s done", id);
}

// ---- hide UI (for recording): every root canvas gets a CanvasGroup with alpha 0 ----
// Alpha only stops drawing; raycasts still pass, so the joystick and buttons keep working blind.
// Groups the game already had keep their own alpha, which comes back when the option is off.

#define MAX_UI_GROUPS 64
#define MAX_UI_CAMS 4
#define HIDE_UI_PERIOD 0.2

static struct { void *group; float alpha; } g_ui_groups[MAX_UI_GROUPS];
static int g_nui_groups, g_ui_hidden;

static void *find_class(const char *ns, const char *name) {
    size_t n = 0;
    void **as = il2cpp_domain_get_assemblies_(il2cpp_domain_get_(), &n);
    for (size_t i = 0; i < n; i++) {
        void *k = il2cpp_class_from_name_(il2cpp_assembly_get_image_(as[i]), ns, name);
        if (k) return k;
    }
    return NULL;
}

static void *type_object(const char *ns, const char *name) {
    void *k = find_class(ns, name);
    return k ? il2cpp_type_get_object_(il2cpp_class_get_type_(k)) : NULL;
}

#define ARRAY_AT(arr, i) (((void **)((char *)(arr) + ARRAY_DATA))[i])
#define ARRAY_COUNT(arr) ((arr) ? FIELD(arr, ARRAY_LENGTH, int32_t) : 0)

static void update_hidden_ui(int hide) {
    static void *canvas_type, *group_type, *camera_type;
    // these two static wrappers take an unused first argument and read the Type from r1
    static void *(*find_objects)(void *, void *, void *), *(*find_all)(void *, void *, void *);
    static void *(*get_game_object)(void *, void *), *(*get_name)(void *, void *);
    static void *(*get_component)(void *, void *, void *), *(*add_component)(void *, void *, void *);
    static int (*is_root)(void *, void *), (*get_enabled)(void *, void *);
    static void (*set_enabled)(void *, int, void *);
    static float (*get_alpha)(void *, void *);
    static void (*set_alpha)(void *, float, void *);
    static void *ui_cams[MAX_UI_CAMS];
    static int nui_cams;
    if (!canvas_type) {
        if (!il2cpp_class_get_type_ || !il2cpp_type_get_object_) return;
        canvas_type = type_object("UnityEngine", "Canvas"), group_type = type_object("UnityEngine", "CanvasGroup");
        camera_type = type_object("UnityEngine", "Camera");
        if (!canvas_type || !group_type || !camera_type) {
            LOG("hide ui: Canvas %p CanvasGroup %p Camera %p", canvas_type, group_type, camera_type);
            g_opt[MOD_HIDE_UI] = 0;
            canvas_type = NULL;
            return;
        }
        find_objects = FN(RVA_Object_FindObjectsOfType), find_all = FN(RVA_Resources_FindObjectsOfTypeAll);
        get_game_object = FN(RVA_Component_get_gameObject), get_name = FN(RVA_Object_get_name);
        get_component = FN(RVA_GameObject_GetComponent), add_component = FN(RVA_GameObject_AddComponent);
        is_root = FN(RVA_Canvas_get_isRootCanvas);
        get_enabled = FN(RVA_Behaviour_get_enabled), set_enabled = FN(RVA_Behaviour_set_enabled);
        get_alpha = FN(RVA_CanvasGroup_get_alpha), set_alpha = FN(RVA_CanvasGroup_set_alpha);
    }
    // the minimap is a render texture shown by its own camera (UICamera), not through a canvas
    void *cams = find_objects(NULL, camera_type, NULL);
    for (int i = 0; i < ARRAY_COUNT(cams); i++) {
        void *cam = ARRAY_AT(cams, i);
        char name[16];
        if (!cam) continue;
        int k = 0;
        while (k < nui_cams && ui_cams[k] != cam) k++;
        if (!hide) {
            if (k < nui_cams) set_enabled(cam, 1, NULL);
            continue;
        }
        if (!get_enabled(cam, NULL)) continue;
        str_ascii(get_name(get_game_object(cam, NULL), NULL), name, sizeof name);
        if (strcmp(name, "UICamera") || (k == nui_cams && nui_cams == MAX_UI_CAMS)) continue;
        if (k == nui_cams) ui_cams[nui_cams++] = cam;
        set_enabled(cam, 0, NULL);
    }
    if (!hide) {
        nui_cams = 0;
        // all groups, inactive ones too: a panel closed meanwhile must not reopen invisible
        void *groups = find_all(NULL, group_type, NULL);
        for (int i = 0; i < ARRAY_COUNT(groups); i++) {
            void *group = ARRAY_AT(groups, i);
            for (int k = 0; group && k < g_nui_groups; k++)
                if (g_ui_groups[k].group == group) set_alpha(group, g_ui_groups[k].alpha, NULL);
        }
        g_nui_groups = 0;
        return;
    }
    void *canvases = find_objects(NULL, canvas_type, NULL);
    for (int i = 0; i < ARRAY_COUNT(canvases); i++) {
        void *canvas = ARRAY_AT(canvases, i);
        if (!canvas || !is_root(canvas, NULL)) continue;
        void *go = get_game_object(canvas, NULL);
        void *group = get_component(go, group_type, NULL);
        int k = 0;
        while (k < g_nui_groups && g_ui_groups[k].group != group) k++;
        if (!group) {
            group = add_component(go, group_type, NULL);
            if (!group) continue;
            k = g_nui_groups;
        }
        float a = get_alpha(group, NULL);
        if (k == g_nui_groups) {
            if (k == MAX_UI_GROUPS) continue;
            g_ui_groups[g_nui_groups++] = (typeof(g_ui_groups[0])){group, a};
        } else if (a > 0) {
            g_ui_groups[k].alpha = a; // the game faded this canvas in meanwhile
        }
        set_alpha(group, 0, NULL);
    }
}

// Runs queued menu requests on the game thread; called from hooks that the game runs every frame.
static void game_tick(void) {
    static double next_ui;
    int hide = g_opt[MOD_HIDE_UI];
    if (hide || g_ui_hidden) {
        struct timespec ts;
        clock_gettime(CLOCK_MONOTONIC, &ts);
        double now = ts.tv_sec + ts.tv_nsec * 1e-9;
        if (hide != g_ui_hidden || now >= next_ui) {
            update_hidden_ui(hide);
            g_ui_hidden = hide && g_opt[MOD_HIDE_UI];
            next_ui = now + HIDE_UI_PERIOD;
        }
    }
    if (!g_action_req[0] || __sync_lock_test_and_set(&g_action_lock, 1)) return;
    char id[sizeof g_action_req];
    memcpy(id, g_action_req, sizeof id);
    g_action_req[0] = 0;
    __sync_lock_release(&g_action_lock);
    run_action(id);
}

// ---- dupe: "Split" works on single items and leaves the source stack whole ----

static const struct { uintptr_t rva; uint32_t orig, mod; } DUPE[] = {
    {RVA_Inventories_CheckSplit_cmp, 0xE3500001, 0xE3500000}, // cmp r0,#1 -> cmp r0,#0
    {RVA_Inventories_Split_left, 0xE1A0100A, 0xE3A01000},     // mov r1,r10 -> mov r1,#0
    {RVA_Inventories_Split_left2, 0xE1A01004, 0xE3A01000},    // mov r1,r4 -> mov r1,#0
};
static int g_dupe_ok;

static void set_dupe(int on) {
    if (!g_dupe_ok) return;
    for (size_t i = 0; i < sizeof DUPE / sizeof DUPE[0]; i++)
        write_code((uint32_t *)(g_base + DUPE[i].rva), on ? &DUPE[i].mod : &DUPE[i].orig, 1);
}

// ---- free shop: real-money packs are granted like a completed purchase, donut prices are skipped ----

static void (*o_PaymentsManager_BuyItem)(void *, void *, void *, void *, void *);

static void h_PaymentsManager_BuyItem(void *pm, void *id, void *complete, void *fail, void *mi) {
    static void (*call_complete)(void *, void *, void *);
    static void (*add_transaction)(void *, void *, void *, int, void *);
    static void (*use_all)(void *, void *);
    static int n;
    void *gm = FIELD(pm, PM_MANAGER, void *);
    void *tm = gm ? FIELD(gm, GM_TRANSACTION_MANAGER, void *) : NULL;
    if (!g_opt[MOD_FREE_SHOP] || !tm || !id) {
        o_PaymentsManager_BuyItem(pm, id, complete, fail, mi);
        return;
    }
    call_complete = FN(RVA_PaymentsManager_CallComplete);
    add_transaction = FN(RVA_TransactionManager_AddTransaction);
    use_all = FN(RVA_TransactionManager_UseAllUnusedTransaction);
    char order[48];
    snprintf(order, sizeof order, "free.%ld.%d", (long)time(NULL), ++n);
    void *s = il2cpp_string_new_(order);
    // Same steps as PaymentsManager.OnRequestComplete after a successful payment.
    FIELD(pm, PM_COMPLETE, void *) = complete;
    FIELD(pm, PM_FAIL, void *) = fail;
    call_complete(pm, s, NULL);
    add_transaction(tm, id, s, (int)time(NULL), NULL);
    use_all(tm, NULL);
    LOG("free purchase %s", order);
}

static int (*o_StaticResourcePrice_Check)(void *, void *, void *, void *);
static void (*o_StaticResourcePrice_Pay)(void *, void *, void *, void *);

static int free_static_price(void *price) {
    Il2CppString *res = FIELD(price, SRP_RESOURCE, Il2CppString *);
    return (g_opt[MOD_FREE_SHOP] && str_is(res, "donut")) || (g_opt[MOD_UNLOCK_RESEARCH] && str_is(res, "research_points"));
}
static int h_StaticResourcePrice_Check(void *price, void *entity, void *args, void *mi) {
    return free_static_price(price) || o_StaticResourcePrice_Check(price, entity, args, mi);
}
static void h_StaticResourcePrice_Pay(void *price, void *entity, void *args, void *mi) {
    if (!free_static_price(price)) o_StaticResourcePrice_Pay(price, entity, args, mi);
}

// ---- free craft: item-stack prices (recipes, building) always pass and take nothing ----

static int (*o_InventoryStacksPrice_Check)(void *, void *, void *, void *);
static void (*o_InventoryStacksPrice_Pay)(void *, void *, void *, void *);

static int h_InventoryStacksPrice_Check(void *price, void *entity, void *args, void *mi) {
    return g_opt[MOD_FREE_CRAFT] || o_InventoryStacksPrice_Check(price, entity, args, mi);
}
static void h_InventoryStacksPrice_Pay(void *price, void *entity, void *args, void *mi) {
    if (!g_opt[MOD_FREE_CRAFT]) o_InventoryStacksPrice_Pay(price, entity, args, mi);
}

// ---- free assembly: collections (generator, vehicles, radio tower...) count as filled, so "Assemble" works ----
// The dialog enables the button from IsBuilded and Complete checks it again; the parts put in so far stay in.

static int (*o_BuildingCollection_get_IsBuilded)(void *, void *);

static int h_BuildingCollection_get_IsBuilded(void *collection, void *mi) {
    return g_opt[MOD_FREE_ASSEMBLY] || o_BuildingCollection_get_IsBuilded(collection, mi);
}

// ---- builder inventory tab: one slot per cell of the character's inventories, but the prefab has 25 ----
// With a big backpack there are more cells: UpdateItems then throws on slot 26, the rest of the backpack is never
// listed and "Build" from the inventory finds no slot for its cell (a chest there can't be placed). The tab gets
// more slots, cloned from its first one; UpdateItems wires each slot to its cell as usual.

static void (*o_InventoryPanelController_UpdateItems)(void *, void *);

static int character_cells(void) {
    static void *(*get_inventories)(void *, void *);
    get_inventories = FN(RVA_CharacterModel_get_Inventories);
    void *ch = player_character(), *invs = ch ? get_inventories(ch, NULL) : NULL;
    if (!invs || strcmp(class_name(invs), "Inventories")) return 0;
    void *parts = FIELD(invs, INVS_PARTS, void *);
    int n = 0;
    for (int i = 0; i < list_size(parts); i++) {
        void *inv = list_get(parts, i);
        if (!inv || strcmp(class_name(inv), "Inventory")) return 0;
        n += list_size(FIELD(inv, INV_CELLS, void *));
    }
    return n;
}

static void grow_inventory_tab(void *panel) {
    static void *(*instantiate)(void *, void *, int, void *);
    static void *(*get_transform)(void *, void *);
    static void *(*get_parent)(void *, void *);
    instantiate = FN(RVA_Object_Instantiate_parent);
    get_transform = FN(RVA_Component_get_transform), get_parent = FN(RVA_Transform_get_parent);
    void *slots = FIELD(panel, IPC_ITEMS, void *);
    int have = list_size(slots), need = character_cells();
    if (!have || need <= have) return;
    void *arr = FIELD(slots, LIST_ITEMS, void *), *first = list_get(slots, 0);
    if (!first) return;
    if (FIELD(arr, ARRAY_LENGTH, int32_t) < need) {
        void *bigger = il2cpp_array_new_(il2cpp_class_get_element_class_(il2cpp_object_get_class_(arr)), need);
        if (!bigger) return;
        memcpy((char *)bigger + ARRAY_DATA, (char *)arr + ARRAY_DATA, have * sizeof(void *));
        FIELD(slots, LIST_ITEMS, void *) = arr = bigger;
    }
    void *parent = get_parent(get_transform(first, NULL), NULL);
    void **data = (void **)((char *)arr + ARRAY_DATA);
    int n = have;
    while (n < need && (data[n] = instantiate(first, parent, 0, NULL))) n++;
    FIELD(slots, LIST_SIZE, int32_t) = n;
    FIELD(slots, LIST_VERSION, int32_t)++;
    LOG("builder inventory tab: %d cells, slots %d -> %d", need, have, n);
}

static void h_InventoryPanelController_UpdateItems(void *panel, void *mi) {
    grow_inventory_tab(panel);
    o_InventoryPanelController_UpdateItems(panel, mi);
}

// ---- free travel: running on the global map costs no energy ----

static int (*o_GetBoostPrice)(void *, void *);
static int (*o_get_BoostEnergyPrice)(void *, void *);

static int h_GetBoostPrice(void *self, void *mi) {
    return g_opt[MOD_FREE_TRAVEL] ? 0 : o_GetBoostPrice(self, mi);
}
static int h_get_BoostEnergyPrice(void *self, void *mi) {
    return g_opt[MOD_FREE_TRAVEL] ? 0 : o_get_BoostEnergyPrice(self, mi);
}

// ...and is instant: a running trip has its road parts moved into the past, so Update sees the arrival.
static void (*o_GlobalMapMovement_Update)(void *, void *);

static void h_GlobalMapMovement_Update(void *m, void *mi) {
    static double (*time_now)(void *, void *);
    void *road = FIELD(m, GMM_ROAD, void *), *player = FIELD(m, GMM_PLAYER, void *);
    int n = list_size(road);
    if (g_opt[MOD_FREE_TRAVEL] && FIELD(m, GMM_IS_MOVING, uint8_t) && player && n > 0) {
        time_now = FN(RVA_Player_get_TimeNow);
        double now = time_now(player, NULL), end = FIELD(list_get(road, n - 1), ROAD_TS_END, double);
        if (end > now) {
            double shift = end - now + 0.05;
            for (int i = 0; i < n; i++) {
                void *part = list_get(road, i);
                FIELD(part, ROAD_TS_START, double) -= shift;
                FIELD(part, ROAD_TS_END, double) -= shift;
            }
            FIELD(m, GMM_START_TS, double) -= shift;
        }
    }
    o_GlobalMapMovement_Update(m, mi);
}

// ---- unlock: every global map location gets the "true" requirement for open/walk/run ----

#define MAX_LOCS 256
static struct { void *loc, *orig[3]; } g_locs[MAX_LOCS];
static int g_nlocs;
static void *g_true_req;
static volatile int g_locs_lock;
static void (*o_GlobalMapLocationDescription_ctor)(void *, void *, void *, void *);

static void apply_unlock(int i) {
    void **f = &FIELD(g_locs[i].loc, LOC_REQUIREMENTS, void *);
    for (int k = 0; k < 3; k++) f[k] = g_opt[MOD_UNLOCK] && g_true_req ? g_true_req : g_locs[i].orig[k];
}

static void apply_unlock_all(void) {
    while (__sync_lock_test_and_set(&g_locs_lock, 1)) {}
    for (int i = 0; i < g_nlocs; i++) apply_unlock(i);
    __sync_lock_release(&g_locs_lock);
    LOG("unlock %d applied to %d locations (true requirement %p)", g_opt[MOD_UNLOCK], g_nlocs, g_true_req);
}

static void h_GlobalMapLocationDescription_ctor(void *loc, void *id, void *node, void *mi) {
    o_GlobalMapLocationDescription_ctor(loc, id, node, mi);
    while (__sync_lock_test_and_set(&g_locs_lock, 1)) {}
    if (g_nlocs < MAX_LOCS) {
        int i = g_nlocs++, found = 0;
        void **f = &FIELD(loc, LOC_REQUIREMENTS, void *);
        g_locs[i].loc = loc;
        il2cpp_gchandle_new_(loc, 0);
        for (int k = 0; k < 3; k++) {
            g_locs[i].orig[k] = f[k];
            if (f[k]) il2cpp_gchandle_new_(f[k], 0); // keeps the originals alive while swapped out
        }
        if (!g_true_req && f[0] && !strcmp(class_name(f[0]), "TrueRequirement")) {
            g_true_req = f[0], found = 1;
            LOG("true requirement from location %d", i);
        }
        if (found)
            for (int j = 0; j < g_nlocs; j++) apply_unlock(j);
        else
            apply_unlock(i);
    }
    __sync_lock_release(&g_locs_lock);
}

// ---- events: freeze (time left stays constant) and forced spawn of any global map event ----
// Every event id has one model that the map updates each frame, active or not; both features work from that update.

#define MAX_EVENTS 64
static struct { void *ev; double frozen_left; } g_events[MAX_EVENTS];
static char g_spawn_req[64]; // event id to spawn, taken by that event's next update (game thread)
static volatile int g_spawn_lock;
static void (*o_GlobalMapEvent_Update)(void *, void *, void *);

// The horde is left alone.
static int is_skipped_event(void *ev) {
    return str_is(FIELD(ev, EV_NAME, Il2CppString *), "horde");
}

static int str_eq(Il2CppString *a, Il2CppString *b) {
    return a && b && a->length == b->length && !memcmp(a->chars, b->chars, a->length * 2);
}

static void *find_location(Il2CppString *id) {
    for (int i = 0; i < g_nlocs; i++)
        if (str_eq(FIELD(g_locs[i].loc, DESC_ID, Il2CppString *), id)) return g_locs[i].loc;
    return NULL;
}

// Same as the end of GlobalMapMovement.SpawnEventBehaviour, with our pick of event and location.
static void spawn_event(void *ev, void *player) {
    static void (*set)(void *, void *, void *, double, int, void *);
    static void *(*get_movement)(void *, void *);
    static void (*call_spawned)(void *, void *, void *, void *);
    set = FN(RVA_GlobalMapEvent_Set), get_movement = FN(RVA_Player_get_GlobalMapMovement);
    call_spawned = FN(RVA_GlobalMapMovement_CallEventSpawned);
    char name[64];
    str_ascii(FIELD(ev, EV_NAME, Il2CppString *), name, sizeof name);
    void *desc = FIELD(ev, EV_DESCRIPTION, void *), *locs = desc ? FIELD(desc, EVD_LOCATIONS, void *) : NULL;
    int n = list_size(locs);
    void *movement = get_movement(player, NULL);
    if (!n || !movement) {
        LOG("spawn %s: no locations (%d) or movement %p", name, n, movement);
        return;
    }
    void *loc = NULL;
    for (int tries = 0, k = (int)(time(NULL) % n); tries < n && !loc; tries++, k = (k + 1) % n)
        loc = find_location(list_get(locs, k));
    if (!loc) {
        LOG("spawn %s: location not loaded", name);
        return;
    }
    set(ev, player, loc, SPAWNED_EVENT_TIME, FIELD(desc, EVD_LEVEL, int32_t), NULL);
    call_spawned(movement, desc, ev, NULL);
    LOG("spawned %s", name);
}

static void h_GlobalMapEvent_Update(void *ev, void *player, void *mi) {
    static double (*ts_now)(void *, void *);
    static void (*set_ts)(void *, double, void *);
    if (!ts_now) ts_now = FN(RVA_GlobalMapEvent_get_TsNow), set_ts = FN(RVA_GlobalMapEvent_SetTs);
    game_tick();
    int i, free_slot = -1;
    for (i = 0; i < MAX_EVENTS && g_events[i].ev != ev; i++)
        if (!g_events[i].ev && free_slot < 0) free_slot = i;
    if (i == MAX_EVENTS && free_slot >= 0) i = free_slot, g_events[i].ev = ev, g_events[i].frozen_left = 0;
    if (g_spawn_req[0] && !__sync_lock_test_and_set(&g_spawn_lock, 1)) {
        if (str_is(FIELD(ev, EV_NAME, Il2CppString *), g_spawn_req) && player) {
            g_spawn_req[0] = 0;
            spawn_event(ev, player);
            if (i < MAX_EVENTS) g_events[i].frozen_left = 0;
        }
        __sync_lock_release(&g_spawn_lock);
    }
    if (i < MAX_EVENTS) {
        double now = ts_now(ev, NULL), end = FIELD(ev, EV_TS, double), *left = &g_events[i].frozen_left;
        // SetTs takes the time left (end = TsNow + arg). Older builds passed the end itself, pushing events ~56 years
        // out (saved, and the map's timer then throws): give such events the spawn duration back.
        if (now > MIN_SANE_TS && end - now > MAX_EVENT_LEFT) {
            LOG("event end %.0f s ahead, reset", end - now);
            set_ts(ev, SPAWNED_EVENT_TIME, NULL);
            end = FIELD(ev, EV_TS, double);
            *left = 0;
        }
        if (!g_opt[MOD_FREEZE_EVENTS] || is_skipped_event(ev) || end <= now - 1 || now < MIN_SANE_TS) {
            *left = 0;
        } else if (*left <= 0 || end > now + *left + 1) {
            *left = end - now; // frozen from now on (or the event was restarted longer)
        } else if (end < now + *left - 1) {
            set_ts(ev, *left, NULL);
        }
    }
    o_GlobalMapEvent_Update(ev, player, mi);
}

// TimeSpan.FromSeconds throws on huge values, and the throw aborts the global map load (endless loading screen).
static void (*o_SetFormatedTime)(void *, double, void *);
static void h_SetFormatedTime(void *container, double time, void *mi) {
    if (!(time > -1e9 && time < 1e9)) {
        static int logged;
        if (!logged++) LOG("event point time %g clamped", time);
        time = 0;
    }
    o_SetFormatedTime(container, time, mi);
}

// Siege and counter siege load another player's base from the raid server (PvpLocationLoader). Offline the request
// fails, and GlobalMapController.OnPvpLocationLoadFailed just calls Load again: the global map waits for it forever
// (and the game resumes into the map, so it hangs every start). End such an event instead and let the map finish:
// the loader's failure (CallFailed) reports completion to the controller. (OnPvpLocationLoadFailed itself starts
// with a branch the trampoline can't relocate.)
#define PVP_COMPLETED 0x8 // PvpLocationLoader.Completed (Action<PvpLocationLoader>)
#define PVP_EVENT 0x1C    // PvpLocationLoader._globalMapEvent
#define DELEGATE_TARGET 0x10
static void (*o_PvpLocationLoader_CallFailed)(void *, void *);
static void h_PvpLocationLoader_CallFailed(void *loader, void *mi) {
    static void (*set_ts)(void *, double, void *);
    static void (*completed)(void *, void *, void *);
    set_ts = FN(RVA_GlobalMapEvent_SetTs), completed = FN(RVA_GlobalMapController_OnPvpLocationLoadCompleted);
    void *done = FIELD(loader, PVP_COMPLETED, void *), *controller = done ? FIELD(done, DELEGATE_TARGET, void *) : NULL;
    if (!controller || strcmp(class_name(controller), "GlobalMapController")) {
        o_PvpLocationLoader_CallFailed(loader, mi);
        return;
    }
    void *ev = FIELD(loader, PVP_EVENT, void *);
    if (ev && !strcmp(class_name(ev), "GlobalMapEvent")) {
        for (int i = 0; i < MAX_EVENTS; i++)
            if (g_events[i].ev == ev) g_events[i].frozen_left = 0;
        set_ts(ev, -2, NULL); // already over: its next update completes it
    }
    LOG("pvp location unavailable offline, event %p ended", ev);
    completed(controller, loader, NULL);
}

// ---- save guard: a scene load that never finishes (the game resumes into it, so it hangs every start) ----
// Before each scene switch the save files are copied to <save dir>/cubemod_backup/bak and a "loading" marker is
// written; the shown scene removes it. A marker found at the next start means that load died: the copy is put
// back. If the start after that dies too, the mod options are switched off for the session (safe mode).

enum { NOTICE_RESTORED = 1, NOTICE_SAFE_MODE = 2 };
static char g_save_dir[256], g_guard_dir[300];
static jmethodID g_menu_notice;

static void guard_path(char *out, size_t cap, const char *name) {
    snprintf(out, cap, "%s/%s", g_guard_dir, name);
}

static int guard_has(const char *name) {
    char p[400];
    guard_path(p, sizeof p, name);
    return access(p, F_OK) == 0;
}

static void guard_set(const char *name, int on) {
    char p[400];
    guard_path(p, sizeof p, name);
    if (!on) {
        unlink(p);
        return;
    }
    FILE *f = fopen(p, "w");
    if (f) fclose(f);
}

// The game's save set: asn.fdat (+ old_asn.fdat) and the rotating *.sdat files; tmp_* are half-written ones.
static int is_save_file(const char *name) {
    size_t n = strlen(name);
    return strncmp(name, "tmp_", 4) && n > 5 && (!strcmp(name + n - 5, ".sdat") || !strcmp(name + n - 5, ".fdat"));
}

static int copy_file(const char *from, const char *to) {
    char buf[8192];
    size_t n;
    FILE *in = fopen(from, "rb"), *out = in ? fopen(to, "wb") : NULL;
    int ok = in && out;
    while (ok && (n = fread(buf, 1, sizeof buf, in)) > 0) ok = fwrite(buf, 1, n, out) == n;
    if (in) fclose(in);
    if (out && fclose(out)) ok = 0;
    return ok;
}

// Deletes the save files in dir (all files if all), then rmdir when all.
static void clear_saves(const char *dir, int all) {
    char p[600];
    DIR *d = opendir(dir);
    struct dirent *e;
    if (!d) return;
    while ((e = readdir(d)))
        if (e->d_name[0] != '.' && (all || is_save_file(e->d_name))) {
            snprintf(p, sizeof p, "%s/%s", dir, e->d_name);
            unlink(p);
        }
    closedir(d);
    if (all) rmdir(dir);
}

static int copy_saves(const char *from, const char *to) {
    char a[600], b[600];
    int n = 0, ok = 1;
    DIR *d = opendir(from);
    struct dirent *e;
    if (!d) return 0;
    while ((e = readdir(d)))
        if (is_save_file(e->d_name)) {
            snprintf(a, sizeof a, "%s/%s", from, e->d_name);
            snprintf(b, sizeof b, "%s/%s", to, e->d_name);
            ok &= copy_file(a, b);
            n++;
        }
    closedir(d);
    return ok ? n : 0;
}

// Copy into bak.tmp first so a kill halfway leaves the previous copy intact.
static void backup_saves(void) {
    char tmp[400], bak[400];
    guard_path(tmp, sizeof tmp, "bak.tmp");
    guard_path(bak, sizeof bak, "bak");
    clear_saves(tmp, 1);
    mkdir(tmp, 0770);
    int n = copy_saves(g_save_dir, tmp);
    if (!n) {
        clear_saves(tmp, 1);
        LOG("save backup failed");
        return;
    }
    clear_saves(bak, 1);
    rename(tmp, bak);
}

static int restore_saves(void) {
    char bak[400], p[600];
    guard_path(bak, sizeof bak, "bak");
    snprintf(p, sizeof p, "%s/asn.fdat", bak);
    if (access(p, F_OK)) return 0;
    clear_saves(g_save_dir, 0);
    return copy_saves(bak, g_save_dir);
}

static void notify_menu(int code) {
    JNIEnv *env;
    if (!g_menu || !g_menu_notice) return;
    if ((*g_vm)->GetEnv(g_vm, (void **)&env, JNI_VERSION_1_6) != JNI_OK &&
        (*g_vm)->AttachCurrentThread(g_vm, &env, NULL) != JNI_OK)
        return;
    (*env)->CallStaticVoidMethod(env, g_menu, g_menu_notice, code);
    if ((*env)->ExceptionCheck(env)) (*env)->ExceptionClear(env);
}

static void safe_mode(void) {
    for (int id = MOD_GOD; id < MOD_COUNT; id++) g_opt[id] = 0;
    g_opt[MOD_SPEED] = 10;
    set_dupe(0);
    apply_unlock_all();
}

// Reads the save files at start: the place to check the marker, before the game has seen them.
static void (*o_GetDataFiles)(void *, void *);
static void h_GetDataFiles(void *cm, void *mi) {
    str_ascii(FIELD(cm, CM_PATH_SAVE, Il2CppString *), g_save_dir, sizeof g_save_dir);
    char *slash = strrchr(g_save_dir, '/');
    if (slash) {
        *slash = 0;
        snprintf(g_guard_dir, sizeof g_guard_dir, "%s/cubemod_backup", g_save_dir);
        mkdir(g_guard_dir, 0770);
        if (guard_has("loading") && guard_has("restored")) {
            LOG("save guard: load failed again after restore, safe mode");
            safe_mode();
            notify_menu(NOTICE_SAFE_MODE);
        } else if (guard_has("loading")) {
            int n = restore_saves();
            LOG("save guard: last load did not finish, restored %d files", n);
            if (n) guard_set("restored", 1), notify_menu(NOTICE_RESTORED);
            else guard_set("loading", 0);
        }
    } else {
        g_save_dir[0] = g_guard_dir[0] = 0;
    }
    o_GetDataFiles(cm, mi);
}

static void (*o_SwitchLevel)(void *, Il2CppString *, void *, void *);
static void h_SwitchLevel(void *mgr, Il2CppString *id, void *param, void *mi) {
    if (g_guard_dir[0] && !guard_has("loading")) {
        backup_saves();
        guard_set("loading", 1);
    }
    o_SwitchLevel(mgr, id, param, mi);
}

static void (*o_OnShown)(void *, void *, void *);
static void h_OnShown(void *mgr, void *scene, void *mi) {
    if (g_guard_dir[0]) guard_set("loading", 0), guard_set("restored", 0);
    o_OnShown(mgr, scene, mi);
}

// Queues a spawn; returns 1 if that event's model has been seen (the map was opened), else 0.
static int request_spawn(const char *id) {
    int known = 0;
    for (int i = 0; i < MAX_EVENTS; i++)
        if (g_events[i].ev && str_is(FIELD(g_events[i].ev, EV_NAME, Il2CppString *), id)) known = 1;
    while (__sync_lock_test_and_set(&g_spawn_lock, 1)) {}
    snprintf(g_spawn_req, sizeof g_spawn_req, "%s", id);
    __sync_lock_release(&g_spawn_lock);
    return known;
}

// ---- ads: rewarded ads grant their reward without showing anything ----

static void (*o_ShowRewardedAd)(void *, void *, void *, void *, void *);
static int (*o_Advertisement_get_isInitialized)(void *);
static int (*o_Advertisement_get_isSupported)(void *);
static int (*o_Advertisement_IsReady)(void *, void *);

static void h_ShowRewardedAd(void *am, void *action, void *placement, void *fail_action, void *mi) {
    static void (*handle_result)(void *, int, void *);
    if (!g_opt[MOD_NO_ADS]) {
        o_ShowRewardedAd(am, action, placement, fail_action, mi);
        return;
    }
    handle_result = FN(RVA_AdsManager_HandleShowResult);
    FIELD(am, ADS_ACTION, void *) = action;
    FIELD(am, ADS_FAIL_ACTION, void *) = fail_action;
    handle_result(am, SHOW_RESULT_FINISHED, NULL);
}
static int h_Advertisement_get_isInitialized(void *mi) {
    return g_opt[MOD_NO_ADS] || o_Advertisement_get_isInitialized(mi);
}
static int h_Advertisement_get_isSupported(void *mi) {
    return g_opt[MOD_NO_ADS] || o_Advertisement_get_isSupported(mi);
}
static int h_Advertisement_IsReady(void *placement, void *mi) {
    return g_opt[MOD_NO_ADS] || o_Advertisement_IsReady(placement, mi);
}

// ---- Google Play Games: never sign in ----
// The APK is re-signed, so Play Services answer DEVELOPER_ERROR and the GPG SDK throws
// IllegalStateException on the main thread (seen on a Galaxy Tab S5e). Every Authenticate
// overload ends here. The callback is dropped: answering "false" from inside SocialServices.Init
// makes GpgsSocialService ask for a sign-in with a native alert and then warn about it, and
// nothing in the game waits for the answer.

static void h_PlayGames_Authenticate(void *platform, void *callback, int silent, void *mi) {
    (void)platform, (void)callback, (void)silent, (void)mi;
    LOG("Play Games sign-in skipped");
}

// ---- setup ----

void mods_install(uintptr_t base, void *(*sym)(const char *)) {
    g_base = base;
    il2cpp_domain_get_ = sym("il2cpp_domain_get");
    il2cpp_domain_get_assemblies_ = sym("il2cpp_domain_get_assemblies");
    il2cpp_assembly_get_image_ = sym("il2cpp_assembly_get_image");
    il2cpp_image_get_name_ = sym("il2cpp_image_get_name");
    il2cpp_class_from_name_ = sym("il2cpp_class_from_name");
    il2cpp_class_get_field_from_name_ = sym("il2cpp_class_get_field_from_name");
    il2cpp_field_static_get_value_ = sym("il2cpp_field_static_get_value");
    il2cpp_object_get_class_ = sym("il2cpp_object_get_class");
    il2cpp_class_get_name_ = sym("il2cpp_class_get_name");
    il2cpp_gchandle_new_ = sym("il2cpp_gchandle_new");
    il2cpp_string_new_ = sym("il2cpp_string_new");
    il2cpp_object_new_ = sym("il2cpp_object_new");
    il2cpp_array_new_ = sym("il2cpp_array_new");
    il2cpp_class_get_element_class_ = sym("il2cpp_class_get_element_class");
    il2cpp_class_get_type_ = sym("il2cpp_class_get_type");
    il2cpp_type_get_object_ = sym("il2cpp_type_get_object");
    g_tramp = mmap(NULL, 4096, PROT_READ | PROT_WRITE | PROT_EXEC, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (g_tramp == MAP_FAILED) { LOG("no trampoline memory"); return; }

    g_dupe_ok = 1;
    for (size_t i = 0; i < sizeof DUPE / sizeof DUPE[0]; i++)
        if (*(uint32_t *)(g_base + DUPE[i].rva) != DUPE[i].orig) g_dupe_ok = 0;
    if (!g_dupe_ok) LOG("split code differs, dupe disabled");

#define H(name, rva) o_##name = hook(rva, h_##name)
    hook(RVA_SettingsDialog_OnSupportButtonClick, h_OnSupportButtonClick);
    H(MoveAction_GetSpeed, RVA_MoveAction_GetSpeed);
    H(MovePathAction_GetSpeed, RVA_MovePathAction_GetSpeed);
    H(HealthController_Attach, RVA_HealthController_Attach);
    H(LimitedResource_set_Amount, RVA_LimitedResource_set_Amount);
    H(ConsumableResource_get_Amount, RVA_ConsumableResource_get_Amount);
    H(ConsumableResource_Update, RVA_ConsumableResource_Update);
    H(SimpleMove, RVA_CharacterController_SimpleMove);
    H(CalculateDamage, RVA_WeaponAttackAction_CalculateDamage);
    H(WeaponAttackAction_OnInit, RVA_WeaponAttackAction_OnInit);
    H(ChangeDurability, RVA_DurabilityInventoryStack_ChangeDurability);
    H(MoveProgress, RVA_Workbench_MoveProgress);
    H(UnlockLootObjectAction_OnUpdate, RVA_UnlockLootObjectAction_OnUpdate);
    H(CheckCode, RVA_CodeLocation_CheckCode);
    H(BunkerComputer_CheckUse, RVA_BunkerComputerController_CheckUse);
    H(Research_Check, RVA_Research_Check);
    H(ResearchRequirement_Check, RVA_ResearchRequirement_Check);
    H(LevelRequirement_Check, RVA_LevelRequirement_Check);
    H(ActionDescription_ctor, RVA_ActionDescription_ctor);
    H(GlobalMapMovement_Update, RVA_GlobalMapMovement_Update);
    H(PaymentsManager_BuyItem, RVA_PaymentsManager_BuyItem);
    H(StaticResourcePrice_Check, RVA_StaticResourcePrice_Check);
    H(StaticResourcePrice_Pay, RVA_StaticResourcePrice_Pay);
    H(InventoryStacksPrice_Check, RVA_InventoryStacksPrice_Check);
    H(InventoryStacksPrice_Pay, RVA_InventoryStacksPrice_Pay);
    H(GetBoostPrice, RVA_GlobalMapMovement_GetBoostPrice);
    H(get_BoostEnergyPrice, RVA_GlobalMapMovement_get_BoostEnergyPrice);
    H(GlobalMapLocationDescription_ctor, RVA_GlobalMapLocationDescription_ctor);
    H(GlobalMapEvent_Update, RVA_GlobalMapEvent_Update);
    H(SetFormatedTime, RVA_GlobalMapEventPointContainer_SetFormatedTime);
    H(PvpLocationLoader_CallFailed, RVA_PvpLocationLoader_CallFailed);
    H(SwitchLevel, RVA_GameSceneManager_SwitchLevel);
    H(OnShown, RVA_GameSceneManager_OnShown);
    H(GetDataFiles, RVA_CryptoManager_GetDataFiles);
    H(ShowRewardedAd, RVA_AdsManager_ShowRewardedAd);
    H(Advertisement_get_isInitialized, RVA_Advertisement_get_isInitialized);
    H(Advertisement_get_isSupported, RVA_Advertisement_get_isSupported);
    H(Advertisement_IsReady, RVA_Advertisement_IsReady);
    hook(RVA_PlayGamesPlatform_Authenticate, h_PlayGames_Authenticate);
    H(BuildingCollection_get_IsBuilded, RVA_BuildingCollection_get_IsBuilded);
    if (il2cpp_array_new_ && il2cpp_class_get_element_class_)
        H(InventoryPanelController_UpdateItems, RVA_InventoryPanelController_UpdateItems);
#undef H
    LOG("mod hooks installed (%d trampolines)", g_ntramp);
}

static void JNICALL n_set(JNIEnv *env, jclass cls, jint id, jint value) {
    (void)env, (void)cls;
    if (id < 0 || id >= MOD_COUNT) return;
    g_opt[id] = value;
    if (id == MOD_DUPE) set_dupe(value);
    if (id == MOD_UNLOCK) apply_unlock_all();
    LOG("option %d = %d", id, value);
}

static jint JNICALL n_spawn(JNIEnv *env, jclass cls, jstring id) {
    (void)cls;
    const char *s = (*env)->GetStringUTFChars(env, id, NULL);
    if (!s) return 0;
    int r = request_spawn(s);
    (*env)->ReleaseStringUTFChars(env, id, s);
    return r;
}

// Queues action "cubemod_give_<item>"; returns 0 if the patched references didn't load it.
static jint JNICALL n_give(JNIEnv *env, jclass cls, jstring item) {
    (void)cls;
    const char *s = (*env)->GetStringUTFChars(env, item, NULL);
    if (!s) return 0;
    while (__sync_lock_test_and_set(&g_action_lock, 1)) {}
    snprintf(g_action_req, sizeof g_action_req, "cubemod_give_%s", s);
    __sync_lock_release(&g_action_lock);
    (*env)->ReleaseStringUTFChars(env, item, s);
    return g_nactions;
}

// Menu button: the next start puts back the copy made before the last scene switch. Returns 0 without a copy.
static jint JNICALL n_restore_next(JNIEnv *env, jclass cls) {
    (void)env, (void)cls;
    if (!g_guard_dir[0] || !guard_has("bak/asn.fdat")) return 0;
    guard_set("restored", 0);
    guard_set("loading", 1);
    LOG("save guard: restore requested");
    return 1;
}

void mods_jni(JavaVM *vm) {
    JNIEnv *env;
    g_vm = vm;
    if ((*vm)->GetEnv(vm, (void **)&env, JNI_VERSION_1_6) != JNI_OK) return;
    jclass c = (*env)->FindClass(env, "cube/mod/ModMenu");
    if (!c) {
        (*env)->ExceptionClear(env);
        LOG("ModMenu class not found");
        return;
    }
    static const JNINativeMethod M[] = {
        {"nativeSet", "(II)V", (void *)n_set},
        {"nativeSpawn", "(Ljava/lang/String;)I", (void *)n_spawn},
        {"nativeGive", "(Ljava/lang/String;)I", (void *)n_give},
        {"nativeRestoreNext", "()I", (void *)n_restore_next},
    };
    if ((*env)->RegisterNatives(env, c, M, sizeof M / sizeof M[0]) != 0) {
        (*env)->ExceptionClear(env);
        LOG("RegisterNatives failed");
        return;
    }
    g_menu_open = (*env)->GetStaticMethodID(env, c, "open", "(Z)V");
    g_menu_notice = (*env)->GetStaticMethodID(env, c, "notice", "(I)V");
    g_menu = (*env)->NewGlobalRef(env, c);
}
