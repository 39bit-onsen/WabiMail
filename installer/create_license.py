#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WabiMail ライセンスファイル生成スクリプト

Task 14: Inno Setupインストーラー用ライセンスファイル作成
"""

from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent

def create_license_file():
    """ライセンスファイル作成"""
    
    license_content = """WabiMail ソフトウェアライセンス契約書

Copyright (C) 2025 WabiMail Development Team

本ソフトウェア「WabiMail」（以下「本ソフトウェア」）の使用に関して、以下の条件に同意していただく必要があります。

1. 使用許諾
   本ソフトウェアは、個人および商用利用において無料でご利用いただけます。

2. 配布
   本ソフトウェアの再配布は、元のパッケージを変更せずに行う場合のみ許可されます。

3. 改変
   本ソフトウェアのソースコードの改変は許可されますが、改変版の配布には
   原作者への適切な帰属表示が必要です。

4. 免責事項
   本ソフトウェアは「現状のまま」提供され、明示的または暗示的な保証は
   一切ありません。作者は本ソフトウェアの使用によって生じたいかなる
   損害に対しても責任を負いません。

5. 侘び寂びの精神
   本ソフトウェアは日本の美学である「侘び寂び」の精神に基づいて開発されました。
   シンプルさ、不完全性の美、自然との調和を大切にしています。

6. プライバシー
   WabiMailは、ユーザーの個人情報やメールデータを外部に送信することはありません。
   すべてのデータはお客様のコンピューター上でのみ処理されます。

本ライセンスに同意いただけない場合は、本ソフトウェアをインストールまたは
使用しないでください。

WabiMail Development Team
https://github.com/wabimail/wabimail
"""
    
    license_file = PROJECT_ROOT / "LICENSE"
    with open(license_file, 'w', encoding='utf-8') as f:
        f.write(license_content)
    
    print(f"✅ ライセンスファイル作成: {license_file}")

def create_readme_file():
    """README.mdファイル作成"""
    
    readme_content = """# WabiMail - 侘び寂びメールクライアント

🌸 侘び寂びの美学を体現したシンプルで美しいメールクライアント

## 概要

WabiMailは、日本の美意識である「侘び寂び」の精神に基づいて設計されたデスクトップメールクライアントです。シンプルで直感的なインターフェースを通じて、メールの管理を美しく、穏やかな体験に変えます。

## 特徴

### 🌸 侘び寂びの美学
- **簡素性**: 不要な装飾を排除したミニマルなデザイン
- **自然性**: 自然な色調とオーガニックな要素
- **調和性**: すべての要素が美しく調和したUI

### 📧 強力なメール機能
- **マルチアカウント対応**: Gmail、IMAP、SMTP、POPをサポート
- **OAuth2認証**: Gmailとの安全な認証
- **暗号化**: すべての設定とデータを安全に暗号化
- **添付ファイル**: ファイルの送受信に完全対応

### 🔒 プライバシー重視
- **ローカル処理**: すべてのデータはお客様のPC上でのみ処理
- **暗号化保存**: 認証情報の安全な保管
- **オフライン対応**: インターネット接続なしでも閲覧可能

## システム要件

- **OS**: Windows 7 SP1 以降（64bit推奨）
- **メモリ**: 2GB以上のRAM
- **ディスク**: 100MB以上の空き容量
- **その他**: .NET Framework 4.7.2以降

## インストール

1. `WabiMail-Setup-1.0.0.exe` をダウンロード
2. 実行ファイルを右クリックして「管理者として実行」
3. インストールウィザードの指示に従って進行
4. インストール完了後、WabiMailを起動

## 使用方法

### 初回セットアップ
1. WabiMailを起動
2. 「アカウント追加」をクリック
3. メールプロバイダーを選択（Gmail推奨）
4. 認証情報を入力してアカウントを設定

### 基本操作
- **メール表示**: 左ペインでフォルダー、中央でメールリスト、右で本文
- **新規作成**: ツールバーの「作成」ボタン
- **送信**: 作成画面で「送信」ボタン
- **設定**: メニューの「設定」から各種オプション

## トラブルシューティング

### よくある問題

**Q: Gmailに接続できません**
A: Gmail設定で「安全性の低いアプリ」を有効にするか、OAuth2認証を使用してください。

**Q: アンチウイルスソフトが警告を表示します**
A: WabiMailは安全なソフトウェアです。お使いのアンチウイルスソフトで例外設定を行ってください。

**Q: 設定が保存されません**
A: 管理者権限で実行されていることを確認してください。

## サポート

- **公式サイト**: https://github.com/wabimail/wabimail
- **問題報告**: GitHubのIssuesページ
- **ドキュメント**: プロジェクトWiki

## ライセンス

WabiMail は WabiMail Development Team により開発されています。
詳細はLICENSEファイルをご覧ください。

## 侘び寂びについて

「侘び寂び」は日本古来の美意識で、不完全性、無常性、質素さの中に美を見出す概念です。
WabiMailは、この精神を現代のソフトウェア開発に取り入れ、技術的な複雑さをシンプルで
美しいユーザー体験に昇華することを目指しています。

---

🌸 WabiMail - 美しいメール体験をあなたに

Version: 1.0.0
Build Date: """ + datetime.now().strftime("%Y-%m-%d") + """
Copyright (C) 2025 WabiMail Development Team
"""
    
    readme_file = PROJECT_ROOT / "README.md"
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"✅ READMEファイル作成: {readme_file}")

def main():
    """メイン関数"""
    print("📄 WabiMail インストーラー用ドキュメント作成")
    print("=" * 50)
    
    create_license_file()
    create_readme_file()
    
    print("=" * 50)
    print("✅ ドキュメント作成完了")

if __name__ == "__main__":
    main()