# Build libcubefix.so (armeabi-v7a).  CUBE_NDK_BIN = <ndk>\toolchains\llvm\prebuilt\windows-x86_64\bin
# -Slot builds libcubefix_slot.so for the patcher: no embedded game data, an empty slot instead (see refs.S).
param([switch]$Slot)
$ErrorActionPreference = "Stop"
$ndk = $env:CUBE_NDK_BIN
if (-not $ndk) { throw "set CUBE_NDK_BIN to the NDK's llvm bin directory (see README.md)" }
Set-Location $PSScriptRoot
$out = "libcubefix.so"
$defs = @()
if ($Slot) { $out = "libcubefix_slot.so"; $defs = @("-DCUBE_REFS_SLOT=0x100000") }
& "$ndk\clang.exe" --target=armv7a-linux-androideabi21 -marm -O2 -fPIC -shared -Wall @defs -o $out cubefix.c mods.c refs.S icon.S -llog -ldl "-Wl,--no-undefined" "-Wl,-z,max-page-size=16384"
if ($LASTEXITCODE -ne 0) { exit 1 }
& "$ndk\llvm-strip.exe" $out
"built $out " + (Get-Item $out).Length
