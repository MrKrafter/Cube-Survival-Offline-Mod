# Build libcubefix.so (armeabi-v7a).  CUBE_NDK_BIN = <ndk>\toolchains\llvm\prebuilt\windows-x86_64\bin
$ErrorActionPreference = "Stop"
$ndk = $env:CUBE_NDK_BIN
if (-not $ndk) { throw "set CUBE_NDK_BIN to the NDK's llvm bin directory (see README.md)" }
Set-Location $PSScriptRoot
& "$ndk\clang.exe" --target=armv7a-linux-androideabi21 -marm -O2 -fPIC -shared -Wall -o libcubefix.so cubefix.c mods.c refs.S -llog -ldl "-Wl,--no-undefined" "-Wl,-z,max-page-size=16384"
if ($LASTEXITCODE -ne 0) { exit 1 }
& "$ndk\llvm-strip.exe" libcubefix.so
"built " + (Get-Item libcubefix.so).Length
