# Tap the emulator/device at x,y (screenshot pixels), wait, then screenshot to D:\CubeSurvival\avd\<name>.png
param([int]$X, [int]$Y, [string]$Name = "shot", [double]$Wait = 1.5)
$adb = 'D:\CubeSurvival\sdk\platform-tools\adb.exe'
if (-not $env:ANDROID_SERIAL) { $env:ANDROID_SERIAL = 'emulator-5554' }
if ($X -ge 0) { & $adb shell input tap $X $Y }
Start-Sleep -Milliseconds ([int]($Wait * 1000))
& $adb shell screencap -p /data/local/tmp/s.png | Out-Null
& $adb pull /data/local/tmp/s.png "D:\CubeSurvival\avd\$Name.png" | Out-Null
