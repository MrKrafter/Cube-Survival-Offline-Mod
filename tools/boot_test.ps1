# Start the game on the emulator with the given mod options on; report whether it got to the player (log "player health resource").
param([string]$Opts = "", [int]$Wait = 60)
$env:ANDROID_SERIAL = 'emulator-5554'
python D:\CubeSurvival\scripts\set_prefs.py $Opts.Split(' ') | Out-Null
adb logcat -c
adb shell monkey -p cube.survival.adventure -c android.intent.category.LAUNCHER 1 | Out-Null
$ok = $false
for ($t = 0; $t -lt $Wait -and -not $ok; $t += 5) {
    Start-Sleep 5
    $ok = [bool](adb logcat -d -s cubemod | Select-String 'player health resource')
}
"opts [$Opts] -> " + $(if ($ok) { "OK after ${t}s" } else { "HANG" })
