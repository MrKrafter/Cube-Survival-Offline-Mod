# Cube Survival Offline Mod

Офлайн-патч и мод-меню для Cube Survival: LDoE 1.0.4 (Android). Серверы игры давно выключены, и оригинал с тех пор не запускается. С этим патчем игра работает совсем без интернета.

English version below.

Новости и готовые сборки: https://t.me/cubesurvival

## Русский

### Что внутри
- офлайн-сервер внутри игры: библиотека `libcubefix.so` отвечает игре вместо серверов разработчика;
- мод-меню: бог, ноуклип, бесплатный крафт и магазин, выдача любых предметов, открытие всех локаций, ивенты на карте и другое;
- исправления багов самой игры: СВД и револьвер, тактический рюкзак, бесконечные загрузки карты из-за осад и сломанных ивентов;
- совместимость с новыми версиями Android.

В репозитории нет файлов игры. APK, OBB и игровые данные берутся из вашей собственной копии игры.

### Нужно 32-битное устройство
Игра существует только в 32-битной ARM-версии (armeabi-v7a). Она запускается на старых телефонах и планшетах примерно до 2022-2023 года (Android 4.1+) и на эмуляторах с поддержкой ARM-приложений: BlueStacks, LDPlayer, MuMu, эмулятор Android Studio. На устройствах только с 64-битной частью (Pixel 7 и новее, Galaxy S24) игра не запустится.

### Зачем игре был нужен интернет
Оригинал без сети не запускался вообще. Через сервер разработчика шли:
- конфиг игры и точное время;
- аккаунт и облачные сохранения;
- данные игры (предметы, рецепты, локации), которые можно было менять без обновления;
- покупки и их проверка;
- осады: сервер подбирал базу другого игрока;
- праздничные ивенты и статистика.

Выбор сервера при входе («Сервер 1-6» с цветными пометками загруженности) был бутафорским. Список вместе с «загруженностью» лежит прямо в файлах игры, а выбранное название только записывается в профиль. Все игроки ходили на один и тот же сервер.

### Как устроен офлайн
`libcubefix.so` загружается при старте игры и перехватывает в il2cpp-коде классы, через которые игра ходит в сеть. На каждый запрос игра получает ответ от встроенного «сервера»: конфиг, время, офлайн-аккаунт, данные игры (они зашиты в библиотеку) и «ок» на каждое сохранение. Сохранения поэтому только локальные. Вход в Google Play Игры пропускается, потому что у переподписанной игры он падает.

### Мод-меню
Открывается тремя быстрыми нажатиями в левом верхнем углу экрана или через «Настройки → Поддержка». Язык меню совпадает с языком игры (русский или английский). Переключатели запоминаются между запусками.

Что есть:
- персонаж: скорость x1-x5, режим бога, ноуклип, убийство с одного удара, мгновенная атака, вечная прочность;
- крафт и база: крафт и стройка без ресурсов, сборка генератора и машин без деталей, мгновенные станки, все рецепты открыты, дюп через «Разделить», мгновенные сундуки, «Получить любой предмет…» со всеми 355 предметами и поиском;
- магазин: всё бесплатно, награды за рекламу без рекламы;
- карта: мгновенные переходы, все локации открыты, бункер «Альфа» без кулдауна, заморозка ивентов (орду не трогает), создание ивентов на карте, вырезанные предметы и праздничные ивенты;
- сохранения: откат сейва и перезапуск; перед каждой загрузкой локации мод сам делает копию сейва и при зависании откатывает его.

Что работает с оговорками:
- осаду и контросаду создать нельзя, им нужна база другого игрока с сервера;
- нефтебаза, вторая вышка и бункер «Чарли» открываются, но внутри обычный лес: разработчики не успели сделать для них карты;
- после двух зависаний подряд мод выключает все опции меню, их нужно включить заново.

### Сборка своими руками
Понадобится своя копия Cube Survival 1.0.4 (пакет `cube.survival.adventure`, versionCode 26): APK и OBB `main.26.cube.survival.adventure.obb`.

Инструменты (сборка проверялась на Windows 11):
- Python 3.12+ и `pip install UnityPy`;
- JDK 17 или новее;
- Android SDK: build-tools (zipalign, apksigner, d8) и `android.jar` платформы 35;
- Android NDK r27 (clang для armeabi-v7a);
- apktool 2.12.

Пути к инструментам задаются переменными окружения (PowerShell):

```powershell
$env:CUBE_JDK = 'C:\path\to\jdk-21'                                   # домашняя папка JDK
$env:CUBE_BUILD_TOOLS = 'C:\path\to\Android\Sdk\build-tools\35.0.0'   # zipalign, apksigner, d8
$env:CUBE_ANDROID_JAR = 'C:\path\to\Android\Sdk\platforms\android-35\android.jar'
$env:CUBE_NDK_BIN = 'C:\path\to\ndk\android-ndk-r27d\toolchains\llvm\prebuilt\windows-x86_64\bin'
$env:CUBE_APKTOOL = 'C:\path\to\apktool.jar'                          # по умолчанию toolchain\apktool.jar
```

Ключ подписи по умолчанию создаётся в `signing/cube.keystore` (`CUBE_KEYSTORE` меняет путь). Не теряйте его: обновить установленную сборку можно только APK, подписанным тем же ключом.

1. Распакуйте APK (это zip) в `in/apk`, а OBB (тоже zip) в `in/obb`.
2. Декомпилируйте APK: `java -jar apktool.jar d CubeSurvival_1.0.4.apk -o apktool_cube`.
3. Примените патч `patches/smali.diff` к `apktool_cube/smali`. Он меняет пять классов:
   - `ru/kv3dunityext/permissions/MainActivity`: загружает `libcubefix` и подключает мод-меню;
   - `ru/kv3dunityext/permissions/UnityInterface`: разрешение на память всегда «выдано» (на новых Android запрос ломается);
   - `bitter/jnibridge/JNIBridge$a`: не падает на default-методах Java-интерфейсов (Android 14+);
   - `com/unity/purchasing/googleplay/BillingServiceManager`: сразу отвечает «нет сервиса покупок»;
   - `com/unity3d/player/UnityPlayer`: слежение за звонками обёрнуто в try/catch (SecurityException на новых Android).
4. Достаньте из данных игры TextAsset `r14` (данные предметов, рецептов и локаций) в `textassets/r14.bytes`: `python -I scripts/extract_r14.py` (нужен `pip install UnityPy`).
5. Соберите мод-меню: `modmenu/build.ps1`. Скрипт компилирует Java и кладёт smali в `apktool_cube/smali/cube/mod`.
6. Запустите `python scripts/patch_smali_compat.py`. Он заменяет вызовы `TelephonyManager.getNetworkType` (на новых Android им нужно разрешение) в трёх классах рекламы и аналитики.
7. Запустите `python scripts/build_apk.py`. Скрипт:
   - готовит данные игры (`patch_refs.py`);
   - собирает `libcubefix.so`;
   - пересобирает APK через apktool;
   - патчит `libunity.so` (`patch_unity.py`);
   - кладёт содержимое OBB внутрь APK;
   - выравнивает и подписывает APK.

   Готовый файл: `out/CubeSurvival_offline_1.0.4.apk`. Ключ подписи создаётся при первой сборке.

   С ключом `--rec` получится копия под другим именем пакета (`cube.survival.adventure.rec`, в лаунчере «Cube Survival REC»): она ставится рядом с основной игрой и хранит свой сейв, удобно для записи видео с нуля. Только в этой копии в мод-меню есть пункт «Скрыть интерфейс»: пропадают кнопки, полоска здоровья и миникарта, управление работает вслепую, после перезапуска интерфейс возвращается. Файл: `out/CubeSurvival_offline_1.0.4_rec.apk`.

### Что где лежит
- `cubefix/cubefix.c`: офлайн-сервер, перехват сетевых запросов;
- `cubefix/mods.c`: хуки мод-меню, исправления багов, страховка сейвов;
- `cubefix/refs.S`: вшивает данные игры в библиотеку;
- `modmenu/`: интерфейс мод-меню на Java;
- `scripts/`: сборка (`build_apk.py`, `patch_refs.py`, `extract_r14.py` и остальное нужное для неё);
- `tools/`: вспомогательные скрипты для разбора игры (Ghidra, il2cpp, тесты на эмуляторе). Пути в них указаны под раскладку автора, поправьте под себя;
- `patches/`: патчи к smali.

### Нашли проблему?
Пишите в Telegram: @MrKrafter. Укажите модель устройства, версию Android и что делали перед ошибкой. Скриншот или запись экрана тоже очень помогут.

### Кто делал
- MrKrafter: автор проекта, тестирование, видео.
- Claude (ИИ-ассистент Anthropic): разбор игры, офлайн-патч, мод-меню.

Это фанатский проект. Права на игру принадлежат её разработчикам, здесь лежит только код мода.

## English

### What's inside
- an offline server inside the game: `libcubefix.so` answers in place of the developer's servers;
- a mod menu: god mode, noclip, free crafting and shop, any item, every location unlocked, map events and more;
- fixes for bugs in the game itself: the SVD and revolver, the tactical backpack, endless map loading caused by sieges and broken events;
- compatibility fixes for newer Android versions.

The repository contains no game files. The APK, OBB and game data come from your own copy of the game.

### You need a 32-bit device
The game only exists as 32-bit ARM (armeabi-v7a). It runs on older phones and tablets from before about 2022-2023 (Android 4.1+) and on emulators that can run ARM apps: BlueStacks, LDPlayer, MuMu, the Android Studio emulator. Devices that dropped 32-bit support (Pixel 7 and later, Galaxy S24) can't run it.

### Why the game needed the internet
The original wouldn't start at all without a connection. The developer's server handled:
- the game config and the exact time;
- your account and cloud saves;
- the game data (items, recipes, locations), which could change without an update;
- purchases and their validation;
- sieges: the server picked another player's base for you;
- holiday events and analytics.

The server choice at login ("Server 1-6" with colored load labels) was just for show. The list, "load" included, sits right in the game files, and the name you pick only goes into your profile. Everyone played on the same server.

### How the offline part works
`libcubefix.so` loads when the game starts and hooks the il2cpp classes the game uses for networking. Every request gets an answer from the built-in "server": the config, the time, an offline account, the game data (packed into the library) and "ok" for every save. Saves are therefore local only. Google Play Games sign-in is skipped, since it crashes in a re-signed game.

### Mod menu
Open it with three quick taps in the top-left corner of the screen, or from Settings → Support. It follows the game's language (Russian or English). Toggles are remembered between launches.

What it has:
- character: speed x1-x5, god mode, noclip, one-hit kills, instant attack, items never wear out;
- craft and base: crafting and building without resources, generator and vehicles without parts, instant workbenches, every recipe unlocked, duplication via Split, instant chests, "Get any item…" with all 355 items and search;
- shop: everything free, ad rewards without ads;
- map: instant travel, every location unlocked, Bunker Alfa without cooldown, frozen events (the horde is left alone), spawning map events, cut items and holiday events;
- saves: roll back and restart; the mod also copies your save before every location load and restores it if the load hangs.

What works with caveats:
- siege and counter siege can't be spawned, since they need another player's base from the server;
- the oil plant, the second tower and Bunker Charlie open, but they're a plain forest inside: the developers never made their maps;
- after two hangs in a row the mod turns every menu option off, so switch them back on.

### Building it yourself
You need your own copy of Cube Survival 1.0.4 (package `cube.survival.adventure`, versionCode 26): the APK and the OBB `main.26.cube.survival.adventure.obb`.

Tools (the build was tested on Windows 11):
- Python 3.12+ with `pip install UnityPy`;
- JDK 17 or newer;
- Android SDK: build-tools (zipalign, apksigner, d8) and the platform 35 `android.jar`;
- Android NDK r27 (clang for armeabi-v7a);
- apktool 2.12.

Tool paths are passed through environment variables (PowerShell):

```powershell
$env:CUBE_JDK = 'C:\path\to\jdk-21'                                   # JDK home
$env:CUBE_BUILD_TOOLS = 'C:\path\to\Android\Sdk\build-tools\35.0.0'   # zipalign, apksigner, d8
$env:CUBE_ANDROID_JAR = 'C:\path\to\Android\Sdk\platforms\android-35\android.jar'
$env:CUBE_NDK_BIN = 'C:\path\to\ndk\android-ndk-r27d\toolchains\llvm\prebuilt\windows-x86_64\bin'
$env:CUBE_APKTOOL = 'C:\path\to\apktool.jar'                          # default: toolchain\apktool.jar
```

The signing key is created in `signing/cube.keystore` by default (`CUBE_KEYSTORE` overrides the path). Keep it: an installed build can only be updated with an APK signed by the same key.

1. Unzip the APK into `in/apk` and the OBB (also a zip) into `in/obb`.
2. Decode the APK: `java -jar apktool.jar d CubeSurvival_1.0.4.apk -o apktool_cube`.
3. Apply `patches/smali.diff` to `apktool_cube/smali`. It changes five classes:
   - `ru/kv3dunityext/permissions/MainActivity`: loads `libcubefix` and hooks up the mod menu;
   - `ru/kv3dunityext/permissions/UnityInterface`: the storage permission always reads as granted (the request breaks on newer Android);
   - `bitter/jnibridge/JNIBridge$a`: no crash on default methods of Java interfaces (Android 14+);
   - `com/unity/purchasing/googleplay/BillingServiceManager`: answers "no billing service" right away;
   - `com/unity3d/player/UnityPlayer`: the phone call listener is wrapped in try/catch (SecurityException on newer Android).
4. Extract the TextAsset `r14` (item, recipe and location data) from the game data into `textassets/r14.bytes`: `python -I scripts/extract_r14.py` (needs `pip install UnityPy`).
5. Build the mod menu: `modmenu/build.ps1`. It compiles the Java code and puts the smali into `apktool_cube/smali/cube/mod`.
6. Run `python scripts/patch_smali_compat.py`. It replaces `TelephonyManager.getNetworkType` calls (which need a permission on newer Android) in three ad and analytics classes.
7. Run `python scripts/build_apk.py`. The script:
   - prepares the game data (`patch_refs.py`);
   - builds `libcubefix.so`;
   - rebuilds the APK with apktool;
   - patches `libunity.so` (`patch_unity.py`);
   - puts the OBB contents inside the APK;
   - aligns and signs the APK.

   The result is `out/CubeSurvival_offline_1.0.4.apk`. The signing key is created on the first build.

   With `--rec` you get a copy under another package name (`cube.survival.adventure.rec`, "Cube Survival REC" in the launcher). It installs next to the main game and keeps its own save, which is handy for recording videos from scratch. Only this copy has "Hide the interface" in the mod menu: the buttons, health bar and minimap disappear, the controls still work blind, and the interface comes back after a restart. The file is `out/CubeSurvival_offline_1.0.4_rec.apk`.

### Where things are
- `cubefix/cubefix.c`: the offline server and the network hooks;
- `cubefix/mods.c`: mod menu hooks, game bug fixes, the save guard;
- `cubefix/refs.S`: embeds the game data into the library;
- `modmenu/`: the mod menu UI in Java;
- `scripts/`: the build (`build_apk.py`, `patch_refs.py`, `extract_r14.py` and the rest it needs);
- `tools/`: helper scripts for taking the game apart (Ghidra, il2cpp, emulator tests). Their paths follow the author's layout; edit them for yours;
- `patches/`: smali patches.

### Found a problem?
Message @MrKrafter on Telegram. Mention your device model, Android version and what you did before the problem. A screenshot or a screen recording helps a lot.

### Credits
- MrKrafter: project author, testing, videos.
- Claude (Anthropic's AI assistant): reverse engineering, the offline patch, the mod menu.

This is a fan project. The game belongs to its developers; this repository only holds the mod's code.
