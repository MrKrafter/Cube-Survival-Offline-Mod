Cube Survival Offline Mod — патчер / patcher
https://github.com/MrKrafter/Cube-Survival-Offline-Mod

=== Русский ===

Патчер делает из вашей копии Cube Survival: LDoE 1.0.4 офлайн-версию с мод-меню.
Файлов игры в нём нет, их берут из вашей копии.

Что нужно:
- Python 3.8 или новее (https://www.python.org/downloads/; при установке на Windows
  отметьте "Add python.exe to PATH");
- APK игры версии 1.0.4 и OBB main.26.cube.survival.adventure.obb. Подойдут и архивы
  с ними (.xapk, .zip).

Контрольные суммы SHA-256 версии из Google Play:
  APK  15499be6a2d0eefeb66496b394cdfeb5c5828278fc5c7369e594004d15ecb03b
  OBB  7d46ce31eb8224ac25d32cf2a9540b014f553e1cac60e0efc5d8dbe2775c1578
Другие копии тоже подойдут, если в них те же файлы игры: патчер проверит сам.

Как пользоваться (Windows):
1. Положите APK и OBB в эту папку.
2. Запустите patch.bat (или перетащите APK и OBB на него мышкой).
3. Через минуту рядом появится CubeSurvival_offline_1.0.4.apk. Его и ставьте на
   телефон, OBB отдельно не нужен.

Linux, macOS, Android (Termux): python3 cube_patcher.py игра.apk main.26.cube.survival.adventure.obb

При первом запуске патчер создаёт ключ подписи cube_patcher_key.json. Не удаляйте его:
поставить новую версию поверх старой (с сохранением прогресса) можно только с тем же ключом.
Сборку из Telegram-канала обновить так не получится, у неё другой ключ.

Игре нужно 32-битное устройство: телефоны и планшеты примерно до 2022-2023 года
или эмуляторы с ARM (BlueStacks, LDPlayer, MuMu).

=== English ===

The patcher turns your own copy of Cube Survival: LDoE 1.0.4 into the offline build
with the mod menu. It contains no game files; they come from your copy.

You need:
- Python 3.8 or newer (https://www.python.org/downloads/; on Windows tick
  "Add python.exe to PATH" in the installer);
- the game APK, version 1.0.4, and the OBB main.26.cube.survival.adventure.obb.
  Archives that contain them (.xapk, .zip) work too.

SHA-256 of the Google Play release:
  APK  15499be6a2d0eefeb66496b394cdfeb5c5828278fc5c7369e594004d15ecb03b
  OBB  7d46ce31eb8224ac25d32cf2a9540b014f553e1cac60e0efc5d8dbe2775c1578
Other copies work as long as they hold the same game files; the patcher checks.

How to use it (Windows):
1. Put the APK and the OBB into this folder.
2. Run patch.bat (or drag the APK and the OBB onto it).
3. In about a minute you get CubeSurvival_offline_1.0.4.apk next to it. Install that
   on your phone; the OBB is not needed separately.

Linux, macOS, Android (Termux): python3 cube_patcher.py game.apk main.26.cube.survival.adventure.obb

On the first run the patcher creates a signing key, cube_patcher_key.json. Keep it:
a new build only installs over the old one (keeping your progress) with the same key.
The build from the Telegram channel can't be updated this way; it has a different key.

The game needs a 32-bit capable device: phones and tablets from before about
2022-2023, or emulators with ARM support (BlueStacks, LDPlayer, MuMu).
