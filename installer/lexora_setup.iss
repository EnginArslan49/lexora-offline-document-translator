; ============================================================
; Lexora — Inno Setup Script
; ============================================================
; Derleme: iscc.exe installer\lexora_setup.iss
; Önkoşul: Inno Setup 6 kurulu olmalı.
; Ayrıca dist\Lexora\ oluşturulmuş olmalı (PyInstaller).
; ============================================================

#define MyAppName "Lexora"
#define MyAppVersion "1.0.1"
#define MyAppPublisher "Engin ARSLAN"
#define MyAppURL "https://github.com/EnginArslan49"
#define MyAppExeName "Lexora.exe"

[Setup]
AppId={{9F1C4C8A-LEXORA-101-SETUP-000000000001}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
DefaultDirName={localappdata}\Programs\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=..\installer\output
OutputBaseFilename=Lexora_Setup_{#MyAppVersion}
SetupIconFile=..\resources\icons\app.ico
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "turkish"; MessagesFile: "compiler:Languages\Turkish.isl"

[Tasks]
Name: "desktopicon"; Description: "Masaüstü kısayolu oluştur"; GroupDescription: "Ek görevler:"; Flags: unchecked

[Files]
Source: "..\dist\Lexora\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{#MyAppName} Kaldır"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Lexora'yı başlat"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"

[Code]
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  DataDir: String;
begin
  if CurUninstallStep = usPostUninstall then
  begin
    DataDir := ExpandConstant('{localappdata}\Lexora');
    if DirExists(DataDir) then
    begin
      if MsgBox('Lexora ayarları ve çeviri geçmişi de silinsin mi?' + #13#10 +
                '(Hayır derseniz bir sonraki kurulumda korunur.)',
                mbConfirmation, MB_YESNO) = IDYES then
      begin
        DelTree(DataDir, True, True, True);
      end;
    end;
  end;
end;