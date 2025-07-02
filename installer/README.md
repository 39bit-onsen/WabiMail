# WabiMail Inno Setup インストーラー

## 概要

このディレクトリには、WabiMailのWindows用インストーラーを作成するためのInno Setupスクリプトとツールが含まれています。

## ファイル構成

```
installer/
├── wabimail_installer.iss    # Inno Setup メインスクリプト
├── build_installer.py        # インストーラービルドスクリプト
├── test_installer.py         # インストーラーテストスクリプト
├── create_license.py         # ライセンス・README生成
└── README.md                 # このファイル
```

## 必要な環境

### Windows開発環境
- **Inno Setup 6**: [ダウンロード](https://jrsoftware.org/isdl.php)
- **Python 3.10+**: スクリプト実行用
- **管理者権限**: インストーラーテスト用

### 前提条件
- PyInstallerによる実行ファイル（`dist/WabiMail.exe`）が生成済み
- プロジェクトルートに`config.yaml`、`LICENSE`、`README.md`が存在

## インストーラー作成手順

### 1. 環境準備

```bash
# Inno Setup 6 をインストール
# https://jrsoftware.org/isdl.php からダウンロード

# Python依存関係
pip install pillow  # アイコン変換用
```

### 2. ドキュメント作成

```bash
python installer/create_license.py
```

### 3. インストーラービルド

```bash
python installer/build_installer.py
```

### 4. インストーラーテスト（Windowsのみ）

```bash
# 管理者権限で実行
python installer/test_installer.py
```

## Inno Setup スクリプト仕様

### 基本設定
- **アプリケーション名**: WabiMail
- **バージョン**: 1.0.0
- **インストール先**: `C:\Program Files\WabiMail`
- **UI言語**: 日本語・英語対応

### インストール内容
- `WabiMail.exe` - メイン実行ファイル
- `config.yaml` - 設定ファイル
- `assets/` - アイコン・リソース
- `README.md` - ドキュメント
- `LICENSE` - ライセンス

### 機能
- **デスクトップショートカット**: オプション選択可能
- **スタートメニュー**: 自動作成
- **ファイル関連付け**: .emlファイル
- **レジストリ登録**: アプリケーション情報
- **アンインストーラー**: 完全な削除機能

### セキュリティ
- **コード署名**: 対応可能（証明書必要）
- **管理者権限**: インストール時に要求
- **ファイアウォール**: 例外追加オプション

## 侘び寂び美学の実装

### UI デザイン
- **色調**: ベージュ（#F5F5DC）とダークスレートグレー（#2F4F4F）
- **画像**: ミニマルなウィザード画像を自動生成
- **メッセージ**: 和の心を感じる説明文

### ユーザー体験
- **シンプルさ**: 最小限の設定項目
- **直感性**: わかりやすいインストール手順
- **調和**: Windowsの標準UIとの自然な統合

## トラブルシューティング

### よくある問題

**Inno Setup が見つからない**
```
エラー: Inno Setup コンパイラーが見つかりません
解決: C:\Program Files (x86)\Inno Setup 6\ISCC.exe を確認
```

**実行ファイルが見つからない**
```
エラー: WabiMail.exe が見つかりません
解決: python build_exe.py を先に実行
```

**管理者権限エラー**
```
エラー: 管理者権限が必要です
解決: PowerShellまたはコマンドプロンプトを管理者として実行
```

### ログファイル
- **ビルドログ**: `build_reports/installer_build_report_*.txt`
- **テストログ**: `test_reports/installer_test_report_*.json`

## カスタマイズ

### アイコン変更
```pascal
; wabimail_installer.iss 内
SetupIconFile=..\resources\assets\icons\your_icon.ico
```

### インストール先変更
```pascal
; wabimail_installer.iss 内
DefaultDirName={autopf}\YourAppName
```

### 追加ファイル
```pascal
; [Files] セクションに追加
Source: "your_file.txt"; DestDir: "{app}"; Flags: ignoreversion
```

## CI/CD統合

### GitHub Actions例
```yaml
- name: Build Installer
  run: |
    python installer/build_installer.py
    
- name: Test Installer
  run: |
    python installer/test_installer.py
```

### 自動署名
```bash
# コード署名（証明書が必要）
signtool sign /a /t http://timestamp.comodoca.com dist/installer/WabiMail-Setup-1.0.0.exe
```

## 配布

### ファイル構成
```
dist/installer/
└── WabiMail-Setup-1.0.0.exe  # 配布用インストーラー
```

### チェックサム生成
```bash
# SHA256 ハッシュ生成
certutil -hashfile WabiMail-Setup-1.0.0.exe SHA256
```

---

**作成者**: WabiMail Development Team  
**更新日**: 2025-07-02  
**バージョン**: 1.0.0