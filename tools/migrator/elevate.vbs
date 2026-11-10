Set UAC = CreateObject("Shell.Application")
Set FSO = CreateObject("Scripting.FileSystemObject")

scriptDir = FSO.GetParentFolderName(WScript.ScriptFullName)
toolsDir = FSO.GetParentFolderName(scriptDir)
baseDir = FSO.GetParentFolderName(toolsDir)

batPath = baseDir & "\JRFK_Migrator.bat"
If Not FSO.FileExists(batPath) Then
    batPath = "D:\JRFK\JRFK_Migrator.bat"
    baseDir = "D:\JRFK"
End If

UAC.ShellExecute batPath, "", baseDir, "runas", 1
