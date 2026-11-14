@echo off
set CSC="C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe"
%CSC% /nologo /t:winexe /optimize+ /out:"%~dp0Preview_Presentation_1.exe" "%~dp0SimpleLauncher.cs"
copy /y "%~dp0Preview_Presentation_1.exe" "%~dp0..\..\Preview_Presentation_1.exe"
copy /y "%~dp0Preview_Presentation_1.exe" "%~dp0..\..\docs\deck1\Preview_Presentation_1.exe"
echo Build complete.
