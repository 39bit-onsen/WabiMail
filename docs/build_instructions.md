# WabiMail ビルド手順書

## 概要

このドキュメントでは、WabiMailの実行ファイルをPyInstallerを使用してビルドする手順を説明します。

## 必要な環境

### Python環境
- Python 3.10以上
- pip（パッケージマネージャー）

### 必要なパッケージ
```bash
pip install pyinstaller
pip install pillow  # 画像処理用
```

## ビルド手順

### 1. 環境準備

```bash
# プロジェクトディレクトリに移動
cd WabiMail

# 仮想環境の作成（推奨）
python -m venv venv

# 仮想環境の有効化
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 依存関係のインストール
pip install -r requirements.txt
pip install pyinstaller
```

### 2. シンプルビルド（推奨）

最も簡単な方法は`build_simple.py`を使用することです：

```bash
python build_simple.py
```

このスクリプトは以下を自動的に実行します：
- 既存のビルドディレクトリのクリーンアップ
- 必要なアイコンファイルの準備
- PyInstallerによるビルド実行
- 実行ファイルの生成（dist/ディレクトリ内）

### 3. 詳細ビルド（高度な設定）

より詳細な制御が必要な場合は`build_exe.py`を使用します：

```bash
python build_exe.py
```

このスクリプトは以下の追加機能を提供します：
- プラットフォーム別の最適化
- 配布用パッケージの自動作成
- ビルドレポートの生成
- 実行ファイルの基本テスト

### 4. カスタムビルド（上級者向け）

PyInstaller specファイルを直接使用する場合：

```bash
# specファイルの生成
python build_config/pyinstaller_spec.py

# ビルド実行
pyinstaller WabiMail.spec
```

## プラットフォーム別の注意事項

### Windows
- 実行ファイル名: `WabiMail.exe`
- 場所: `dist/WabiMail.exe`
- アイコン: `.ico`形式が推奨
- Windows Defenderの警告が出る場合があります

### macOS
- 実行ファイル名: `WabiMail.app`
- 場所: `dist/WabiMail.app`
- アイコン: `.icns`形式が推奨
- 初回実行時にセキュリティ警告が出る場合があります
- コード署名が必要な場合があります

### Linux
- 実行ファイル名: `wabimail`または`WabiMail`
- 場所: `dist/wabimail`
- アイコン: `.png`形式
- 実行権限の付与が必要: `chmod +x dist/wabimail`

## ビルドオプション

### 単一ファイル vs ディレクトリ

#### 単一ファイル（--onefile）
```bash
pyinstaller --onefile src/main.py
```
- 利点: 配布が簡単
- 欠点: 起動が遅い、ファイルサイズが大きい

#### ディレクトリ（デフォルト）
```bash
pyinstaller src/main.py
```
- 利点: 起動が速い
- 欠点: 複数ファイルの管理が必要

### デバッグビルド

問題解決のためのデバッグビルド：

```bash
pyinstaller --debug=all --console src/main.py
```

## トラブルシューティング

### 1. ModuleNotFoundError

隠しインポートを追加：
```bash
pyinstaller --hidden-import=module_name src/main.py
```

### 2. データファイルが見つからない

データファイルを明示的に追加：
```bash
pyinstaller --add-data "config.yaml;." src/main.py  # Windows
pyinstaller --add-data "config.yaml:." src/main.py  # macOS/Linux
```

### 3. アンチウイルスの誤検知

- PyInstallerで生成されたファイルは誤検知されることがあります
- デジタル署名の追加を検討してください
- VirusTotalでスキャンして確認

### 4. 実行時エラー

1. コンソールモードでビルドして詳細を確認：
   ```bash
   pyinstaller --console src/main.py
   ```

2. ログファイルの確認：
   - `build/WabiMail/warn-WabiMail.txt`
   - `build/WabiMail/xref-WabiMail.html`

## ビルド後のテスト

### 基本テスト

```bash
# 実行ファイルのテスト
python test_executable.py
```

### 手動テスト項目

1. **起動テスト**
   - アプリケーションが正常に起動するか
   - スプラッシュスクリーンが表示されるか

2. **機能テスト**
   - アカウント追加機能
   - メール送受信機能
   - 設定保存機能

3. **パフォーマンステスト**
   - 起動時間
   - メモリ使用量
   - レスポンス速度

## 配布準備

### 1. コード署名（推奨）

#### Windows
```bash
signtool sign /a /t http://timestamp.comodoca.com/authenticode dist/WabiMail.exe
```

#### macOS
```bash
codesign --deep --force --verify --verbose --sign "Developer ID Application: Your Name" dist/WabiMail.app
```

### 2. パッケージング

#### Windows（ZIP）
```bash
python -c "import shutil; shutil.make_archive('WabiMail-Windows', 'zip', 'dist')"
```

#### macOS（DMG）
```bash
hdiutil create -volname "WabiMail" -srcfolder dist/WabiMail.app -ov -format UDZO WabiMail.dmg
```

#### Linux（tar.gz）
```bash
tar -czf WabiMail-Linux.tar.gz -C dist .
```

## ビルド自動化

### GitHub Actions（CI/CD）

`.github/workflows/build.yml`:
```yaml
name: Build WabiMail

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    strategy:
      matrix:
        os: [windows-latest, macos-latest, ubuntu-latest]
    
    runs-on: ${{ matrix.os }}
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pyinstaller
    
    - name: Build executable
      run: python build_exe.py
    
    - name: Upload artifacts
      uses: actions/upload-artifact@v2
      with:
        name: WabiMail-${{ matrix.os }}
        path: dist/
```

## まとめ

WabiMailのビルドプロセスは、PyInstallerを使用して簡単に実行できます。プラットフォーム別の注意事項を理解し、適切なテストを行うことで、高品質な実行ファイルを作成できます。

問題が発生した場合は、デバッグモードでのビルドやログファイルの確認を行い、トラブルシューティングセクションを参照してください。