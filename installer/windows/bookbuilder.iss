; Inno Setup script for BookBuilder (Windows installer).
; Build on Windows after PyInstaller has produced dist\BookBuilder:
;   iscc installer\windows\bookbuilder.iss /DMyAppVersion=1.0.0
; Produces releases\BookBuilder-<version>-windows-setup.exe with desktop +
; Start-menu shortcuts and an automatic uninstaller.

#define MyAppName "BookBuilder"
#ifndef MyAppVersion
  #define MyAppVersion "1.0.0"
#endif
#define MyAppExe "BookBuilder.exe"

[Setup]
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher=BookBuilder
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=..\..\releases
OutputBaseFilename=BookBuilder-{#MyAppVersion}-windows-setup
SetupIconFile=..\..\assets\bookbuilder.ico
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional icons:"

[Files]
; The entire PyInstaller one-folder bundle.
Source: "..\..\dist\BookBuilder\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExe}"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExe}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExe}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent

; NOTE: PDF input needs poppler (pdftotext) on PATH. It is NOT bundled here;
; .txt/.docx/.epub work out of the box. An internet connection is required
; because voices stream from the Microsoft Edge TTS service.
