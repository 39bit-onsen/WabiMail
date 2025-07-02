; WabiMail Inno Setup インストーラースクリプト
; 侘び寂びの美学を体現したメールクライアント

#define MyAppName "WabiMail"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "WabiMail Development Team"
#define MyAppURL "https://github.com/wabimail/wabimail"
#define MyAppExeName "WabiMail.exe"
#define MyAppDescription "侘び寂びの美学を体現したメールクライアント"

[Setup]
; アプリケーション基本情報
AppId={{8B7355A1-2F4F-4F4F-8B73-55A12F4F4F4F}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
AppCopyright=Copyright (C) 2025 {#MyAppPublisher}
VersionInfoDescription={#MyAppDescription}
VersionInfoProductName={#MyAppName}
VersionInfoVersion={#MyAppVersion}

; インストール設定
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=..\LICENSE
InfoBeforeFile=..\README.md
OutputDir=..\dist\installer
OutputBaseFilename=WabiMail-Setup-{#MyAppVersion}
SetupIconFile=..\resources\assets\icons\wabimail.ico
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern

; システム要件
MinVersion=6.1sp1
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

; UI設定（侘び寂び美学）
WizardImageFile=..\resources\installer\wizard-large.bmp
WizardSmallImageFile=..\resources\installer\wizard-small.bmp
WizardImageStretch=no
WizardImageBackColor=$F5F5DC
DisableWelcomePage=no

[Languages]
Name: "japanese"; MessagesFile: "compiler:Languages\Japanese.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; メイン実行ファイル
Source: "..\dist\WabiMail.exe"; DestDir: "{app}"; Flags: ignoreversion

; 設定ファイル
Source: "..\config.yaml"; DestDir: "{app}"; Flags: ignoreversion

; アセットファイル
Source: "..\resources\assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs

; ドキュメント
Source: "..\README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\LICENSE"; DestDir: "{app}"; Flags: ignoreversion

; Visual C++ Redistributable（必要に応じて）
; Source: "vcredist_x64.exe"; DestDir: {tmp}; Flags: deleteafterinstall

[Icons]
; スタートメニュー
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Comment: "{#MyAppDescription}"; IconFilename: "{app}\assets\icons\wabimail.ico"
Name: "{group}\README"; Filename: "{app}\README.md"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"

; デスクトップアイコン
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Comment: "{#MyAppDescription}"; IconFilename: "{app}\assets\icons\wabimail.ico"; Tasks: desktopicon

; クイック起動（古いWindows）
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
; インストール後の実行オプション
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

; Visual C++ Redistributable のインストール（必要に応じて）
; Filename: {tmp}\vcredist_x64.exe; Parameters: "/quiet"; StatusMsg: "Visual C++ Redistributable をインストール中..."; Check: VCRedistNeedsInstall

[UninstallDelete]
; アンインストール時に削除するユーザーデータ
Type: filesandordirs; Name: "{userappdata}\WabiMail"
Type: filesandordirs; Name: "{localappdata}\WabiMail"

[Registry]
; ファイル関連付け（.eml ファイル）
Root: HKCR; Subkey: ".eml"; ValueType: string; ValueName: ""; ValueData: "WabiMail.EmailMessage"; Flags: uninsdeletevalue
Root: HKCR; Subkey: "WabiMail.EmailMessage"; ValueType: string; ValueName: ""; ValueData: "WabiMail Email Message"; Flags: uninsdeletekey
Root: HKCR; Subkey: "WabiMail.EmailMessage\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\{#MyAppExeName},0"
Root: HKCR; Subkey: "WabiMail.EmailMessage\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""

; アプリケーション登録
Root: HKLM; Subkey: "Software\{#MyAppPublisher}\{#MyAppName}"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\{#MyAppPublisher}\{#MyAppName}"; ValueType: string; ValueName: "Version"; ValueData: "{#MyAppVersion}"

[Code]
// Visual C++ Redistributable チェック関数
function VCRedistNeedsInstall: Boolean;
begin
  // VC++ 2015-2022 Redistributable の検出
  Result := not RegKeyExists(HKLM, 'SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\X64');
end;

// カスタムページの設定
procedure InitializeWizard;
begin
  // 侘び寂び風のウェルカムメッセージ
  WizardForm.WelcomeLabel2.Caption := 
    'WabiMailは、侘び寂びの美学を体現したシンプルで美しいメールクライアントです。' + #13#10 + #13#10 +
    'このセットアップウィザードでは、お使いのコンピューターにWabiMailをインストールします。' + #13#10 + #13#10 +
    'インストールを開始する前に、他のアプリケーションを終了することをお勧めします。';
end;

// インストール前チェック
function InitializeSetup(): Boolean;
begin
  Result := True;
  
  // 管理者権限チェック
  if not IsAdminLoggedOn then
  begin
    MsgBox('WabiMailのインストールには管理者権限が必要です。', mbError, MB_OK);
    Result := False;
  end;
  
  // Windows バージョンチェック
  if GetWindowsVersion < $06010000 then
  begin
    MsgBox('WabiMailはWindows 7 SP1以降が必要です。', mbError, MB_OK);
    Result := False;
  end;
end;

// アンインストール確認
function InitializeUninstall(): Boolean;
begin
  Result := True;
  if MsgBox('WabiMailをアンインストールしますか？' + #13#10 + 
            '設定やメールデータも削除されます。', 
            mbConfirmation, MB_YESNO) = IDNO then
    Result := False;
end;

// インストール完了後の処理
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // ファイアウォール例外追加（Windowsセキュリティ）
    // Exec('netsh', 'advfirewall firewall add rule name="WabiMail" dir=in action=allow program="' + ExpandConstant('{app}\{#MyAppExeName}') + '"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  end;
end;