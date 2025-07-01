#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基本GUI実装のデモンストレーション

WabiMailの基本GUI機能を実際に試すためのデモスクリプトです。
3ペインレイアウト、アカウント管理、メール表示等の機能を確認します。

Author: WabiMail Development Team
Created: 2025-07-01
"""

import sys
from pathlib import Path
from datetime import datetime

# プロジェクトルートをPythonパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.mail.account import Account, AccountType, AuthType
from src.mail.account_manager import AccountManager
from src.mail.mail_message import MailMessage, MessageFlag, MailAttachment
from src.config.app_config import AppConfig
from src.utils.logger import setup_logger


def create_demo_accounts() -> list[Account]:
    """
    デモ用アカウントを作成します
    
    Returns:
        list[Account]: デモアカウントのリスト
    """
    accounts = []
    
    # Gmail アカウント
    gmail_account = Account(
        name="仕事用Gmail",
        email_address="work@gmail.com",
        account_type=AccountType.GMAIL,
        auth_type=AuthType.OAUTH2
    )
    gmail_account.apply_preset_settings()
    accounts.append(gmail_account)
    
    # IMAP アカウント
    imap_account = Account(
        name="プライベートメール",
        email_address="private@example.com", 
        account_type=AccountType.IMAP,
        auth_type=AuthType.PASSWORD
    )
    imap_account.settings.incoming_server = "imap.example.com"
    imap_account.settings.incoming_port = 993
    imap_account.settings.incoming_security = "SSL"
    imap_account.settings.outgoing_server = "smtp.example.com"
    imap_account.settings.outgoing_port = 587
    imap_account.settings.outgoing_security = "STARTTLS"
    accounts.append(imap_account)
    
    # POP3 アカウント
    pop_account = Account(
        name="レガシーメール",
        email_address="legacy@oldmail.com",
        account_type=AccountType.POP3,
        auth_type=AuthType.PASSWORD
    )
    pop_account.settings.incoming_server = "pop.oldmail.com"
    pop_account.settings.incoming_port = 995
    pop_account.settings.incoming_security = "SSL"
    pop_account.settings.outgoing_server = "smtp.oldmail.com"
    pop_account.settings.outgoing_port = 25
    pop_account.settings.outgoing_security = "NONE"
    accounts.append(pop_account)
    
    return accounts


def create_demo_messages() -> list[MailMessage]:
    """
    デモ用メッセージを作成します
    
    Returns:
        list[MailMessage]: デモメッセージのリスト
    """
    messages = []
    
    # メッセージ1: WabiMail進捗報告
    msg1 = MailMessage(
        subject="🌸 WabiMail基本GUI実装完了報告",
        sender="dev-team@wabimail.example.com",
        recipients=["user@example.com"],
        cc_recipients=["manager@example.com"],
        body_text="""WabiMail開発チームです。

基本GUI実装が完了いたしました。

【実装完了機能】
• 3ペインレイアウト（アカウント・フォルダ／メール一覧／本文表示）
• 侘び寂びデザインテーマ（和紙色・薄桜色・墨色の配色）
• アカウント管理機能（Gmail、IMAP、SMTP、POP3対応）
• メール一覧表示（フラグ、送信者、件名、日時）
• メール本文表示（ヘッダー・本文・添付ファイル情報）
• ツールバー（新規作成・更新・アカウント追加・検索）
• メニューバー（ファイル・表示・ヘルプ）
• ステータスバー（状態表示・接続状態）

【デザイン特徴】
• 余白を活かしたミニマルデザイン
• 絵文字による視覚的な状態表現
• 日本語ローカライゼーション
• 直感的なキーボード・マウス操作

【技術的特徴】
• Tkinter + TTK による高品質GUI
• 3ペインのリサイズ対応
• バックグラウンドでのメール読み込み
• エラーハンドリングと状態管理
• サンプルデータによる動作確認

侘び寂びの精神に基づき、シンプルで美しいインターフェースを実現しました。
ユーザーが迷うことなく、静かで心地よいメール体験を提供します。

次のフェーズでは、OAuth2認証機能の実装に進みます。

--
WabiMail開発チーム
🌸 静寂の中の美しさを追求して""",
        body_html="""<html>
<body style="font-family: 'Yu Gothic', 'Meiryo', sans-serif; color: #333; background: #fefefe;">
<h2 style="color: #666; border-bottom: 1px solid #eee;">🌸 WabiMail基本GUI実装完了</h2>

<p>WabiMail開発チームです。</p>
<p>基本GUI実装が完了いたしました。</p>

<h3 style="color: #888;">【実装完了機能】</h3>
<ul style="color: #555;">
<li>3ペインレイアウト（アカウント・フォルダ／メール一覧／本文表示）</li>
<li>侘び寂びデザインテーマ（和紙色・薄桜色・墨色の配色）</li>
<li>アカウント管理機能（Gmail、IMAP、SMTP、POP3対応）</li>
<li>メール一覧表示（フラグ、送信者、件名、日時）</li>
<li>メール本文表示（ヘッダー・本文・添付ファイル情報）</li>
</ul>

<div style="background: #f9f9f9; padding: 15px; border-left: 3px solid #ddd; margin: 20px 0;">
侘び寂びの精神に基づき、シンプルで美しいインターフェースを実現しました。<br>
ユーザーが迷うことなく、静かで心地よいメール体験を提供します。
</div>

<p>次のフェーズでは、OAuth2認証機能の実装に進みます。</p>

<hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
<p style="color: #888; font-size: 0.9em;">
WabiMail開発チーム<br>
🌸 静寂の中の美しさを追求して
</p>
</body>
</html>""",
        priority="high"
    )
    msg1.add_flag(MessageFlag.FLAGGED)  # 重要マーク
    
    # 添付ファイルを追加
    attachment1 = MailAttachment(
        filename="gui_specifications.pdf",
        content_type="application/pdf",
        size=512000,
        is_inline=False
    )
    attachment2 = MailAttachment(
        filename="wabi_sabi_design.jpg",
        content_type="image/jpeg",
        size=256000,
        is_inline=True,
        content_id="<design@wabimail>"
    )
    msg1.attachments.extend([attachment1, attachment2])
    messages.append(msg1)
    
    # メッセージ2: テスト用
    msg2 = MailMessage(
        subject="GUI実装テスト - 3ペインレイアウト",
        sender="test@wabimail.example.com",
        recipients=["user@example.com"],
        body_text="""GUI実装のテストメッセージです。

3ペインレイアウトの動作確認：
• 左ペイン：アカウント・フォルダツリー表示
• 中央ペイン：メール一覧（件名・送信者・日時）
• 右ペイン：選択メールの本文表示

メール選択、フラグ操作、検索機能等を確認してください。""",
        priority="normal"
    )
    msg2.mark_as_read()
    messages.append(msg2)
    
    # メッセージ3: 未読メッセージ
    msg3 = MailMessage(
        subject="侘び寂びデザインテーマ適用完了",
        sender="design@wabimail.example.com",
        recipients=["user@example.com"],
        body_text="""デザインチームより報告いたします。

侘び寂びテーマの適用が完了しました：

【カラーパレット】
• ベースカラー：和紙白（#fefefe）
• アクセント：薄いグレー（#f5f5f5）
• テキスト：墨色（#333333）
• 選択色：薄桜色（#ffe8e8）

【フォント】
• Yu Gothic UI（日本語対応）
• 読みやすさと美しさを両立

【アイコン】
• 絵文字による直感的な状態表現
• 📧📬📥📤📝⚠️🗑️📖📩⭐📎など

静かで落ち着いた雰囲気をお楽しみください。""",
        priority="normal"
    )
    # 未読のまま残す
    messages.append(msg3)
    
    # メッセージ4: 返信済みメッセージ
    msg4 = MailMessage(
        subject="Re: UIコンポーネント設計について",
        sender="architect@wabimail.example.com",
        recipients=["user@example.com"],
        body_text="""ご質問いただいたUIコンポーネント設計について回答いたします。

WabiMailでは以下のコンポーネント設計を採用しています：

1. MVCパターンの適用
   - Model: Account, MailMessage等のデータクラス
   - View: MainWindow, Dialogクラス
   - Controller: イベントハンドラーとビジネスロジック

2. 状態管理の分離
   - current_account, current_folder等で状態管理
   - UI更新とデータ更新の分離

3. 拡張性の確保
   - プラグイン機能の将来対応
   - テーマ・カスタマイゼーション対応

詳細は添付の設計書をご確認ください。""",
        priority="normal"
    )
    msg4.mark_as_read()
    msg4.add_flag(MessageFlag.ANSWERED)  # 返信済み
    messages.append(msg4)
    
    return messages


def demo_gui_components():
    """
    GUIコンポーネントのデモ
    """
    print("\n" + "="*60)
    print("🎨 基本GUI実装コンポーネントデモ")
    print("="*60)
    
    # アカウント管理デモ
    print(f"\n📧 アカウント管理機能:")
    accounts = create_demo_accounts()
    
    for i, account in enumerate(accounts, 1):
        print(f"  {i}. {account.account_type.value.upper()}アカウント")
        print(f"     名前: {account.name}")
        print(f"     メールアドレス: {account.email_address}")
        print(f"     認証方式: {account.auth_type.value}")
        print(f"     受信サーバー: {account.settings.incoming_server}:{account.settings.incoming_port}")
        print(f"     暗号化: {account.settings.incoming_security}")
        print()
    
    # メール一覧デモ
    print(f"\n📥 メール一覧表示機能:")
    messages = create_demo_messages()
    
    print(f"  {'フラグ':>4} {'送信者':>25} {'件名':>35} {'日時':>15}")
    print(f"  {'-'*4} {'-'*25} {'-'*35} {'-'*15}")
    
    for message in messages:
        # フラグ表示
        flags = ""
        if message.is_read():
            flags += "📖"
        else:
            flags += "📩"
        if message.is_flagged():
            flags += "⭐"
        if message.has_attachments():
            flags += "📎"
        if message.has_flag(MessageFlag.ANSWERED):
            flags += "↩️"
        
        # 送信者（短縮）
        sender = message.sender
        if len(sender) > 23:
            sender = sender[:20] + "..."
        
        # 件名（短縮）
        subject = message.subject
        if len(subject) > 33:
            subject = subject[:30] + "..."
        
        # 日時
        date_str = message.get_display_date().strftime("%m/%d %H:%M")
        
        print(f"  {flags:>4} {sender:>25} {subject:>35} {date_str:>15}")
    
    # 本文表示デモ
    print(f"\n📖 メール本文表示機能:")
    selected_message = messages[0]  # 最初のメッセージを選択
    
    print(f"  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"  差出人: {selected_message.sender}")
    print(f"  宛先: {', '.join(selected_message.recipients)}")
    if selected_message.cc_recipients:
        print(f"  CC: {', '.join(selected_message.cc_recipients)}")
    print(f"  件名: {selected_message.subject}")
    print(f"  日時: {selected_message.get_display_date().strftime('%Y年%m月%d日 %H時%M分')}")
    print(f"  優先度: {selected_message.priority}")
    print(f"  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()
    
    # 本文プレビュー
    body_preview = selected_message.get_body_preview(300)
    print(f"  {body_preview}")
    print()
    
    # 添付ファイル情報
    if selected_message.has_attachments():
        print(f"  📎 添付ファイル ({selected_message.get_attachment_count()}件):")
        for i, attachment in enumerate(selected_message.attachments, 1):
            inline_text = "(インライン)" if attachment.is_inline else ""
            print(f"    {i}. {attachment.filename} - {attachment.size:,}バイト {inline_text}")
        print()


def demo_gui_layout():
    """
    GUIレイアウトのデモ
    """
    print("\n" + "="*60)
    print("🖼️ 3ペインレイアウト構成デモ")
    print("="*60)
    
    print("""
┌─────────────────────────────────────────────────────────────────────────────┐
│ 🌸 WabiMail - 侘び寂びメールクライアント                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│ [📝新規メール] [🔄更新] [➕アカウント追加]              [🔍検索ボックス] │
├───────────────┬─────────────────────┬───────────────────────────────────────┤
│ 📧 アカウント │ 📥 メール一覧       │ 📖 メール内容                        │
│  ・フォルダ    │                     │                                       │
│               │                     │                                       │
│ 📧 Gmail      │ フラグ 送信者 件名  │ 差出人: dev-team@wabimail...          │
│ └📥 受信トレイ │  📩⭐📎 dev... 🌸Wa │ 宛先: user@example.com                │
│ └📤 送信済み  │  📖   test... GUI  │ 件名: 🌸 WabiMail基本GUI実装完了報告  │
│ └📝 下書き    │  📩   design. 侘び │ 日時: 2025年07月01日 13時30分         │
│               │                     │ ─────────────────────────────────────│
│ 📬 IMAP       │                     │                                       │
│ └📥 受信トレイ │                     │ WabiMail開発チームです。              │
│ └📤 送信済み  │                     │                                       │
│               │                     │ 基本GUI実装が完了いたしました。       │
│ 📬 POP3       │                     │                                       │
│ └📥 受信トレイ │                     │ 【実装完了機能】                      │
│               │                     │ • 3ペインレイアウト                   │
├───────────────┴─────────────────────┴───────────────────────────────────────┤
│ ステータス: 3個のアカウントを読み込みました        接続状態: オフライン    │
└─────────────────────────────────────────────────────────────────────────────┘
""")
    
    print("\n🎨 デザイン特徴:")
    print("  • 和紙白（#fefefe）ベースの落ち着いた配色")
    print("  • 薄桜色（#ffe8e8）での選択状態表示")
    print("  • 墨色（#333333）での読みやすいテキスト")
    print("  • 絵文字による直感的な状態表現")
    print("  • 余白を活かしたミニマルレイアウト")
    
    print("\n📱 操作方法:")
    print("  • 左ペイン: アカウント・フォルダをクリックで選択")
    print("  • 中央ペイン: メールをクリックで選択・ダブルクリックで詳細")
    print("  • 右ペイン: 返信・転送・削除ボタンでアクション")
    print("  • ツールバー: 新規作成・更新・アカウント追加・検索")
    print("  • メニューバー: ファイル・表示・ヘルプメニュー")
    
    print("\n🔧 技術的実装:")
    print("  • Tkinter + TTK による高品質GUI")
    print("  • PanedWindow による3ペインのリサイズ対応")
    print("  • Treeview による階層表示（アカウント・メール一覧）")
    print("  • Threading によるバックグラウンド処理")
    print("  • Style による統一されたデザインテーマ")


def demo_gui_features():
    """
    GUI機能のデモ
    """
    print("\n" + "="*60)
    print("⚙️ GUI機能実装状況デモ")
    print("="*60)
    
    features = [
        ("✅", "3ペインレイアウト", "左・中央・右ペインによる情報整理"),
        ("✅", "アカウント管理", "Gmail・IMAP・SMTP・POP3の統合管理"),
        ("✅", "メール一覧表示", "フラグ・送信者・件名・日時の表示"),
        ("✅", "メール本文表示", "ヘッダー・本文・添付ファイル情報"),
        ("✅", "侘び寂びデザイン", "和の美意識を取り入れた配色・レイアウト"),
        ("✅", "ツールバー", "よく使う機能へのクイックアクセス"),
        ("✅", "メニューバー", "全機能への体系的なアクセス"),
        ("✅", "ステータスバー", "現在の状態・接続状況の表示"),
        ("✅", "イベント処理", "マウス・キーボード操作への対応"),
        ("✅", "エラーハンドリング", "例外処理と状態管理"),
        ("✅", "日本語対応", "完全な日本語ローカライゼーション"),
        ("✅", "サンプルデータ", "動作確認用のデモデータ生成"),
        ("🔄", "OAuth2認証", "Google API連携（次フェーズ実装予定）"),
        ("🔄", "メール送信", "作成画面と送信処理（次フェーズ実装予定）"),
        ("🔄", "設定画面", "アカウント・外観設定（次フェーズ実装予定）")
    ]
    
    print(f"\n機能実装状況:")
    for status, feature, description in features:
        print(f"  {status} {feature:20} : {description}")
    
    print(f"\n🎯 完了率:")
    completed = sum(1 for status, _, _ in features if status == "✅")
    total = len(features)
    percentage = (completed / total) * 100
    print(f"  基本GUI機能: {completed}/{total} ({percentage:.0f}%)")
    
    print(f"\n📊 技術スタック:")
    tech_stack = [
        "Python 3.10+",
        "Tkinter (標準GUI ライブラリ)",
        "TTK (テーマ対応ウィジェット)",
        "Threading (バックグラウンド処理)",
        "Pathlib (ファイルパス操作)",
        "Dataclasses (データ構造)",
        "Enum (定数管理)",
        "Logging (ログ出力)"
    ]
    
    for tech in tech_stack:
        print(f"  • {tech}")


def main():
    """
    基本GUI実装のデモンストレーション
    """
    # ログを設定
    logger = setup_logger()
    logger.info("🌸 WabiMail 基本GUI実装デモを開始します")
    
    try:
        print("\n" + "="*60)
        print("🌸 WabiMail 基本GUI実装デモ")
        print("="*60)
        print("📱 3ペインレイアウトによる統合メールクライアント")
        print("🎨 侘び寂びデザインテーマの適用")
        print("🔧 Tkinter + TTK による高品質GUI実装")
        
        # GUIコンポーネントデモ
        demo_gui_components()
        
        # レイアウトデモ
        demo_gui_layout()
        
        # 機能デモ
        demo_gui_features()
        
        print(f"\n" + "="*60)
        print("🎯 デモのポイント")
        print("="*60)
        print("✨ 侘び寂び美学：シンプルで静かな美しさを追求")
        print("🏗️ 3ペイン設計：情報を整理して迷わない操作")
        print("🎨 和のデザイン：和紙色・薄桜色・墨色の上品な配色")
        print("📧 統合管理：複数アカウント・プロトコルの一元管理")
        print("⚡ 高品質GUI：Tkinter + TTK による美しいインターフェース")
        print("🌐 完全日本語対応：エラーメッセージ・UI全て日本語化")
        
        print(f"\n🌸 基本GUI実装完了！次はOAuth2認証機能の実装に進みます")
        print("="*60)
        
    except Exception as e:
        logger.error(f"デモ実行中にエラーが発生しました: {e}")
        print(f"❌ エラー: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()