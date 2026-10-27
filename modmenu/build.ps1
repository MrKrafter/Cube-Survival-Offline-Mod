# Compile the mod menu (Java) and drop it into the apktool tree as smali.
# Needs CUBE_JDK (JDK 17+ home), CUBE_BUILD_TOOLS (build-tools dir with d8.bat), CUBE_ANDROID_JAR (platform android.jar);
# CUBE_APKTOOL is optional (default toolchain\apktool.jar).
$ErrorActionPreference = "Stop"
foreach ($n in "CUBE_JDK", "CUBE_BUILD_TOOLS", "CUBE_ANDROID_JAR") {
    if (-not (Get-Item "env:$n" -ErrorAction SilentlyContinue)) { throw "set $n (see README.md)" }
}
$jdk = $env:CUBE_JDK
$bt = $env:CUBE_BUILD_TOOLS
$jar = $env:CUBE_ANDROID_JAR
$root = Split-Path $PSScriptRoot
$apktool = if ($env:CUBE_APKTOOL) { $env:CUBE_APKTOOL } else { "$root\toolchain\apktool.jar" }
$env:JAVA_HOME = $jdk
Set-Location $PSScriptRoot
Remove-Item -Recurse -Force out -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force out\classes, out\dex | Out-Null
& "$jdk\bin\javac.exe" -encoding UTF-8 --release 8 -Xlint:-options -cp $jar -d out\classes (Get-ChildItem src -Recurse -Filter *.java | % FullName)
if ($LASTEXITCODE -ne 0) { exit 1 }
& cmd /c "$bt\d8.bat" --min-api 16 --lib $jar --output out\dex (Get-ChildItem out\classes -Recurse -Filter *.class | % FullName)
if ($LASTEXITCODE -ne 0) { exit 1 }
$dst = "$root\apktool_cube\smali\cube\mod"
Remove-Item -Recurse -Force $dst -ErrorAction SilentlyContinue
# apktool's bundled baksmali has no CLI entry point; decoding a zip that holds only classes.dex works.
& "$jdk\bin\jar.exe" cfM out\mm.zip -C out\dex classes.dex
& "$jdk\bin\java.exe" -jar $apktool d -r -f out\mm.zip -o out\dec | Out-Null
if ($LASTEXITCODE -ne 0) { exit 1 }
Copy-Item -Recurse out\dec\smali\cube\mod $dst
"modmenu smali: " + (Get-ChildItem $dst).Count + " files"
