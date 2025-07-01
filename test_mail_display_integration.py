#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
メール表示機能統合テスト

Task 8: メール表示機能の統合動作確認
- MailListとMailViewerコンポーネントの統合
- MainWindowでの表示機能確認
"""

import sys
import os
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import tkinter as tk
from datetime import datetime
from src.mail.mail_message import MailMessage, MessageFlag
from src.ui.mail_list import MailList
from src.ui.mail_viewer import MailViewer


def create_sample_messages():
    """サンプルメッセージを作成"""
    messages = []
    
    # メッセージ1: 未読・重要
    msg1 = MailMessage(
        subject="🌸 WabiMail Task 8 完了報告",
        sender="dev-team@wabimail.example.com",
        recipients=["user@example.com"],
        body_text="""WabiMail開発チームです。

Task 8「メール表示機能」の実装が完了いたしました。

【実装された機能】
✅ MailListコンポーネント - 高度なメールリスト表示
✅ MailViewerコンポーネント - リッチなメール本文表示
✅ MainWindow統合 - シームレスな連携動作

【技術特徴】
• 侘び寂びの美学に基づいたUI設計
• 高速な仮想スクロール対応
• 豊富なソート・フィルタリング機能
• HTML/テキスト対応メール表示
• 添付ファイル管理
• ズーム・印刷対応

次はTask 9「メール送信機能」の実装に進みます。

--
WabiMail開発チーム
🌸 静寂の中の美しさを追求して""",
        date_received=datetime.now()
    )
    msg1.add_flag(MessageFlag.FLAGGED)
    messages.append(msg1)
    
    # メッセージ2: 既読・添付ファイルあり
    msg2 = MailMessage(
        subject="技術仕様書 - メール表示コンポーネント",
        sender="architect@wabimail.example.com",
        recipients=["dev-team@wabimail.example.com"],
        body_text="""添付の技術仕様書をご確認ください。

メール表示機能の詳細なアーキテクチャと
実装方針を記載しています。""",
        date_received=datetime.now()
    )
    msg2.mark_as_read()
    # 模擬的な添付ファイル情報を追加
    from src.mail.mail_message import MailAttachment
    attachment = MailAttachment(
        filename="mail_display_spec.pdf",
        content_type="application/pdf",
        size=1024*512  # 512KB
    )
    msg2.attachments.append(attachment)
    messages.append(msg2)
    
    # メッセージ3: 未読
    msg3 = MailMessage(
        subject="コードレビュー依頼",
        sender="reviewer@wabimail.example.com", 
        recipients=["dev-team@wabimail.example.com"],
        body_text="""メール表示機能のコードレビューをお願いします。

特に以下の点をご確認ください：
• UIコンポーネントの設計
• パフォーマンス最適化
• エラーハンドリング
• テストカバレッジ

宜しくお願いいたします。""",
        date_received=datetime.now()
    )
    messages.append(msg3)
    
    return messages


def main():
    """メール表示統合テスト実行"""
    print("🌸 WabiMail メール表示機能統合テスト")
    print("="*50)
    
    try:
        # Tkinterルートウィンドウ作成
        root = tk.Tk()
        root.title("🌸 メール表示機能テスト - WabiMail")
        root.geometry("1000x700")
        
        # メインフレーム作成
        main_frame = tk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左側: メールリスト
        list_frame = tk.Frame(main_frame)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 選択変更時のコールバック
        def on_selection_change(selected_messages):
            if selected_messages:
                viewer.display_message(selected_messages[0])
                print(f"✅ メッセージ選択: {selected_messages[0].subject}")
            else:
                viewer.display_message(None)
        
        # ダブルクリック時のコールバック
        def on_double_click(message):
            print(f"📧 ダブルクリック: {message.subject}")
        
        # コンテキストメニュー時のコールバック  
        def on_context_menu(action, data):
            print(f"🔧 コンテキストメニュー: {action}")
        
        # MailListコンポーネント作成
        mail_list = MailList(
            list_frame,
            on_selection_change=on_selection_change,
            on_double_click=on_double_click,
            on_context_menu=on_context_menu
        )
        mail_list.pack(fill=tk.BOTH, expand=True)
        
        # 右側: メール表示
        view_frame = tk.Frame(main_frame)
        view_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 返信・転送・削除コールバック
        def on_reply(message):
            print(f"📮 返信: {message.subject if message else 'None'}")
        
        def on_forward(message):
            print(f"📤 転送: {message.subject if message else 'None'}")
        
        def on_delete(message):
            print(f"🗑️ 削除: {message.subject if message else 'None'}")
        
        # MailViewerコンポーネント作成
        viewer = MailViewer(
            view_frame,
            on_reply=on_reply,
            on_forward=on_forward,
            on_delete=on_delete
        )
        viewer.pack(fill=tk.BOTH, expand=True)
        
        # サンプルメッセージを設定
        print("📧 サンプルメッセージを読み込み中...")
        messages = create_sample_messages()
        mail_list.set_messages(messages, "受信トレイ")
        
        print(f"✅ {len(messages)}件のメッセージを読み込みました")
        print()
        print("🔧 操作方法:")
        print("• メールリストでメッセージをクリックして表示")
        print("• ダブルクリックでアクション実行")
        print("• 右クリックでコンテキストメニュー")
        print("• メール表示エリアでズーム・スクロール")
        print()
        print("✨ 侘び寂びの美しさをお楽しみください")
        
        # メインループ開始
        root.mainloop()
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()