Set UAC = CreateObject("Shell.Application")
Set FSO = CreateObject("Scripting.FileSystemObject")

scriptDir = FSO.GetParentFolderName(WScript.ScriptFullName)
toolsDir = FSO.GetParentFolderName(scriptDir)
baseDir = FSO.GetParentFolderName(toolsDir)

batPath = baseDir & "\JRFK_Migrator.bat"
If Not FSO.FileExists(batPath) Then
    MsgBox "Could not find JRFK_Migrator.bat in: " & baseDir, 16, "JRFK Migrator"
    WScript.Quit 1
End If

UAC.ShellExecute batPath, "", baseDir, "runas", 1
