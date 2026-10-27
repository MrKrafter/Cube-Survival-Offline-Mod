# Take an emulator/device screenshot to D:\CubeSurvival\avd\<name>.png
param([string]$Name = "shot")
adb shell screencap -p /data/local/tmp/s.png | Out-Null
adb pull /data/local/tmp/s.png "D:\CubeSurvival\avd\$Name.png" | Out-Null
