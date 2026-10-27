# Cube Survival Offline Mod

Cube Survival: LDoE давно не работает: серверы выключили и из Google Play игру убрали в 2020 году. Здесь лежит офлайн-патч, который возвращает её к жизни, так ещё и мод-меню в придачу.

Это мой первый проект публично опубликованный на GitHub, а также первый публичный проект связанный с игрой для Android. Позднее я бы хотел довести игру до ума и внести в неё контента, а также восстановить тот, что уже в игре есть, но работает лишь частично. Новости проекта, а также многое другое можете найти тут: https://t.me/cubesurvival

English version below.

## Русский

### Что внутри
- офлайн-сервер внутри игры: библиотека `libcubefix.so` отвечает игре вместо серверов разработчика;
- мод-меню: бог, ноуклип, бесплатный крафт и магазин, выдача любых предметов, открытие всех локаций, ивенты на карте и другое;
- исправления багов самой игры: СВД и револьвер теперь работоспособны, как и тактический рюкзак с хранилищем. Бесконечные загрузки карты из-за осад и сломанных ивентов починены;
- совместимость с новыми версиями Android.

В репозитории нет файлов игры. APK, OBB и игровые данные берутся из вашей собственной копии игры!

### Как поставить
Проще всего через патчер: он сам делает офлайн-версию из вашей копии игры, ничего собирать не нужно.

1. Скачайте `Cube_Survival_Offline_Mod_patcher_*.zip` в разделе [Releases](https://github.com/MrKrafter/Cube-Survival-Offline-Mod/releases) и распакуйте.
2. Установите [Python](https://www.python.org/downloads/) 3.8 или новее (на Windows отметьте «Add python.exe to PATH»).
3. Положите в папку патчера APK игры 1.0.4 и OBB `main.26.cube.survival.adventure.obb` (подойдут и архивы с ними: .xapk, .zip).
4. Запустите `patch.bat` (на Linux, macOS или в Termux: `python3 cube_patcher.py`).
5. Поставьте получившийся `CubeSurvival_offline_1.0.4.apk` на устройство. OBB отдельно не нужен, он уже внутри.

Патчер проверяет файлы сам. Версия из Google Play, SHA-256:

| Файл | SHA-256 |
|---|---|
| APK `cube.survival.adventure` 1.0.4 (versionCode 26) | `15499be6a2d0eefeb66496b394cdfeb5c5828278fc5c7369e594004d15ecb03b` |
| OBB `main.26.cube.survival.adventure.obb` | `7d46ce31eb8224ac25d32cf2a9540b014f553e1cac60e0efc5d8dbe2775c1578` |

При первом запуске патчер создаёт ключ подписи `cube_patcher_key.json`. Сохраните его: новую версию мода можно поставить поверх старой (не теряя прогресс), только если она подписана тем же ключом. Поверх сборки из Telegram-канала так не встанет, у неё другой ключ.

### Нужно 32-битное устройство
Игра существует только в 32-битной ARM-версии (armeabi-v7a). Она запускается на старых телефонах и планшетах примерно до 2022-2023 года (Android 4.1+) и на эмуляторах с поддержкой ARM-приложений: BlueStacks, LDPlayer, MuMu, эмулятор Android Studio. На устройствах только с 64-битной частью (Pixel 7 и новее, Galaxy S24) игра не запустится.

### Зачем игре был нужен интернет
Оригинал без сети не запускался вообще. Через сервер разработчика шли:
- конфиг игры и точное время;
- аккаунт и облачные сохранения;
- данные игры (предметы, рецепты, локации), которые можно было менять без обновления;
- покупки и их проверка;
- осады: сервер подбирал базу другого игрока;
- статистика.

Выбор сервера при входе («Сервер 1-6» с цветными пометками загруженности) был липовым. Список вместе с «загруженностью» лежит прямо в файлах игры, а выбранное название только записывается в профиль. Все игроки ходили на один и тот же сервер.

### Как устроен офлайн
`libcubefix.so` загружается при старте игры и перехватывает в il2cpp-коде классы, через которые игра ходит в сеть. На каждый запрос игра получает ответ от встроенного «сервера»: конфиг, время, офлайн-аккаунт, данные игры (они зашиты в библиотеку) и «ок» на каждое сохранение. Сохранения поэтому только локальные. Вход в Google Play Игры пропускается, потому что у переподписанной игры он падает.

### Мод-меню
Открывается тремя быстрыми нажатиями в левом верхнем углу экрана или через «Настройки → Поддержка». Язык меню совпадает с языком игры (русский или английский). Переключатели запоминаются между запусками.

Что есть:
- персонаж: скорость x1-x5, режим бога, ноуклип, убийство с одного удара, мгновенная атака, вечная прочность;
- крафт и база: крафт и стройка без ресурсов, сборка генератора и машин без деталей, мгновенные станки, все рецепты открыты, дюп через «Разделить», мгновенные сундуки, «Получить любой предмет…» со всеми 355 предметами и поиском;
- магазин: всё бесплатно, награды за рекламу без рекламы;
- карта: мгновенные переходы, все локации открыты, бункер «Альфа» без кулдауна, заморозка ивентов (орду не трогает), создание ивентов на карте, вырезанные предметы. Праздничных ивентов в Cube Survival не было, от LDoE в файлах остались только их заготовки (китайский и рождественский), и мод-меню умеет их запускать;
- сохранения: откат сейва и перезапуск; перед каждой загрузкой локации мод сам делает копию сейва и при зависании откатывает его.

Что работает с оговорками:
- осаду и контросаду создать нельзя, им нужна база другого игрока с сервера;
- нефтебаза, вторая вышка и бункер «Чарли» открываются, но внутри обычный лес: разработчики не успели сделать для них карты;
- после двух зависаний подряд мод выключает все опции меню, их нужно включить заново.

### Сборка своими руками
Это для тех, кто хочет менять мод. Чтобы просто играть, хватит патчера.

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

Архив патчера собирается после обычной сборки: `cubefix/build.ps1 -Slot` (библиотека без вшитых данных игры), `pip install bsdiff4`, затем `python patcher/make_release.py <версия>`. В архив попадают только наш код, `libcubefix_slot.so` и бинарная разница для `classes.dex`; данные для офлайн-сервера патчер достаёт из OBB игрока.

### Что где лежит
- `cubefix/cubefix.c`: офлайн-сервер, перехват сетевых запросов;
- `cubefix/mods.c`: хуки мод-меню, исправления багов, страховка сейвов;
- `cubefix/refs.S`: вшивает данные игры в библиотеку;
- `cubefix/icon.S`, `cubefix/telegram.png`: иконка кнопки Telegram (рисует `tools/make_tg_icon.py`);
- `modmenu/`: интерфейс мод-меню на Java;
- `patcher/`: патчер для игроков (чистый Python без зависимостей: применение разницы, сборка и подпись APK) и `make_release.py` для сборки его архива;
- `scripts/`: сборка (`build_apk.py`, `patch_refs.py`, `extract_r14.py` и остальное нужное для неё);
- `tools/`: вспомогательные скрипты для разбора игры (Ghidra, il2cpp, тесты на эмуляторе). Пути в них указаны под раскладку автора, поправьте под себя;
- `patches/`: патчи к smali.

### Нашли проблему?
Пишите в Telegram: @MrKrafter. Укажите модель устройства, версию Android и что делали перед ошибкой. Скриншот или запись экрана тоже очень помогут.

### Кто делал
MrKrafter с помощью Claude.

Это фанатский проект. Права на игру принадлежат её разработчикам, здесь лежит только код мода.

## English

Cube Survival: LDoE doesn't work anymore: the servers were shut down and the game was pulled from Google Play in 2020. This is an offline patch that brings it back to life, with a mod menu on top of that.

This is my first project published on GitHub, and also my first public project for an Android game. Later I'd like to polish the game and add content to it, and also restore what is already in the game but only partly works. You can find the project news and much more here: https://t.me/cubesurvival

### What's inside
- an offline server inside the game: `libcubefix.so` answers in place of the developer's servers;
- a mod menu: god mode, noclip, free crafting and shop, any item, every location unlocked, map events and more;
- fixes for bugs in the game itself: the SVD and revolver work now, and so do the tactical backpack and storage. Endless map loading caused by sieges and broken events is fixed;
- compatibility with newer Android versions.

The repository contains no game files. The APK, OBB and game data come from your own copy of the game!

### Installing
The easiest way is the patcher: it makes the offline build from your copy of the game, no building required.

1. Download `Cube_Survival_Offline_Mod_patcher_*.zip` from [Releases](https://github.com/MrKrafter/Cube-Survival-Offline-Mod/releases) and unzip it.
2. Install [Python](https://www.python.org/downloads/) 3.8 or newer (on Windows tick "Add python.exe to PATH").
3. Put the game's 1.0.4 APK and the OBB `main.26.cube.survival.adventure.obb` into the patcher folder (archives with them work too: .xapk, .zip).
4. Run `patch.bat` (on Linux, macOS or in Termux: `python3 cube_patcher.py`).
5. Install the resulting `CubeSurvival_offline_1.0.4.apk` on your device. The OBB isn't needed separately, it's already inside.

The patcher checks the files itself. SHA-256 of the Google Play release:

| File | SHA-256 |
|---|---|
| APK `cube.survival.adventure` 1.0.4 (versionCode 26) | `15499be6a2d0eefeb66496b394cdfeb5c5828278fc5c7369e594004d15ecb03b` |
| OBB `main.26.cube.survival.adventure.obb` | `7d46ce31eb8224ac25d32cf2a9540b014f553e1cac60e0efc5d8dbe2775c1578` |

On the first run the patcher creates a signing key, `cube_patcher_key.json`. Keep it: a new version of the mod installs over the old one (keeping your progress) only if it's signed with the same key. It won't install over the build from the Telegram channel, which has a different key.

### You need a 32-bit device
The game only exists as 32-bit ARM (armeabi-v7a). It runs on older phones and tablets from before about 2022-2023 (Android 4.1+) and on emulators that can run ARM apps: BlueStacks, LDPlayer, MuMu, the Android Studio emulator. Devices that dropped 32-bit support (Pixel 7 and later, Galaxy S24) can't run it.

### Why the game needed the internet
The original wouldn't start at all without a connection. The developer's server handled:
- the game config and the exact time;
- your account and cloud saves;
- the game data (items, recipes, locations), which could change without an update;
- purchases and their validation;
- sieges: the server picked another player's base for you;
- analytics.

The server choice at login ("Server 1-6" with colored load labels) was fake. The list, "load" included, sits right in the game files, and the name you pick only goes into your profile. Everyone played on the same server.

### How the offline part works
`libcubefix.so` loads when the game starts and hooks the il2cpp classes the game uses for networking. Every request gets an answer from the built-in "server": the config, the time, an offline account, the game data (packed into the library) and "ok" for every save. Saves are therefore local only. Google Play Games sign-in is skipped, since it crashes in a re-signed game.

### Mod menu
Open it with three quick taps in the top-left corner of the screen, or from Settings → Support. It follows the game's language (Russian or English). Toggles are remembered between launches.

What it has:
- character: speed x1-x5, god mode, noclip, one-hit kills, instant attack, items never wear out;
- craft and base: crafting and building without resources, generator and vehicles without parts, instant workbenches, every recipe unlocked, duplication via Split, instant chests, "Get any item…" with all 355 items and search;
- shop: everything free, ad rewards without ads;
- map: instant travel, every location unlocked, Bunker Alfa without cooldown, frozen events (the horde is left alone), spawning map events, cut items. Cube Survival never had holiday events; only their leftovers from LDoE remain in the files (the Chinese and the Christmas one), and the mod menu can start them;
- saves: roll back and restart; the mod also copies your save before every location load and restores it if the load hangs.

What works with caveats:
- siege and counter siege can't be spawned, since they need another player's base from the server;
- the oil plant, the second tower and Bunker Charlie open, but they're a plain forest inside: the developers never made their maps;
- after two hangs in a row the mod turns every menu option off, so switch them back on.

### Building it yourself
This is for changing the mod. To just play, the patcher is enough.

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

The patcher zip is made after a normal build: `cubefix/build.ps1 -Slot` (the library without embedded game data), `pip install bsdiff4`, then `python patcher/make_release.py <version>`. The zip only holds our code, `libcubefix_slot.so` and a binary diff for `classes.dex`; the patcher takes the offline server's data from the player's OBB.

### Where things are
- `cubefix/cubefix.c`: the offline server and the network hooks;
- `cubefix/mods.c`: mod menu hooks, game bug fixes, the save guard;
- `cubefix/refs.S`: embeds the game data into the library;
- `cubefix/icon.S`, `cubefix/telegram.png`: the Telegram button icon (drawn by `tools/make_tg_icon.py`);
- `modmenu/`: the mod menu UI in Java;
- `patcher/`: the patcher for players (pure Python, no dependencies: applies the diff, builds and signs the APK) and `make_release.py`, which makes its zip;
- `scripts/`: the build (`build_apk.py`, `patch_refs.py`, `extract_r14.py` and the rest it needs);
- `tools/`: helper scripts for taking the game apart (Ghidra, il2cpp, emulator tests). Their paths follow the author's layout; edit them for yours;
- `patches/`: smali patches.

### Found a problem?
Message @MrKrafter on Telegram. Mention your device model, Android version and what you did before the problem. A screenshot or a screen recording helps a lot.

### Credits
MrKrafter, with help from Claude.

This is a fan project. The game belongs to its developers; this repository only holds the mod's code.
