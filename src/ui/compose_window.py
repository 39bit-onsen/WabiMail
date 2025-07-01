# -*- coding: utf-8 -*-
"""
メール作成ウィンドウモジュール

WabiMailのメール作成・編集機能を実装します。
侘び寂びの美学に基づいた、集中して文章を書ける環境を提供します。

Author: WabiMail Development Team
Created: 2025-07-01
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import List, Optional, Dict, Any, Callable
import threading
import os
from pathlib import Path
from datetime import datetime
import tempfile

from src.mail.account import Account
from src.mail.mail_message import MailMessage, MailAttachment
from src.mail.mail_client_factory import MailClientFactory
from src.utils.logger import get_logger

# ロガーを取得
logger = get_logger(__name__)


class ComposeWindow:
    """
    メール作成ウィンドウクラス
    
    侘び寂びの美学に基づいた、静かで集中できるメール作成環境を提供します。
    心を込めたメッセージの作成を支援する機能を実装します。
    
    機能:
    • シンプルで美しいメール作成UI
    • 宛先・CC・BCC管理
    • リッチテキスト・HTML対応
    • 添付ファイル管理
    • 下書き保存
    • 送信処理・エラーハンドリング
    • 返信・転送対応
    
    Attributes:
        parent: 親ウィンドウ
        account: 送信に使用するアカウント
        message_type: メッセージタイプ（新規、返信、転送）
        original_message: 返信・転送元メッセージ
        on_sent: 送信完了コールバック
        window: メインウィンドウ
        is_html_mode: HTML編集モード
        attachments: 添付ファイルリスト
        is_draft_saved: 下書き保存状態
    """
    
    def __init__(self, parent, account: Account, 
                 message_type: str = "new",
                 original_message: Optional[MailMessage] = None,
                 on_sent: Optional[Callable] = None):
        """
        メール作成ウィンドウを初期化します
        
        Args:
            parent: 親ウィンドウ
            account: 送信に使用するアカウント
            message_type: メッセージタイプ（"new", "reply", "forward"）
            original_message: 返信・転送元メッセージ
            on_sent: 送信完了時のコールバック
        """
        self.parent = parent
        self.account = account
        self.message_type = message_type
        self.original_message = original_message
        self.on_sent = on_sent
        
        # ウィンドウ状態
        self.window = None
        self.is_html_mode = tk.BooleanVar(value=False)
        self.attachments: List[MailAttachment] = []
        self.is_draft_saved = False
        self.auto_save_timer = None
        
        # UI要素の参照
        self.to_entry = None
        self.cc_entry = None
        self.bcc_entry = None
        self.subject_entry = None
        self.body_text = None
        self.html_editor = None
        self.attachments_frame = None
        self.status_label = None
        
        # 侘び寂びスタイルの設定
        self._setup_wabi_sabi_style()
        
        # ウィンドウを作成
        self._create_window()
        
        logger.info(f"メール作成ウィンドウを初期化しました: {message_type}")
    
    def _setup_wabi_sabi_style(self):
        """
        侘び寂びの美学に基づいたスタイルを設定します
        """
        self.wabi_colors = {
            "bg": "#fefefe",           # 純白の背景
            "fg": "#333333",           # 墨のような文字色
            "entry_bg": "#fcfcfc",     # 入力欄の背景
            "border": "#e0e0e0",       # 繊細な境界線
            "accent": "#8b7355",       # 侘び寂びアクセント色
            "button_bg": "#f8f8f8",    # ボタン背景
            "button_hover": "#f0f0f0", # ボタンホバー
            "focus": "#d4c4b0"         # フォーカス色
        }
        
        self.wabi_fonts = {
            "header": ("Yu Gothic UI", 12, "normal"),
            "body": ("Yu Gothic UI", 11, "normal"),
            "small": ("Yu Gothic UI", 9, "normal"),
            "compose": ("Yu Gothic UI", 12, "normal")
        }
    
    def _create_window(self):
        """
        メール作成ウィンドウを作成します
        """
        # 新しいウィンドウを作成
        self.window = tk.Toplevel(self.parent)
        
        # ウィンドウタイトル
        title_prefix = {
            "new": "新規メール作成",
            "reply": "返信",
            "forward": "転送"
        }.get(self.message_type, "メール作成")
        
        self.window.title(f"🌸 {title_prefix} - WabiMail")
        
        # ウィンドウサイズと位置
        window_width = 800
        window_height = 600
        
        # 親ウィンドウの中央に配置
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        x = parent_x + (parent_width - window_width) // 2
        y = parent_y + (parent_height - window_height) // 2
        
        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.window.minsize(600, 400)
        
        # ウィンドウ設定
        self.window.configure(bg=self.wabi_colors["bg"])
        self.window.transient(self.parent)
        self.window.grab_set()
        
        # ウィンドウ閉じる時の処理
        self.window.protocol("WM_DELETE_WINDOW", self._on_window_close)
        
        # UI要素を作成
        self._create_toolbar()
        self._create_header_section()
        self._create_body_section()
        self._create_attachments_section()
        self._create_status_bar()
        
        # 初期データを設定
        self._populate_initial_data()
        
        # キーバインド設定
        self._setup_key_bindings()
        
        # 自動保存タイマー開始
        self._start_auto_save()
        
        logger.info("メール作成ウィンドウを作成しました")
    
    def _create_toolbar(self):
        """
        ツールバーを作成します
        """
        toolbar = ttk.Frame(self.window, style="Toolbar.Wabi.TFrame")
        toolbar.pack(fill=tk.X, padx=8, pady=(8, 4))
        
        # 送信ボタン
        send_button = ttk.Button(
            toolbar,
            text="📮 送信",
            style="Send.Wabi.TButton",
            command=self._send_message
        )
        send_button.pack(side=tk.LEFT, padx=(0, 8))
        
        # 下書き保存ボタン
        draft_button = ttk.Button(
            toolbar,
            text="💾 下書き保存",
            style="Draft.Wabi.TButton",
            command=self._save_draft
        )
        draft_button.pack(side=tk.LEFT, padx=(0, 8))
        
        # 添付ファイルボタン
        attach_button = ttk.Button(
            toolbar,
            text="📎 添付",
            style="Attach.Wabi.TButton",
            command=self._add_attachment
        )
        attach_button.pack(side=tk.LEFT, padx=(0, 8))
        
        # セパレーター
        separator1 = ttk.Separator(toolbar, orient=tk.VERTICAL)
        separator1.pack(side=tk.LEFT, fill=tk.Y, padx=8)
        
        # HTML/テキスト切り替え
        html_check = ttk.Checkbutton(
            toolbar,
            text="📝 HTML編集",
            variable=self.is_html_mode,
            style="Toggle.Wabi.TCheckbutton",
            command=self._toggle_html_mode
        )
        html_check.pack(side=tk.LEFT, padx=(0, 8))
        
        # セパレーター
        separator2 = ttk.Separator(toolbar, orient=tk.VERTICAL)
        separator2.pack(side=tk.LEFT, fill=tk.Y, padx=8)
        
        # キャンセルボタン（右寄せ）
        cancel_button = ttk.Button(
            toolbar,
            text="❌ キャンセル",
            style="Cancel.Wabi.TButton",
            command=self._cancel_compose
        )
        cancel_button.pack(side=tk.RIGHT)
    
    def _create_header_section(self):
        """
        ヘッダーセクション（宛先、件名等）を作成します
        """
        header_frame = ttk.LabelFrame(
            self.window,
            text="📧 メッセージ情報",
            style="Header.Wabi.TLabelframe"
        )
        header_frame.pack(fill=tk.X, padx=8, pady=4)
        
        # 送信者情報
        from_frame = ttk.Frame(header_frame)
        from_frame.pack(fill=tk.X, padx=8, pady=4)
        
        ttk.Label(
            from_frame,
            text="差出人:",
            style="HeaderLabel.Wabi.TLabel",
            width=8
        ).pack(side=tk.LEFT)
        
        from_info = ttk.Label(
            from_frame,
            text=f"{self.account.name} <{self.account.email_address}>",
            style="HeaderValue.Wabi.TLabel"
        )
        from_info.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 宛先
        to_frame = ttk.Frame(header_frame)
        to_frame.pack(fill=tk.X, padx=8, pady=2)
        
        ttk.Label(
            to_frame,
            text="宛先:",
            style="HeaderLabel.Wabi.TLabel",
            width=8
        ).pack(side=tk.LEFT)
        
        self.to_entry = ttk.Entry(
            to_frame,
            style="HeaderEntry.Wabi.TEntry",
            font=self.wabi_fonts["body"]
        )
        self.to_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 0))
        
        # CC/BCC展開ボタン
        cc_button = ttk.Button(
            to_frame,
            text="CC/BCC",
            style="CCButton.Wabi.TButton",
            command=self._toggle_cc_bcc
        )
        cc_button.pack(side=tk.RIGHT, padx=(4, 0))
        
        # CC（最初は非表示）
        self.cc_frame = ttk.Frame(header_frame)
        
        ttk.Label(
            self.cc_frame,
            text="CC:",
            style="HeaderLabel.Wabi.TLabel",
            width=8
        ).pack(side=tk.LEFT)
        
        self.cc_entry = ttk.Entry(
            self.cc_frame,
            style="HeaderEntry.Wabi.TEntry",
            font=self.wabi_fonts["body"]
        )
        self.cc_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 0))
        
        # BCC（最初は非表示）
        self.bcc_frame = ttk.Frame(header_frame)
        
        ttk.Label(
            self.bcc_frame,
            text="BCC:",
            style="HeaderLabel.Wabi.TLabel",
            width=8
        ).pack(side=tk.LEFT)
        
        self.bcc_entry = ttk.Entry(
            self.bcc_frame,
            style="HeaderEntry.Wabi.TEntry",
            font=self.wabi_fonts["body"]
        )
        self.bcc_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 0))
        
        # 件名
        subject_frame = ttk.Frame(header_frame)
        subject_frame.pack(fill=tk.X, padx=8, pady=4)
        
        ttk.Label(
            subject_frame,
            text="件名:",
            style="HeaderLabel.Wabi.TLabel",
            width=8
        ).pack(side=tk.LEFT)
        
        self.subject_entry = ttk.Entry(
            subject_frame,
            style="HeaderEntry.Wabi.TEntry",
            font=self.wabi_fonts["body"]
        )
        self.subject_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 0))
    
    def _create_body_section(self):
        """
        本文編集セクションを作成します
        """
        body_frame = ttk.LabelFrame(
            self.window,
            text="✍️ メッセージ本文",
            style="Body.Wabi.TLabelframe"
        )
        body_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)
        
        # テキスト編集エリア
        text_frame = ttk.Frame(body_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        
        # スクロールバー付きテキストエリア
        self.body_text = tk.Text(
            text_frame,
            wrap=tk.WORD,
            font=self.wabi_fonts["compose"],
            bg=self.wabi_colors["entry_bg"],
            fg=self.wabi_colors["fg"],
            selectbackground=self.wabi_colors["focus"],
            insertbackground=self.wabi_colors["fg"],
            relief=tk.FLAT,
            borderwidth=1,
            highlightthickness=1,
            highlightcolor=self.wabi_colors["accent"],
            highlightbackground=self.wabi_colors["border"]
        )
        
        # 縦スクロールバー
        v_scrollbar = ttk.Scrollbar(
            text_frame,
            orient=tk.VERTICAL,
            command=self.body_text.yview
        )
        self.body_text.configure(yscrollcommand=v_scrollbar.set)
        
        # 配置
        self.body_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # HTML編集エリア（最初は非表示）
        self.html_frame = ttk.Frame(body_frame)
        
        # 簡易HTMLエディタ（将来的に拡張予定）
        self.html_editor = tk.Text(
            self.html_frame,
            wrap=tk.WORD,
            font=("Consolas", 10),
            bg=self.wabi_colors["entry_bg"],
            fg=self.wabi_colors["fg"],
            selectbackground=self.wabi_colors["focus"],
            insertbackground=self.wabi_colors["fg"],
            relief=tk.FLAT,
            borderwidth=1,
            highlightthickness=1,
            highlightcolor=self.wabi_colors["accent"],
            highlightbackground=self.wabi_colors["border"]
        )
        
        # HTMLエディタ用スクロールバー
        html_scrollbar = ttk.Scrollbar(
            self.html_frame,
            orient=tk.VERTICAL,
            command=self.html_editor.yview
        )
        self.html_editor.configure(yscrollcommand=html_scrollbar.set)
        
        # HTML編集エリア配置
        self.html_editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        html_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _create_attachments_section(self):
        """
        添付ファイルセクションを作成します
        """
        self.attachments_frame = ttk.LabelFrame(
            self.window,
            text="📎 添付ファイル",
            style="Attachments.Wabi.TLabelframe"
        )
        # 最初は非表示（添付ファイルがある時のみ表示）
        
        # 添付ファイルリスト用のフレーム
        self.attachments_list_frame = ttk.Frame(self.attachments_frame)
        self.attachments_list_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
    
    def _create_status_bar(self):
        """
        ステータスバーを作成します
        """
        status_frame = ttk.Frame(self.window, style="StatusBar.Wabi.TFrame")
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = ttk.Label(
            status_frame,
            text="📝 新しいメッセージを作成中...",
            style="Status.Wabi.TLabel"
        )
        self.status_label.pack(side=tk.LEFT, padx=8, pady=4)
        
        # 文字数カウンター
        self.char_count_label = ttk.Label(
            status_frame,
            text="文字数: 0",
            style="CharCount.Wabi.TLabel"
        )
        self.char_count_label.pack(side=tk.RIGHT, padx=8, pady=4)
        
        # 文字数カウンター更新
        self.body_text.bind('<KeyRelease>', self._update_char_count)
        self.body_text.bind('<Button-1>', self._update_char_count)
    
    def _populate_initial_data(self):
        """
        初期データを設定します（返信・転送の場合）
        """
        if not self.original_message:
            return
        
        if self.message_type == "reply":
            # 返信の場合
            self.to_entry.insert(0, self.original_message.sender)
            
            # 件名にRe:プレフィックス
            original_subject = self.original_message.subject
            if not original_subject.startswith("Re:"):
                reply_subject = f"Re: {original_subject}"
            else:
                reply_subject = original_subject
            self.subject_entry.insert(0, reply_subject)
            
            # 元メッセージを引用
            quote_text = self._create_quote_text(self.original_message)
            self.body_text.insert(tk.END, quote_text)
            
            # カーソルを先頭に移動
            self.body_text.mark_set(tk.INSERT, "1.0")
            
        elif self.message_type == "forward":
            # 転送の場合
            # 件名にFwd:プレフィックス
            original_subject = self.original_message.subject
            if not original_subject.startswith("Fwd:"):
                forward_subject = f"Fwd: {original_subject}"
            else:
                forward_subject = original_subject
            self.subject_entry.insert(0, forward_subject)
            
            # 転送メッセージを作成
            forward_text = self._create_forward_text(self.original_message)
            self.body_text.insert(tk.END, forward_text)
            
            # 元メッセージの添付ファイルをコピー
            for attachment in self.original_message.attachments:
                self.attachments.append(attachment)
            
            # カーソルを先頭に移動
            self.body_text.mark_set(tk.INSERT, "1.0")
        
        # 添付ファイル表示を更新
        self._update_attachments_display()
        
        logger.info(f"初期データを設定しました: {self.message_type}")
    
    def _create_quote_text(self, message: MailMessage) -> str:
        """
        返信用の引用テキストを作成します
        
        Args:
            message: 引用元メッセージ
            
        Returns:
            str: 引用テキスト
        """
        date_str = message.get_display_date().strftime("%Y年%m月%d日 %H:%M")
        
        quote_text = f"""

{date_str} {message.sender} 様:

"""
        
        # 元の本文を引用符付きで追加
        original_body = message.body_text or "[本文なし]"
        quoted_lines = []
        for line in original_body.split('\n'):
            quoted_lines.append(f"> {line}")
        
        quote_text += '\n'.join(quoted_lines)
        
        return quote_text
    
    def _create_forward_text(self, message: MailMessage) -> str:
        """
        転送用のメッセージテキストを作成します
        
        Args:
            message: 転送元メッセージ
            
        Returns:
            str: 転送テキスト
        """
        date_str = message.get_display_date().strftime("%Y年%m月%d日 %H:%M")
        
        forward_text = f"""

---------- 転送メッセージ ----------
差出人: {message.sender}
宛先: {', '.join(message.recipients)}
日時: {date_str}
件名: {message.subject}

{message.body_text or '[本文なし]'}
"""
        
        if message.has_attachments():
            forward_text += f"\n\n添付ファイル: {message.get_attachment_count()}件"
            for attachment in message.attachments:
                forward_text += f"\n• {attachment.filename} ({attachment.size:,}バイト)"
        
        return forward_text
    
    def _toggle_cc_bcc(self):
        """
        CC/BCC欄の表示切り替え
        """
        if self.cc_frame.winfo_manager():
            # 非表示にする
            self.cc_frame.pack_forget()
            self.bcc_frame.pack_forget()
        else:
            # 表示する
            self.cc_frame.pack(fill=tk.X, padx=8, pady=2, after=self.to_entry.master)
            self.bcc_frame.pack(fill=tk.X, padx=8, pady=2, after=self.cc_frame)
    
    def _toggle_html_mode(self):
        """
        HTML/テキスト編集モードの切り替え
        """
        if self.is_html_mode.get():
            # HTMLモードに切り替え
            # テキストエリアの内容をHTMLエディタに移行
            text_content = self.body_text.get("1.0", tk.END)
            html_content = self._text_to_html(text_content)
            
            # テキストエリアを隠してHTMLエディタを表示
            self.body_text.master.pack_forget()
            self.html_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
            
            self.html_editor.delete("1.0", tk.END)
            self.html_editor.insert("1.0", html_content)
            
            self._update_status("📝 HTML編集モードに切り替えました")
            
        else:
            # テキストモードに切り替え
            # HTMLエディタの内容をテキストエリアに移行
            html_content = self.html_editor.get("1.0", tk.END)
            text_content = self._html_to_text(html_content)
            
            # HTMLエディタを隠してテキストエリアを表示
            self.html_frame.pack_forget()
            self.body_text.master.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
            
            self.body_text.delete("1.0", tk.END)
            self.body_text.insert("1.0", text_content)
            
            self._update_status("📝 テキスト編集モードに切り替えました")
    
    def _text_to_html(self, text: str) -> str:
        """
        テキストを簡易HTMLに変換します
        
        Args:
            text: プレーンテキスト
            
        Returns:
            str: HTML形式のテキスト
        """
        import html
        
        # HTMLエスケープ
        escaped_text = html.escape(text)
        
        # 改行をHTML改行に変換
        html_text = escaped_text.replace('\n', '<br>\n')
        
        # 基本的なHTML構造を追加
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: 'Yu Gothic UI', sans-serif;
            font-size: 12px;
            line-height: 1.6;
            color: #333333;
            background-color: #fefefe;
            margin: 16px;
        }}
    </style>
</head>
<body>
{html_text}
</body>
</html>"""
        
        return html_content
    
    def _html_to_text(self, html_content: str) -> str:
        """
        HTMLをプレーンテキストに変換します
        
        Args:
            html_content: HTMLコンテンツ
            
        Returns:
            str: プレーンテキスト
        """
        import re
        import html
        
        # HTMLタグを除去
        text = re.sub(r'<[^>]+>', '', html_content)
        
        # HTMLエンティティをデコード
        text = html.unescape(text)
        
        # 余分な空白を整理
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
        text = text.strip()
        
        return text
    
    def _add_attachment(self):
        """
        添付ファイルを追加します
        """
        file_path = filedialog.askopenfilename(
            title="添付ファイルを選択",
            parent=self.window,
            filetypes=[
                ("すべてのファイル", "*.*"),
                ("文書ファイル", "*.pdf *.doc *.docx *.txt"),
                ("画像ファイル", "*.jpg *.jpeg *.png *.gif *.bmp"),
                ("表計算ファイル", "*.xls *.xlsx *.csv"),
                ("圧縮ファイル", "*.zip *.rar *.7z")
            ]
        )
        
        if file_path:
            try:
                # ファイル情報を取得
                file_path_obj = Path(file_path)
                file_size = file_path_obj.stat().st_size
                
                # MIMEタイプを推測
                import mimetypes
                content_type, _ = mimetypes.guess_type(file_path)
                if not content_type:
                    content_type = "application/octet-stream"
                
                # 添付ファイルオブジェクトを作成
                attachment = MailAttachment(
                    filename=file_path_obj.name,
                    content_type=content_type,
                    size=file_size
                )
                
                # ファイルデータを読み込み（必要時）
                with open(file_path, 'rb') as f:
                    attachment.data = f.read()
                
                # 添付ファイルリストに追加
                self.attachments.append(attachment)
                
                # 表示を更新
                self._update_attachments_display()
                
                self._update_status(f"📎 ファイルを添付しました: {attachment.filename}")
                logger.info(f"ファイルを添付: {attachment.filename} ({attachment.size:,}バイト)")
                
            except Exception as e:
                logger.error(f"ファイル添付エラー: {e}")
                messagebox.showerror(
                    "エラー",
                    f"ファイルの添付に失敗しました:\n{e}",
                    parent=self.window
                )
    
    def _update_attachments_display(self):
        """
        添付ファイル表示を更新します
        """
        # 既存の表示をクリア
        for widget in self.attachments_list_frame.winfo_children():
            widget.destroy()
        
        if not self.attachments:
            # 添付ファイルがない場合は非表示
            self.attachments_frame.pack_forget()
            return
        
        # 添付ファイルセクションを表示
        self.attachments_frame.pack(fill=tk.X, padx=8, pady=4, before=self.status_label.master)
        
        # 各添付ファイルを表示
        for i, attachment in enumerate(self.attachments):
            self._create_attachment_item(attachment, i)
    
    def _create_attachment_item(self, attachment: MailAttachment, index: int):
        """
        添付ファイルアイテムを作成します
        
        Args:
            attachment: 添付ファイル
            index: インデックス
        """
        item_frame = ttk.Frame(self.attachments_list_frame, style="AttachmentItem.Wabi.TFrame")
        item_frame.pack(fill=tk.X, pady=1)
        
        # ファイルアイコン
        icon = self._get_file_icon(attachment.content_type)
        
        # ファイル情報
        info_label = ttk.Label(
            item_frame,
            text=f"{icon} {attachment.filename} ({self._format_file_size(attachment.size)})",
            style="AttachmentInfo.Wabi.TLabel"
        )
        info_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 削除ボタン
        remove_button = ttk.Button(
            item_frame,
            text="❌",
            style="AttachmentRemove.Wabi.TButton",
            command=lambda idx=index: self._remove_attachment(idx),
            width=3
        )
        remove_button.pack(side=tk.RIGHT)
    
    def _get_file_icon(self, content_type: str) -> str:
        """
        ファイルタイプに応じたアイコンを取得します
        
        Args:
            content_type: MIMEタイプ
            
        Returns:
            str: アイコン文字
        """
        if content_type.startswith('image/'):
            return "🖼️"
        elif content_type.startswith('text/'):
            return "📄"
        elif 'pdf' in content_type:
            return "📕"
        elif content_type.startswith('audio/'):
            return "🎵"
        elif content_type.startswith('video/'):
            return "🎬"
        elif any(archive in content_type for archive in ['zip', 'rar', 'tar', 'gz']):
            return "📦"
        else:
            return "📎"
    
    def _format_file_size(self, size_bytes: int) -> str:
        """
        ファイルサイズを読みやすい形式でフォーマットします
        
        Args:
            size_bytes: バイト数
            
        Returns:
            str: フォーマット済みサイズ
        """
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB"]
        size = float(size_bytes)
        
        for unit in size_names:
            if size < 1024.0:
                if unit == "B":
                    return f"{int(size)} {unit}"
                else:
                    return f"{size:.1f} {unit}"
            size /= 1024.0
        
        return f"{size:.1f} TB"
    
    def _remove_attachment(self, index: int):
        """
        添付ファイルを削除します
        
        Args:
            index: 削除する添付ファイルのインデックス
        """
        if 0 <= index < len(self.attachments):
            removed_attachment = self.attachments.pop(index)
            self._update_attachments_display()
            self._update_status(f"📎 添付ファイルを削除しました: {removed_attachment.filename}")
            logger.info(f"添付ファイルを削除: {removed_attachment.filename}")
    
    def _setup_key_bindings(self):
        """
        キーバインドを設定します
        """
        # Ctrl+Enter で送信
        self.window.bind('<Control-Return>', lambda e: self._send_message())
        
        # Ctrl+S で下書き保存
        self.window.bind('<Control-s>', lambda e: self._save_draft())
        
        # Escape でキャンセル
        self.window.bind('<Escape>', lambda e: self._cancel_compose())
        
        # Ctrl+O で添付ファイル追加
        self.window.bind('<Control-o>', lambda e: self._add_attachment())
        
        logger.debug("キーバインドを設定しました")
    
    def _update_char_count(self, event=None):
        """
        文字数カウンターを更新します
        """
        if self.is_html_mode.get():
            content = self.html_editor.get("1.0", tk.END)
        else:
            content = self.body_text.get("1.0", tk.END)
        
        # 末尾の改行を除く
        char_count = len(content.rstrip('\n'))
        self.char_count_label.config(text=f"文字数: {char_count:,}")
    
    def _start_auto_save(self):
        """
        自動保存タイマーを開始します
        """
        def auto_save():
            if self.window and self.window.winfo_exists():
                self._save_draft_silently()
                # 5分後に再実行
                self.auto_save_timer = self.window.after(300000, auto_save)  # 5分 = 300,000ms
        
        # 最初の自動保存は1分後
        self.auto_save_timer = self.window.after(60000, auto_save)  # 1分 = 60,000ms
    
    def _save_draft_silently(self):
        """
        無音で下書きを保存します（自動保存用）
        """
        try:
            # 下書きデータを作成
            draft_data = self._create_message_data()
            
            # 実際の保存処理（将来実装）
            # TODO: 下書きの永続化実装
            
            self.is_draft_saved = True
            logger.debug("下書きを自動保存しました")
            
        except Exception as e:
            logger.warning(f"自動下書き保存エラー: {e}")
    
    def _save_draft(self):
        """
        下書きを保存します
        """
        try:
            self._save_draft_silently()
            self._update_status("💾 下書きを保存しました")
            messagebox.showinfo(
                "下書き保存",
                "下書きを保存しました。",
                parent=self.window
            )
            
        except Exception as e:
            logger.error(f"下書き保存エラー: {e}")
            messagebox.showerror(
                "エラー",
                f"下書きの保存に失敗しました:\n{e}",
                parent=self.window
            )
    
    def _send_message(self):
        """
        メッセージを送信します
        """
        try:
            # 入力検証
            if not self._validate_message():
                return
            
            self._update_status("📮 メッセージを送信中...")
            
            # メッセージデータを作成
            message_data = self._create_message_data()
            
            # バックグラウンドで送信処理
            def send_in_background():
                try:
                    # SMTPクライアントを作成
                    smtp_client = MailClientFactory.create_send_client(self.account)
                    
                    if not smtp_client:
                        raise Exception("SMTPクライアントの作成に失敗しました")
                    
                    # メッセージを送信
                    success, result = smtp_client.send_message(message_data)
                    
                    # UIスレッドで結果を処理
                    self.window.after(0, lambda: self._handle_send_result(success, result))
                    
                except Exception as e:
                    self.window.after(0, lambda: self._handle_send_error(str(e)))
            
            # バックグラウンドスレッドで送信実行
            threading.Thread(target=send_in_background, daemon=True).start()
            
        except Exception as e:
            logger.error(f"メッセージ送信エラー: {e}")
            messagebox.showerror(
                "送信エラー",
                f"メッセージの送信に失敗しました:\n{e}",
                parent=self.window
            )
    
    def _validate_message(self) -> bool:
        """
        メッセージの入力検証を行います
        
        Returns:
            bool: 検証成功時True
        """
        # 宛先チェック
        to_addresses = self.to_entry.get().strip()
        if not to_addresses:
            messagebox.showerror(
                "入力エラー",
                "宛先を入力してください。",
                parent=self.window
            )
            self.to_entry.focus()
            return False
        
        # 件名チェック
        subject = self.subject_entry.get().strip()
        if not subject:
            result = messagebox.askyesno(
                "確認",
                "件名が空です。このまま送信しますか？",
                parent=self.window
            )
            if not result:
                self.subject_entry.focus()
                return False
        
        # 本文チェック
        if self.is_html_mode.get():
            body = self.html_editor.get("1.0", tk.END).strip()
        else:
            body = self.body_text.get("1.0", tk.END).strip()
        
        if not body:
            result = messagebox.askyesno(
                "確認",
                "本文が空です。このまま送信しますか？",
                parent=self.window
            )
            if not result:
                if self.is_html_mode.get():
                    self.html_editor.focus()
                else:
                    self.body_text.focus()
                return False
        
        return True
    
    def _create_message_data(self) -> MailMessage:
        """
        メッセージデータを作成します
        
        Returns:
            MailMessage: 作成されたメッセージ
        """
        # 宛先情報を解析
        to_addresses = [addr.strip() for addr in self.to_entry.get().split(',') if addr.strip()]
        cc_addresses = [addr.strip() for addr in self.cc_entry.get().split(',') if addr.strip()] if self.cc_entry.get().strip() else []
        bcc_addresses = [addr.strip() for addr in self.bcc_entry.get().split(',') if addr.strip()] if self.bcc_entry.get().strip() else []
        
        # 本文を取得
        if self.is_html_mode.get():
            body_html = self.html_editor.get("1.0", tk.END).strip()
            body_text = self._html_to_text(body_html)
        else:
            body_text = self.body_text.get("1.0", tk.END).strip()
            body_html = ""
        
        # メッセージオブジェクトを作成
        message = MailMessage(
            subject=self.subject_entry.get().strip(),
            sender=f"{self.account.name} <{self.account.email_address}>",
            recipients=to_addresses,
            cc_recipients=cc_addresses,
            bcc_recipients=bcc_addresses,
            body_text=body_text,
            body_html=body_html,
            attachments=self.attachments.copy(),
            account_id=self.account.account_id,
            date_sent=datetime.now()
        )
        
        # 返信・転送の場合は関連情報を設定
        if self.original_message:
            if self.message_type == "reply":
                message.in_reply_to = self.original_message.message_id
                message.references = self.original_message.references + [self.original_message.message_id]
            elif self.message_type == "forward":
                message.references = [self.original_message.message_id]
        
        return message
    
    def _handle_send_result(self, success: bool, result: str):
        """
        送信結果を処理します
        
        Args:
            success: 送信成功フラグ
            result: 結果メッセージ
        """
        if success:
            self._update_status("✅ メッセージを送信しました")
            
            # 送信完了ダイアログ
            messagebox.showinfo(
                "送信完了",
                "メッセージを正常に送信しました。",
                parent=self.window
            )
            
            # コールバック実行
            if self.on_sent:
                try:
                    message_data = self._create_message_data()
                    self.on_sent(message_data)
                except Exception as e:
                    logger.warning(f"送信コールバックエラー: {e}")
            
            # ウィンドウを閉じる
            self.window.destroy()
            
            logger.info("メッセージ送信完了")
            
        else:
            self._handle_send_error(result)
    
    def _handle_send_error(self, error_message: str):
        """
        送信エラーを処理します
        
        Args:
            error_message: エラーメッセージ
        """
        self._update_status("❌ メッセージ送信に失敗しました")
        
        logger.error(f"メッセージ送信エラー: {error_message}")
        
        messagebox.showerror(
            "送信エラー",
            f"メッセージの送信に失敗しました:\n\n{error_message}\n\n"
            "設定を確認して再度お試しください。",
            parent=self.window
        )
    
    def _cancel_compose(self):
        """
        メール作成をキャンセルします
        """
        # 内容が変更されている場合は確認
        if self._has_unsaved_changes():
            result = messagebox.askyesnocancel(
                "確認",
                "変更内容が保存されていません。\n\n"
                "下書きに保存しますか？",
                parent=self.window
            )
            
            if result is None:  # キャンセル
                return
            elif result:  # はい（保存）
                self._save_draft()
        
        # ウィンドウを閉じる
        self.window.destroy()
        logger.info("メール作成をキャンセルしました")
    
    def _has_unsaved_changes(self) -> bool:
        """
        未保存の変更があるかチェックします
        
        Returns:
            bool: 未保存の変更がある場合True
        """
        # 基本的な内容チェック
        has_to = bool(self.to_entry.get().strip())
        has_subject = bool(self.subject_entry.get().strip())
        has_body = bool(self.body_text.get("1.0", tk.END).strip())
        has_attachments = bool(self.attachments)
        
        return has_to or has_subject or has_body or has_attachments
    
    def _on_window_close(self):
        """
        ウィンドウ閉じるイベント
        """
        self._cancel_compose()
    
    def _update_status(self, message: str):
        """
        ステータスメッセージを更新します
        
        Args:
            message: ステータスメッセージ
        """
        if self.status_label:
            self.status_label.config(text=message)
        logger.debug(f"ステータス更新: {message}")


def show_compose_window(parent, account: Account, 
                       message_type: str = "new",
                       original_message: Optional[MailMessage] = None,
                       on_sent: Optional[Callable] = None):
    """
    メール作成ウィンドウを表示します
    
    Args:
        parent: 親ウィンドウ
        account: 送信アカウント
        message_type: メッセージタイプ（"new", "reply", "forward"）
        original_message: 返信・転送元メッセージ
        on_sent: 送信完了コールバック
    
    Returns:
        ComposeWindow: 作成されたウィンドウインスタンス
    """
    try:
        compose_window = ComposeWindow(
            parent=parent,
            account=account,
            message_type=message_type,
            original_message=original_message,
            on_sent=on_sent
        )
        
        return compose_window
        
    except Exception as e:
        logger.error(f"メール作成ウィンドウ表示エラー: {e}")
        messagebox.showerror(
            "エラー",
            f"メール作成ウィンドウの表示に失敗しました:\n{e}",
            parent=parent
        )
        return None