#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
メール作成機能デモアプリケーション

Task 9: メール送信機能の動作確認用デモアプリケーション
- メール作成ウィンドウの表示・操作確認
- 返信・転送機能の動作確認
- 添付ファイル機能の動作確認
"""

import sys
import os
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.mail.account import Account, AccountType, AuthType, AccountSettings
from src.mail.mail_message import MailMessage, MailAttachment, MessageFlag
from src.ui.compose_window import show_compose_window


def create_demo_account():
    """デモ用アカウントを作成"""
    return Account(
        account_id="demo_account_001",
        name="WabiMail Demo User",
        email_address="demo@wabimail.example.com",
        account_type=AccountType.GMAIL,
        auth_type=AuthType.OAUTH2,
        settings=AccountSettings(
            incoming_server="imap.gmail.com",
            incoming_port=993,
            incoming_security="SSL",
            outgoing_server="smtp.gmail.com",
            outgoing_port=587,
            outgoing_security="STARTTLS",
            requires_auth=True
        )
    )


def create_demo_messages():
    """デモ用メッセージを作成"""
    messages = []
    
    # メッセージ1: 新機能の提案
    msg1 = MailMessage(
        subject="🌸 WabiMail 新機能のご提案",
        sender="product@wabimail.example.com",
        recipients=["demo@wabimail.example.com"],
        body_text="""WabiMail開発チームです。

いつもWabiMailをご利用いただき、ありがとうございます。

新しいメール送信機能（Task 9）が実装されました！

【新機能の特徴】
✨ 侘び寂びの美学に基づいたメール作成画面
✨ HTML/テキスト切り替え対応
✨ 添付ファイル管理機能
✨ 返信・転送の自動設定
✨ 下書き保存・自動保存
✨ リアルタイム文字数カウント

ぜひお試しいただき、ご感想をお聞かせください。

--
WabiMail Product Team
🌸 静寂の中の美しさを追求して""",
        date_received=datetime.now()
    )
    msg1.add_flag(MessageFlag.FLAGGED)
    messages.append(msg1)
    
    # メッセージ2: 技術文書（添付ファイル付き）
    msg2 = MailMessage(
        subject="メール送信機能 技術仕様書",
        sender="tech@wabimail.example.com",
        recipients=["demo@wabimail.example.com"],
        body_text="""技術チームです。

メール送信機能の技術仕様書を添付いたします。

【実装内容】
• ComposeWindowクラス - メール作成UI
• SMTP統合 - 既存SMTPクライアントとの連携
• 添付ファイル管理 - マルチパート対応
• 侘び寂びスタイル - 一貫したデザイン

ご確認のほど、よろしくお願いいたします。""",
        date_received=datetime.now()
    )
    
    # 添付ファイルを模擬
    attachment = MailAttachment(
        filename="メール送信機能仕様書.pdf",
        content_type="application/pdf",
        size=1024*256,  # 256KB
        data=b"PDF content placeholder"
    )
    msg2.attachments.append(attachment)
    messages.append(msg2)
    
    # メッセージ3: フィードバック依頼
    msg3 = MailMessage(
        subject="メール送信機能のフィードバック依頼",
        sender="qa@wabimail.example.com",
        recipients=["demo@wabimail.example.com"],
        body_text="""QAチームです。

メール送信機能のテストが完了いたしました。

【テスト結果】
✅ 新規メール作成 - 正常動作
✅ 返信機能 - 正常動作
✅ 転送機能 - 正常動作
✅ 添付ファイル - 正常動作
✅ HTML/テキスト切り替え - 正常動作

ユーザビリティの観点から、ご意見をお聞かせください。""",
        date_received=datetime.now()
    )
    messages.append(msg3)
    
    return messages


class ComposeWindowDemo:
    """メール作成機能デモクラス"""
    
    def __init__(self):
        """デモアプリケーションを初期化"""
        self.root = tk.Tk()
        self.root.title("🌸 WabiMail メール送信機能デモ")
        self.root.geometry("600x500")
        
        # デモ用データ
        self.account = create_demo_account()
        self.messages = create_demo_messages()
        
        # UI作成
        self._create_ui()
        
        print("🌸 WabiMail メール送信機能デモ")
        print("="*50)
        print("📧 デモ内容:")
        print("• 新規メール作成")
        print("• 返信機能")
        print("• 転送機能")
        print("• 添付ファイル機能")
        print("• HTML/テキスト切り替え")
        print()
        print("✨ 各ボタンをクリックして機能をお試しください")
    
    def _create_ui(self):
        """デモUI作成"""
        # メインタイトル
        title_label = tk.Label(
            self.root,
            text="🌸 WabiMail メール送信機能デモ",
            font=("Yu Gothic UI", 16, "bold"),
            pady=20
        )
        title_label.pack()
        
        # 説明文
        desc_text = """侘び寂びの美学に基づいたメール作成体験をお試しください。
静かで美しいメール作成環境を実現しています。"""
        
        desc_label = tk.Label(
            self.root,
            text=desc_text,
            font=("Yu Gothic UI", 10),
            justify=tk.CENTER,
            pady=10
        )
        desc_label.pack()
        
        # デモアカウント情報
        account_frame = tk.LabelFrame(
            self.root,
            text="📧 デモアカウント情報",
            font=("Yu Gothic UI", 12),
            pady=10
        )
        account_frame.pack(fill=tk.X, padx=20, pady=10)
        
        account_info = f"""名前: {self.account.name}
メールアドレス: {self.account.email_address}
アカウントタイプ: {self.account.account_type.value}
認証方式: {self.account.auth_type.value}"""
        
        tk.Label(
            account_frame,
            text=account_info,
            font=("Yu Gothic UI", 9),
            justify=tk.LEFT
        ).pack(padx=10, pady=5)
        
        # 機能デモボタン
        demo_frame = tk.LabelFrame(
            self.root,
            text="🔧 機能デモ",
            font=("Yu Gothic UI", 12),
            pady=10
        )
        demo_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # 新規メール作成ボタン
        new_button = tk.Button(
            demo_frame,
            text="📮 新規メール作成",
            font=("Yu Gothic UI", 11),
            command=self._demo_new_message,
            bg="#f8f8f8",
            relief=tk.FLAT,
            pady=5
        )
        new_button.pack(fill=tk.X, padx=10, pady=5)
        
        # 返信デモボタン
        reply_button = tk.Button(
            demo_frame,
            text="↩️ 返信デモ",
            font=("Yu Gothic UI", 11),
            command=self._demo_reply,
            bg="#f8f8f8",
            relief=tk.FLAT,
            pady=5
        )
        reply_button.pack(fill=tk.X, padx=10, pady=5)
        
        # 転送デモボタン
        forward_button = tk.Button(
            demo_frame,
            text="📤 転送デモ",
            font=("Yu Gothic UI", 11),
            command=self._demo_forward,
            bg="#f8f8f8",
            relief=tk.FLAT,
            pady=5
        )
        forward_button.pack(fill=tk.X, padx=10, pady=5)
        
        # 添付ファイル付きメールボタン
        attach_button = tk.Button(
            demo_frame,
            text="📎 添付ファイル付きメール",
            font=("Yu Gothic UI", 11),
            command=self._demo_with_attachment,
            bg="#f8f8f8",
            relief=tk.FLAT,
            pady=5
        )
        attach_button.pack(fill=tk.X, padx=10, pady=5)
        
        # HTMLメールボタン
        html_button = tk.Button(
            demo_frame,
            text="📝 HTMLメール作成",
            font=("Yu Gothic UI", 11),
            command=self._demo_html_message,
            bg="#f8f8f8",
            relief=tk.FLAT,
            pady=5
        )
        html_button.pack(fill=tk.X, padx=10, pady=5)
        
        # 終了ボタン
        quit_button = tk.Button(
            self.root,
            text="❌ デモ終了",
            font=("Yu Gothic UI", 10),
            command=self.root.quit,
            bg="#ffe0e0",
            relief=tk.FLAT,
            pady=3
        )
        quit_button.pack(pady=10)
    
    def _demo_new_message(self):
        """新規メール作成デモ"""
        print("📮 新規メール作成デモを開始...")
        
        def on_sent(message):
            print(f"✅ メール送信完了: {message.subject}")
            messagebox.showinfo(
                "送信完了",
                f"デモメールが正常に作成されました！\n\n件名: {message.subject}",
                parent=self.root
            )
        
        compose_window = show_compose_window(
            parent=self.root,
            account=self.account,
            message_type="new",
            on_sent=on_sent
        )
        
        if compose_window:
            print("✨ 新規メール作成ウィンドウを表示しました")
    
    def _demo_reply(self):
        """返信デモ"""
        print("↩️ 返信デモを開始...")
        
        # 返信対象のメッセージを選択
        original_message = self.messages[0]  # 最初のメッセージに返信
        
        def on_sent(message):
            print(f"✅ 返信送信完了: {message.subject}")
            messagebox.showinfo(
                "返信完了",
                f"返信メールが正常に作成されました！\n\n件名: {message.subject}",
                parent=self.root
            )
        
        compose_window = show_compose_window(
            parent=self.root,
            account=self.account,
            message_type="reply",
            original_message=original_message,
            on_sent=on_sent
        )
        
        if compose_window:
            print(f"✨ 返信ウィンドウを表示しました: {original_message.subject}")
    
    def _demo_forward(self):
        """転送デモ"""
        print("📤 転送デモを開始...")
        
        # 転送対象のメッセージを選択（添付ファイル付き）
        original_message = self.messages[1]  # 添付ファイル付きメッセージ
        
        def on_sent(message):
            print(f"✅ 転送送信完了: {message.subject}")
            messagebox.showinfo(
                "転送完了",
                f"転送メールが正常に作成されました！\n\n"
                f"件名: {message.subject}\n"
                f"添付ファイル: {len(message.attachments)}件",
                parent=self.root
            )
        
        compose_window = show_compose_window(
            parent=self.root,
            account=self.account,
            message_type="forward",
            original_message=original_message,
            on_sent=on_sent
        )
        
        if compose_window:
            print(f"✨ 転送ウィンドウを表示しました: {original_message.subject}")
    
    def _demo_with_attachment(self):
        """添付ファイル付きメールデモ"""
        print("📎 添付ファイル付きメールデモを開始...")
        
        def on_sent(message):
            print(f"✅ 添付ファイル付きメール送信完了: {message.subject}")
            messagebox.showinfo(
                "送信完了",
                f"添付ファイル付きメールが正常に作成されました！\n\n"
                f"件名: {message.subject}\n"
                f"添付ファイル: {len(message.attachments)}件",
                parent=self.root
            )
        
        compose_window = show_compose_window(
            parent=self.root,
            account=self.account,
            message_type="new",
            on_sent=on_sent
        )
        
        if compose_window:
            # 件名と本文を事前設定
            compose_window.subject_entry.insert(0, "📎 添付ファイルのテスト")
            compose_window.body_text.insert(tk.END, """添付ファイル機能のテストです。

「📎 添付」ボタンをクリックしてファイルを添付してみてください。

• 画像ファイル（JPG, PNG）
• 文書ファイル（PDF, Word）
• その他のファイル

添付後は、ファイル名の横の「❌」ボタンで削除できます。""")
            
            print("✨ 添付ファイル付きメール作成ウィンドウを表示しました")
            print("💡 「📎 添付」ボタンでファイルを添付できます")
    
    def _demo_html_message(self):
        """HTMLメールデモ"""
        print("📝 HTMLメールデモを開始...")
        
        def on_sent(message):
            print(f"✅ HTMLメール送信完了: {message.subject}")
            messagebox.showinfo(
                "送信完了",
                f"HTMLメールが正常に作成されました！\n\n件名: {message.subject}",
                parent=self.root
            )
        
        compose_window = show_compose_window(
            parent=self.root,
            account=self.account,
            message_type="new",
            on_sent=on_sent
        )
        
        if compose_window:
            # HTML編集モードに切り替え
            compose_window.is_html_mode.set(True)
            compose_window._toggle_html_mode()
            
            # 件名を設定
            compose_window.subject_entry.insert(0, "📝 HTML形式のメール")
            
            # サンプルHTMLを設定
            sample_html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {
            font-family: 'Yu Gothic UI', sans-serif;
            line-height: 1.6;
            color: #333;
            background: #fefefe;
            margin: 16px;
        }
        h1 { color: #8b7355; }
        .highlight { background-color: #f0f8ff; padding: 8px; }
        .signature { font-style: italic; color: #666; margin-top: 20px; }
    </style>
</head>
<body>
    <h1>🌸 WabiMail HTML メール</h1>
    
    <p>これは<strong>HTML形式</strong>のメールです。</p>
    
    <div class="highlight">
        <p>侘び寂びの美学に基づいた、美しいHTMLメールを作成できます。</p>
    </div>
    
    <p>機能:</p>
    <ul>
        <li>リッチテキスト編集</li>
        <li>カスタムスタイル</li>
        <li>美しいレイアウト</li>
    </ul>
    
    <div class="signature">
        🌸 静寂の中の美しさを追求して<br>
        WabiMail Development Team
    </div>
</body>
</html>"""
            
            compose_window.html_editor.insert(tk.END, sample_html)
            
            print("✨ HTMLメール作成ウィンドウを表示しました")
            print("💡 「📝 HTML編集」がチェックされています")
    
    def run(self):
        """デモアプリケーションを実行"""
        try:
            self.root.mainloop()
            print("\n🌸 デモを終了しました。ありがとうございました！")
        except KeyboardInterrupt:
            print("\n🌸 デモを中断しました")
        except Exception as e:
            print(f"\n❌ デモ実行エラー: {e}")


def main():
    """メイン関数"""
    try:
        # デモアプリケーションを作成・実行
        demo = ComposeWindowDemo()
        demo.run()
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()