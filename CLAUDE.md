# WabiMail - Claude開発メモ

## プロジェクト概要

WabiMailは日本の「侘び寂び」にインスパイアされたシンプルで静かなWindowsデスクトップメールクライアントです。

## ドキュメント構成

### 設計書類
- `docs/要件定義書.md` - プロジェクトの目的、対象ユーザー、核心機能を定義
- `docs/画面仕様書.md` - 5つの主要画面（G001-G005）と3ペインレイアウトの詳細設計
- `docs/技術設計書.md` - Python/Tkinterベースのアーキテクチャと実装方針
- `docs/ブランドガイドライン.md` - 「侘び寂び」に基づくデザイン哲学と視覚的指針
- `docs/インストーラー仕様書.md` - Windows向けInno Setupインストーラーの仕様
- `docs/開発手順書.md` - 開発環境構築からリリースまでの具体的な手順
- `docs/開発フェーズ計画書.md` - 3フェーズに分けた開発計画とスケジュール

## 技術スタック

- **言語**: Python 3.10+
- **GUI**: Tkinter（標準ライブラリ）
- **メール通信**: imaplib, smtplib, poplib（標準ライブラリ）
- **Gmail連携**: google-auth-oauthlib（OAuth2認証）
- **パッケージング**: PyInstaller + Inno Setup
- **対象OS**: Windows 10/11（64bit）

## プロジェクト構造

```
WabiMail/
├─ src/             # メインアプリケーション
│  ├─ main.py       # エントリーポイント
│  ├─ ui/           # GUI関連
│  ├─ mail/         # メール通信処理
│  ├─ utils/        # ユーティリティ
│  └─ config/       # 設定管理
├─ resources/       # アイコン・画像
├─ installer/       # Inno Setupスクリプト
├─ docs/            # 設計書・ブランドガイド
├─ tests/           # テストコード
├─ build/           # バイナリ生成物
└─ requirements.txt # 依存パッケージ
```

## 開発フェーズ

### フェーズ1：基盤構築（高優先度）
1. 開発環境セットアップ
2. プロジェクト基本構造作成
3. アカウント管理モジュール
4. メール通信モジュール
5. 基本GUI実装

### フェーズ2：コア機能実装（中優先度）
6. Gmail OAuth2認証機能
7. アカウント設定画面
8. メール表示機能
9. メール送信機能
10. データ永続化

### フェーズ3：仕上げ・配布準備（低優先度）
11. 設定画面実装
12. 統合テスト
13. PyInstaller実行ファイル生成
14. Inno Setupインストーラー作成
15. 最終品質保証テスト

## 主要機能

- **複数アカウント対応**: Gmail, IMAP, SMTP, POP
- **OAuth2認証**: Gmailアカウントのセキュア認証
- **3ペインUI**: アカウント・メールリスト・本文表示
- **ミニマルデザイン**: 侘び寂びの美学に基づく静かなUI
- **セキュリティ**: 認証情報の暗号化保存
- **インストーラー**: Windows用ウィザード形式

## 開発時の注意点

### セキュリティ
- `client_secret.json`は**Git管理対象外**（.gitignoreに追加済み）
- 認証情報は暗号化してローカル保存
- テスト用アカウントを使用し、個人情報は含めない

### ブランドガイドライン
- 余白と静けさを重視したUI設計
- ソフトな白/クリーム色ベース
- 日本語フォント: Meiryo, Yu Gothic
- 装飾は最小限に抑制

### 開発コマンド
```bash
# 開発環境セットアップ
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# アプリケーション起動
cd src
python main.py

# テスト実行
python -m pytest tests/

# 実行ファイル生成
pyinstaller --onefile --windowed src/main.py
```

## 現在の状態

- **完了**: 要件定義、設計書作成、開発計画策定
- **進行中**: 開発フェーズ1の準備
- **次のステップ**: 開発環境セットアップから開始

## 更新履歴

- 2025-07-01: 初版作成、ドキュメント確認完了、開発計画策定