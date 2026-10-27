# Decompile libil2cpp functions whose names match a regex. Usage: dec.ps1 <out.c> <regex>
param([string]$Out, [string]$Regex)
$env:JAVA_HOME = "D:\SupercowAndroid\toolchain\jdk\jdk-21.0.12.1+1"
$rf = "D:\CubeSurvival\ghidra\regex.txt"
[IO.File]::WriteAllText($rf, $Regex)
& D:\Ghidra\ghidra_12.1.4_PUBLIC\support\analyzeHeadless.bat D:\CubeSurvival\ghidra cube -process libil2cpp.so -noanalysis -readOnly -scriptPath D:\Ghidra\scripts -postScript DecompMatch.java $Out "@$rf" *> D:\CubeSurvival\ghidra\dec.log
Get-Content D:\CubeSurvival\ghidra\dec.log | Select-String "functions:|ERROR|Exception" | Select-Object -First 5
