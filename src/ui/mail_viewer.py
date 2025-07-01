# -*- coding: utf-8 -*-
"""
メール表示コンポーネント

WabiMailのメール本文表示機能を実装します。
HTML/テキストメールの表示、添付ファイル処理、インライン画像表示に対応し、
侘び寂びの美学に基づいた読みやすいメール表示を提供します。

Author: WabiMail Development Team
Created: 2025-07-01
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from typing import Optional, List, Dict, Any, Callable
import threading
import tempfile
import os
import webbrowser
from pathlib import Path
import html
import re
from datetime import datetime

from src.mail.mail_message import MailMessage, MailAttachment, MessageFlag
from src.utils.logger import get_logger

# ロガーを取得
logger = get_logger(__name__)


class MailViewer(ttk.Frame):
    """
    メール表示コンポーネントクラス
    
    メールの詳細表示を担当するUIコンポーネントです。
    侘び寂びの美学に基づいた、読みやすく美しいメール表示を実現します。
    
    機能:
    • HTML/テキストメールの表示
    • 添付ファイルの管理
    • インライン画像の表示
    • メールヘッダー情報の表示
    • 返信・転送・削除等のアクション
    • ズーム機能
    • 印刷対応（将来拡張）
    
    Attributes:
        master: 親ウィジェット
        current_message: 現在表示中のメッセージ
        on_reply: 返信コールバック関数
        on_forward: 転送コールバック関数
        on_delete: 削除コールバック関数
        show_html: HTML表示モード
        zoom_level: 表示倍率
    """
    
    def __init__(self, master, on_reply: Optional[Callable] = None,
                 on_forward: Optional[Callable] = None,
                 on_delete: Optional[Callable] = None):
        """
        メール表示コンポーネントを初期化します
        
        Args:
            master: 親ウィジェット
            on_reply: 返信ボタンクリック時のコールバック
            on_forward: 転送ボタンクリック時のコールバック
            on_delete: 削除ボタンクリック時のコールバック
        """
        super().__init__(master)
        
        self.current_message: Optional[MailMessage] = None
        self.on_reply = on_reply
        self.on_forward = on_forward
        self.on_delete = on_delete
        
        # 表示設定
        self.show_html = tk.BooleanVar(value=False)
        self.zoom_level = tk.DoubleVar(value=1.0)
        self.show_headers = tk.BooleanVar(value=False)
        
        # UI要素の参照
        self.header_frame = None
        self.content_frame = None
        self.text_widget = None
        self.html_widget = None
        self.attachments_frame = None
        self.status_label = None
        
        # 侘び寂びスタイルの設定
        self._setup_wabi_sabi_style()
        
        # UIを構築
        self._create_widgets()
        
        logger.info("メール表示コンポーネントを初期化しました")
    
    def _setup_wabi_sabi_style(self):
        """
        侘び寂びの美学に基づいたスタイルを設定します
        """
        style = ttk.Style()
        
        # メールビューア用カラーパレット
        self.colors = {
            'bg': '#fefefe',           # 和紙白
            'text': '#333333',         # 墨色
            'accent': '#f5f5f5',       # 薄いグレー
            'selected': '#ffe8e8',     # 薄桜色
            'header_bg': '#f9f9f9',    # ヘッダー背景
            'border': '#e0e0e0',       # 境界線
            'link': '#4a6fa5',         # リンク色（和風青）
            'attachment': '#8fbc8f'     # 添付ファイル色（和風緑）
        }
        
        # フォント設定
        self.fonts = {
            'header': ('Yu Gothic UI', 9, 'bold'),
            'body': ('Yu Gothic UI', 10),
            'mono': ('Consolas', 9),
            'small': ('Yu Gothic UI', 8)
        }
    
    def _create_widgets(self):
        """
        UIウィジェットを作成します
        """
        # メインコンテナ
        main_container = ttk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        
        # ヘッダーエリア
        self._create_header_area(main_container)
        
        # ツールバー
        self._create_toolbar(main_container)
        
        # メール本文エリア
        self._create_content_area(main_container)
        
        # 添付ファイルエリア
        self._create_attachments_area(main_container)
        
        # ステータスバー
        self._create_status_bar(main_container)
        
        # 初期状態では空のメッセージを表示
        self._show_empty_message()
    
    def _create_header_area(self, parent):
        """
        メールヘッダー表示エリアを作成します
        
        Args:
            parent: 親ウィジェット
        """
        # ヘッダーフレーム
        self.header_frame = ttk.Frame(parent, relief=tk.FLAT, borderwidth=1)
        self.header_frame.pack(fill=tk.X, pady=(0, 8))
        
        # ヘッダー内容フレーム
        header_content = ttk.Frame(self.header_frame)
        header_content.pack(fill=tk.X, padx=12, pady=8)
        
        # 件名表示
        self.subject_label = tk.Label(header_content, 
                                     text="件名が表示されます", 
                                     font=self.fonts['header'],
                                     bg=self.colors['bg'],
                                     fg=self.colors['text'],
                                     anchor=tk.W)
        self.subject_label.pack(fill=tk.X, pady=(0, 4))
        
        # 送信者・宛先情報フレーム
        info_frame = ttk.Frame(header_content)
        info_frame.pack(fill=tk.X, pady=(0, 4))
        
        # 送信者
        sender_frame = ttk.Frame(info_frame)
        sender_frame.pack(fill=tk.X, pady=1)
        
        tk.Label(sender_frame, text="差出人:", 
                font=self.fonts['small'], 
                bg=self.colors['bg'], fg=self.colors['text']).pack(side=tk.LEFT)
        
        self.sender_label = tk.Label(sender_frame, 
                                    text="送信者が表示されます",
                                    font=self.fonts['body'],
                                    bg=self.colors['bg'], fg=self.colors['text'],
                                    anchor=tk.W)
        self.sender_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 0))
        
        # 宛先
        recipient_frame = ttk.Frame(info_frame)
        recipient_frame.pack(fill=tk.X, pady=1)
        
        tk.Label(recipient_frame, text="宛先:", 
                font=self.fonts['small'], 
                bg=self.colors['bg'], fg=self.colors['text']).pack(side=tk.LEFT)
        
        self.recipient_label = tk.Label(recipient_frame, 
                                       text="宛先が表示されます",
                                       font=self.fonts['body'],
                                       bg=self.colors['bg'], fg=self.colors['text'],
                                       anchor=tk.W)
        self.recipient_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 0))
        
        # 日時・その他情報フレーム
        meta_frame = ttk.Frame(info_frame)
        meta_frame.pack(fill=tk.X, pady=1)
        
        tk.Label(meta_frame, text="日時:", 
                font=self.fonts['small'], 
                bg=self.colors['bg'], fg=self.colors['text']).pack(side=tk.LEFT)
        
        self.date_label = tk.Label(meta_frame, 
                                  text="日時が表示されます",
                                  font=self.fonts['body'],
                                  bg=self.colors['bg'], fg=self.colors['text'],
                                  anchor=tk.W)
        self.date_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 0))
        
        # 詳細ヘッダー表示用（オプション）
        self.detailed_header_frame = ttk.Frame(header_content)
        self.detailed_header_text = scrolledtext.ScrolledText(
            self.detailed_header_frame,
            height=6, width=50,
            font=self.fonts['mono'],
            bg=self.colors['accent'],
            fg=self.colors['text'],
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.detailed_header_text.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
    
    def _create_toolbar(self, parent):
        """
        ツールバーを作成します
        
        Args:
            parent: 親ウィジェット
        """
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, pady=(0, 8))
        
        # 左側：メールアクション
        action_frame = ttk.Frame(toolbar)
        action_frame.pack(side=tk.LEFT)
        
        # 返信ボタン
        self.reply_button = ttk.Button(action_frame, text="↩️ 返信", 
                                      command=self._on_reply_click)
        self.reply_button.pack(side=tk.LEFT, padx=(0, 4))
        
        # 全員に返信ボタン
        self.reply_all_button = ttk.Button(action_frame, text="↩️ 全員に返信", 
                                          command=self._on_reply_all_click)
        self.reply_all_button.pack(side=tk.LEFT, padx=(0, 4))
        
        # 転送ボタン
        self.forward_button = ttk.Button(action_frame, text="↪️ 転送", 
                                        command=self._on_forward_click)
        self.forward_button.pack(side=tk.LEFT, padx=(0, 4))
        
        # 削除ボタン
        self.delete_button = ttk.Button(action_frame, text="🗑️ 削除", 
                                       command=self._on_delete_click)
        self.delete_button.pack(side=tk.LEFT, padx=(0, 16))
        
        # フラグボタン
        self.flag_button = ttk.Button(action_frame, text="⭐ 重要", 
                                     command=self._on_flag_click)
        self.flag_button.pack(side=tk.LEFT, padx=(0, 4))
        
        # 右側：表示オプション
        options_frame = ttk.Frame(toolbar)
        options_frame.pack(side=tk.RIGHT)
        
        # HTML表示切り替え
        self.html_check = ttk.Checkbutton(options_frame, text="HTML表示", 
                                         variable=self.show_html,
                                         command=self._on_html_toggle)
        self.html_check.pack(side=tk.LEFT, padx=(0, 8))
        
        # ヘッダー表示切り替え
        self.headers_check = ttk.Checkbutton(options_frame, text="詳細ヘッダー", 
                                            variable=self.show_headers,
                                            command=self._on_headers_toggle)
        self.headers_check.pack(side=tk.LEFT, padx=(0, 8))
        
        # ズーム制御
        zoom_frame = ttk.Frame(options_frame)
        zoom_frame.pack(side=tk.LEFT)
        
        ttk.Label(zoom_frame, text="倍率:").pack(side=tk.LEFT)
        
        zoom_scale = ttk.Scale(zoom_frame, from_=0.5, to=2.0, 
                              variable=self.zoom_level, orient=tk.HORIZONTAL,
                              length=100, command=self._on_zoom_change)
        zoom_scale.pack(side=tk.LEFT, padx=(4, 4))
        
        self.zoom_label = ttk.Label(zoom_frame, text="100%")
        self.zoom_label.pack(side=tk.LEFT)
    
    def _create_content_area(self, parent):
        """
        メール本文表示エリアを作成します
        
        Args:
            parent: 親ウィジェット
        """
        # コンテンツフレーム
        self.content_frame = ttk.Frame(parent)
        self.content_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 8))
        
        # テキスト表示用ScrolledText
        self.text_widget = scrolledtext.ScrolledText(
            self.content_frame,
            font=self.fonts['body'],
            bg=self.colors['bg'],
            fg=self.colors['text'],
            wrap=tk.WORD,
            state=tk.DISABLED,
            selectbackground=self.colors['selected'],
            relief=tk.FLAT,
            borderwidth=0
        )
        self.text_widget.pack(fill=tk.BOTH, expand=True)
        
        # HTML表示用のWebビュー（将来拡張）
        # 現在はテキスト表示のみ実装
        
        # テキストウィジェットのスタイル設定
        self._configure_text_styles()
    
    def _configure_text_styles(self):
        """
        テキストウィジェットのスタイルを設定します
        """
        # 各種テキストスタイルを定義
        self.text_widget.tag_configure("header", 
                                      font=self.fonts['header'],
                                      foreground=self.colors['text'])
        
        self.text_widget.tag_configure("link", 
                                      font=self.fonts['body'],
                                      foreground=self.colors['link'],
                                      underline=True)
        
        self.text_widget.tag_configure("quote", 
                                      font=self.fonts['body'],
                                      foreground="#666666",
                                      lmargin1=20, lmargin2=20)
        
        self.text_widget.tag_configure("code", 
                                      font=self.fonts['mono'],
                                      background=self.colors['accent'])
        
        self.text_widget.tag_configure("emphasis", 
                                      font=(self.fonts['body'][0], self.fonts['body'][1], 'italic'))
        
        self.text_widget.tag_configure("strong", 
                                      font=self.fonts['header'])
        
        # リンククリックのバインド
        self.text_widget.tag_bind("link", "<Button-1>", self._on_link_click)
        self.text_widget.tag_bind("link", "<Enter>", self._on_link_enter)
        self.text_widget.tag_bind("link", "<Leave>", self._on_link_leave)
    
    def _create_attachments_area(self, parent):
        """
        添付ファイル表示エリアを作成します
        
        Args:
            parent: 親ウィジェット
        """
        # 添付ファイルフレーム（初期は非表示）
        self.attachments_frame = ttk.LabelFrame(parent, text="📎 添付ファイル")
        
        # 添付ファイルリスト
        attachments_content = ttk.Frame(self.attachments_frame)
        attachments_content.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)
        
        # 添付ファイルTreeview
        columns = ("name", "type", "size")
        self.attachments_tree = ttk.Treeview(attachments_content, 
                                            columns=columns, show="headings",
                                            height=3)
        
        # カラムヘッダー設定
        self.attachments_tree.heading("name", text="ファイル名", anchor=tk.W)
        self.attachments_tree.heading("type", text="種類", anchor=tk.W)
        self.attachments_tree.heading("size", text="サイズ", anchor=tk.W)
        
        # カラム幅設定
        self.attachments_tree.column("name", width=300, minwidth=200)
        self.attachments_tree.column("type", width=100, minwidth=80)
        self.attachments_tree.column("size", width=80, minwidth=60)
        
        # スクロールバー
        attachments_scroll = ttk.Scrollbar(attachments_content, 
                                          orient=tk.VERTICAL,
                                          command=self.attachments_tree.yview)
        self.attachments_tree.configure(yscrollcommand=attachments_scroll.set)
        
        # パッキング
        self.attachments_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        attachments_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 添付ファイルアクションボタン
        attachments_actions = ttk.Frame(self.attachments_frame)
        attachments_actions.pack(fill=tk.X, padx=8, pady=4)
        
        self.save_attachment_button = ttk.Button(attachments_actions, 
                                               text="💾 保存", 
                                               command=self._on_save_attachment)
        self.save_attachment_button.pack(side=tk.LEFT, padx=(0, 4))
        
        self.save_all_button = ttk.Button(attachments_actions, 
                                         text="💾 すべて保存", 
                                         command=self._on_save_all_attachments)
        self.save_all_button.pack(side=tk.LEFT, padx=(0, 4))
        
        self.open_attachment_button = ttk.Button(attachments_actions, 
                                               text="📂 開く", 
                                               command=self._on_open_attachment)
        self.open_attachment_button.pack(side=tk.LEFT)
        
        # ダブルクリックイベント
        self.attachments_tree.bind("<Double-1>", self._on_attachment_double_click)
    
    def _create_status_bar(self, parent):
        """
        ステータスバーを作成します
        
        Args:
            parent: 親ウィジェット
        """
        status_frame = ttk.Frame(parent, relief=tk.SUNKEN, borderwidth=1)
        status_frame.pack(fill=tk.X)
        
        self.status_label = ttk.Label(status_frame, text="メールを選択してください")
        self.status_label.pack(side=tk.LEFT, padx=4, pady=2)
        
        # メール情報表示
        self.mail_info_label = ttk.Label(status_frame, text="")
        self.mail_info_label.pack(side=tk.RIGHT, padx=4, pady=2)
    
    def display_message(self, message: MailMessage):
        """
        メールメッセージを表示します
        
        Args:
            message: 表示するメールメッセージ
        """
        self.current_message = message
        
        if not message:
            self._show_empty_message()
            return
        
        try:
            # ヘッダー情報を表示
            self._display_header_info(message)
            
            # 本文を表示
            self._display_body_content(message)
            
            # 添付ファイルを表示
            self._display_attachments(message)
            
            # ボタン状態を更新
            self._update_button_states(message)
            
            # ステータスを更新
            self._update_status(message)
            
            # 既読マークを設定
            if not message.is_read():
                message.mark_as_read()
            
            logger.debug(f"メッセージを表示しました: {message.subject}")
            
        except Exception as e:
            logger.error(f"メッセージ表示エラー: {e}")
            self._show_error_message(f"メッセージの表示中にエラーが発生しました: {e}")
    
    def _display_header_info(self, message: MailMessage):
        """
        メールヘッダー情報を表示します
        
        Args:
            message: 表示するメッセージ
        """
        # 件名
        subject = message.subject or "[件名なし]"
        self.subject_label.config(text=subject)
        
        # 送信者
        sender = message.sender or "[送信者不明]"
        self.sender_label.config(text=sender)
        
        # 宛先
        recipients = ", ".join(message.recipients) if message.recipients else "[宛先不明]"
        if len(recipients) > 60:
            recipients = recipients[:57] + "..."
        self.recipient_label.config(text=recipients)
        
        # 日時
        date_str = message.get_display_date().strftime("%Y年%m月%d日 %H:%M:%S")
        self.date_label.config(text=date_str)
        
        # 詳細ヘッダー（オプション）
        if self.show_headers.get():
            self._display_detailed_headers(message)
            self.detailed_header_frame.pack(fill=tk.X, pady=(8, 0))
        else:
            self.detailed_header_frame.pack_forget()
    
    def _display_detailed_headers(self, message: MailMessage):
        """
        詳細ヘッダー情報を表示します
        
        Args:
            message: 表示するメッセージ
        """
        self.detailed_header_text.config(state=tk.NORMAL)
        self.detailed_header_text.delete(1.0, tk.END)
        
        header_text = ""
        
        # 基本ヘッダー
        if message.message_id:
            header_text += f"Message-ID: {message.message_id}\n"
        if message.in_reply_to:
            header_text += f"In-Reply-To: {message.in_reply_to}\n"
        if message.references:
            header_text += f"References: {' '.join(message.references)}\n"
        if message.reply_to:
            header_text += f"Reply-To: {message.reply_to}\n"
        if message.cc_recipients:
            header_text += f"CC: {', '.join(message.cc_recipients)}\n"
        if message.priority != "normal":
            header_text += f"Priority: {message.priority}\n"
        
        # 生ヘッダー情報
        if message.raw_headers:
            header_text += "\n--- 生ヘッダー ---\n"
            for key, value in message.raw_headers.items():
                header_text += f"{key}: {value}\n"
        
        self.detailed_header_text.insert(tk.END, header_text)
        self.detailed_header_text.config(state=tk.DISABLED)
    
    def _display_body_content(self, message: MailMessage):
        """
        メール本文を表示します
        
        Args:
            message: 表示するメッセージ
        """
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete(1.0, tk.END)
        
        if self.show_html.get() and message.body_html:
            # HTML表示
            self._display_html_content(message.body_html)
        else:
            # テキスト表示
            self._display_text_content(message.body_text or "[本文なし]")
        
        self.text_widget.config(state=tk.DISABLED)
    
    def _display_text_content(self, text: str):
        """
        テキスト本文を表示します
        
        Args:
            text: 表示するテキスト
        """
        # URLの検出とリンク化
        url_pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
        
        lines = text.split('\n')
        for line_num, line in enumerate(lines):
            # 引用行の検出（>で始まる行）
            if line.strip().startswith('>'):
                self.text_widget.insert(tk.END, line, "quote")
            else:
                # URLの検出
                last_end = 0
                for match in re.finditer(url_pattern, line):
                    # URL前のテキスト
                    if match.start() > last_end:
                        self.text_widget.insert(tk.END, line[last_end:match.start()])
                    
                    # URL部分をリンクとして挿入
                    url = match.group()
                    if not url.startswith('http'):
                        url = 'http://' + url
                    
                    start_index = self.text_widget.index(tk.END)
                    self.text_widget.insert(tk.END, match.group(), "link")
                    end_index = self.text_widget.index(tk.END)
                    
                    # URLを関連付け
                    self.text_widget.tag_add(f"url_{match.start()}", start_index, end_index)
                    self.text_widget.tag_bind(f"url_{match.start()}", "<Button-1>", 
                                            lambda e, u=url: self._open_url(u))
                    
                    last_end = match.end()
                
                # 残りのテキスト
                if last_end < len(line):
                    self.text_widget.insert(tk.END, line[last_end:])
            
            # 改行（最後の行以外）
            if line_num < len(lines) - 1:
                self.text_widget.insert(tk.END, '\n')
    
    def _display_html_content(self, html: str):
        """
        HTML本文を表示します（簡易版）
        
        Args:
            html: 表示するHTML
        """
        # 簡易的なHTML→テキスト変換
        # 将来的にはHTMLViewerウィジェットを使用
        
        # HTMLタグを除去してテキスト化
        text = self._html_to_text(html)
        self._display_text_content(text)
        
        # HTML表示モードであることを示すマーク
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.insert(1.0, "[HTML表示モード]\n\n", "header")
        self.text_widget.config(state=tk.DISABLED)
    
    def _html_to_text(self, html: str) -> str:
        """
        HTMLをテキストに変換します（簡易版）
        
        Args:
            html: HTML文字列
            
        Returns:
            str: 変換されたテキスト
        """
        if not html:
            return ""
        
        # HTMLエンティティをデコード
        text = html.unescape(html)
        
        # 基本的なHTMLタグを処理
        text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
        text = re.sub(r'<p\s*[^>]*>', '\n\n', text, flags=re.IGNORECASE)
        text = re.sub(r'</p>', '', text, flags=re.IGNORECASE)
        text = re.sub(r'<div\s*[^>]*>', '\n', text, flags=re.IGNORECASE)
        text = re.sub(r'</div>', '', text, flags=re.IGNORECASE)
        
        # すべてのHTMLタグを除去
        text = re.sub(r'<[^>]+>', '', text)
        
        # 連続する空白・改行を整理
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
        text = re.sub(r'^\s+|\s+$', '', text, flags=re.MULTILINE)
        
        return text.strip()
    
    def _display_attachments(self, message: MailMessage):
        """
        添付ファイルを表示します
        
        Args:
            message: 表示するメッセージ
        """
        # 既存の添付ファイルリストをクリア
        for item in self.attachments_tree.get_children():
            self.attachments_tree.delete(item)
        
        if message.has_attachments():
            # 添付ファイルフレームを表示
            self.attachments_frame.pack(fill=tk.X, pady=(0, 8))
            
            # 各添付ファイルを追加
            for attachment in message.attachments:
                # ファイルサイズを人間が読みやすい形式に変換
                size_str = self._format_file_size(attachment.size)
                
                # アイテムを追加
                self.attachments_tree.insert("", "end", values=(
                    attachment.filename,
                    attachment.content_type,
                    size_str
                ))
        else:
            # 添付ファイルがない場合は非表示
            self.attachments_frame.pack_forget()
    
    def _format_file_size(self, size: int) -> str:
        """
        ファイルサイズを人間が読みやすい形式にフォーマットします
        
        Args:
            size: ファイルサイズ（バイト）
            
        Returns:
            str: フォーマットされたサイズ文字列
        """
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        elif size < 1024 * 1024 * 1024:
            return f"{size / (1024 * 1024):.1f} MB"
        else:
            return f"{size / (1024 * 1024 * 1024):.1f} GB"
    
    def _update_button_states(self, message: MailMessage):
        """
        ボタンの状態を更新します
        
        Args:
            message: 現在のメッセージ
        """
        # メッセージがある場合はボタンを有効化
        state = tk.NORMAL if message else tk.DISABLED
        
        self.reply_button.config(state=state)
        self.reply_all_button.config(state=state)
        self.forward_button.config(state=state)
        self.delete_button.config(state=state)
        self.flag_button.config(state=state)
        
        # フラグボタンのテキストを更新
        if message and message.is_flagged():
            self.flag_button.config(text="⭐ 重要解除")
        else:
            self.flag_button.config(text="⭐ 重要")
    
    def _update_status(self, message: MailMessage):
        """
        ステータス情報を更新します
        
        Args:
            message: 現在のメッセージ
        """
        if message:
            # 基本ステータス
            status_text = f"件名: {message.subject}"
            self.status_label.config(text=status_text)
            
            # メール情報
            flags = []
            if message.is_read():
                flags.append("既読")
            if message.is_flagged():
                flags.append("重要")
            if message.has_attachments():
                flags.append(f"添付{message.get_attachment_count()}件")
            
            info_text = " | ".join(flags) if flags else "通常"
            self.mail_info_label.config(text=info_text)
        else:
            self.status_label.config(text="メールを選択してください")
            self.mail_info_label.config(text="")
    
    def _show_empty_message(self):
        """
        空のメッセージ表示を行います
        """
        self.subject_label.config(text="メールを選択してください")
        self.sender_label.config(text="")
        self.recipient_label.config(text="")
        self.date_label.config(text="")
        
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete(1.0, tk.END)
        self.text_widget.insert(1.0, """🌸 WabiMail メール表示

静かで美しいメール読書体験をお楽しみください。

左のメール一覧からメールを選択すると、
ここに詳細な内容が表示されます。

侘び寂びの美学に基づいた、
シンプルで心地よいインターフェースです。

--
静寂の中の美しさを追求して""")
        self.text_widget.config(state=tk.DISABLED)
        
        self.attachments_frame.pack_forget()
        self._update_button_states(None)
        self._update_status(None)
    
    def _show_error_message(self, error: str):
        """
        エラーメッセージを表示します
        
        Args:
            error: エラーメッセージ
        """
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete(1.0, tk.END)
        self.text_widget.insert(1.0, f"❌ エラー\n\n{error}")
        self.text_widget.config(state=tk.DISABLED)
    
    # イベントハンドラー
    def _on_reply_click(self):
        """返信ボタンクリックイベント"""
        if self.current_message and self.on_reply:
            self.on_reply(self.current_message, reply_all=False)
    
    def _on_reply_all_click(self):
        """全員に返信ボタンクリックイベント"""
        if self.current_message and self.on_reply:
            self.on_reply(self.current_message, reply_all=True)
    
    def _on_forward_click(self):
        """転送ボタンクリックイベント"""
        if self.current_message and self.on_forward:
            self.on_forward(self.current_message)
    
    def _on_delete_click(self):
        """削除ボタンクリックイベント"""
        if self.current_message and self.on_delete:
            result = messagebox.askyesno(
                "確認", 
                f"「{self.current_message.subject}」を削除しますか？",
                icon=messagebox.QUESTION
            )
            if result:
                self.on_delete(self.current_message)
    
    def _on_flag_click(self):
        """重要マークボタンクリックイベント"""
        if self.current_message:
            if self.current_message.is_flagged():
                self.current_message.remove_flag(MessageFlag.FLAGGED)
            else:
                self.current_message.add_flag(MessageFlag.FLAGGED)
            
            self._update_button_states(self.current_message)
            self._update_status(self.current_message)
    
    def _on_html_toggle(self):
        """HTML表示切り替えイベント"""
        if self.current_message:
            self._display_body_content(self.current_message)
    
    def _on_headers_toggle(self):
        """ヘッダー表示切り替えイベント"""
        if self.current_message:
            self._display_header_info(self.current_message)
    
    def _on_zoom_change(self, value):
        """ズーム変更イベント"""
        zoom = float(value)
        percentage = int(zoom * 100)
        self.zoom_label.config(text=f"{percentage}%")
        
        # フォントサイズを調整
        base_size = 10
        new_size = int(base_size * zoom)
        new_font = (self.fonts['body'][0], new_size)
        
        self.text_widget.config(font=new_font)
    
    def _on_link_click(self, event):
        """リンククリックイベント"""
        # 現在の実装では何もしない（_open_urlで処理）
        pass
    
    def _on_link_enter(self, event):
        """リンクマウスエンターイベント"""
        self.text_widget.config(cursor="hand2")
    
    def _on_link_leave(self, event):
        """リンクマウスリーブイベント"""
        self.text_widget.config(cursor="")
    
    def _open_url(self, url: str):
        """URLを開きます"""
        try:
            webbrowser.open(url)
        except Exception as e:
            messagebox.showerror("エラー", f"URLを開けませんでした: {e}")
    
    # 添付ファイル関連イベント
    def _on_save_attachment(self):
        """添付ファイル保存イベント"""
        selection = self.attachments_tree.selection()
        if not selection or not self.current_message:
            return
        
        item = selection[0]
        filename = self.attachments_tree.item(item, "values")[0]
        
        # 対応する添付ファイルを検索
        attachment = None
        for att in self.current_message.attachments:
            if att.filename == filename:
                attachment = att
                break
        
        if attachment:
            self._save_attachment_to_file(attachment)
    
    def _on_save_all_attachments(self):
        """すべての添付ファイル保存イベント"""
        if not self.current_message or not self.current_message.has_attachments():
            return
        
        # ディレクトリ選択
        directory = filedialog.askdirectory(title="保存先ディレクトリを選択")
        if directory:
            for attachment in self.current_message.attachments:
                self._save_attachment_to_directory(attachment, directory)
    
    def _on_open_attachment(self):
        """添付ファイルを開くイベント"""
        selection = self.attachments_tree.selection()
        if not selection or not self.current_message:
            return
        
        item = selection[0]
        filename = self.attachments_tree.item(item, "values")[0]
        
        # 対応する添付ファイルを検索
        attachment = None
        for att in self.current_message.attachments:
            if att.filename == filename:
                attachment = att
                break
        
        if attachment:
            self._open_attachment_temp(attachment)
    
    def _on_attachment_double_click(self, event):
        """添付ファイルダブルクリックイベント"""
        self._on_open_attachment()
    
    def _save_attachment_to_file(self, attachment: MailAttachment):
        """添付ファイルを指定ファイルに保存"""
        if not attachment.data:
            messagebox.showwarning("警告", "添付ファイルのデータが利用できません")
            return
        
        # ファイル保存ダイアログ
        filename = filedialog.asksaveasfilename(
            title=f"添付ファイルを保存: {attachment.filename}",
            initialname=attachment.filename,
            filetypes=[("すべてのファイル", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'wb') as f:
                    f.write(attachment.data)
                messagebox.showinfo("成功", f"添付ファイルを保存しました:\n{filename}")
            except Exception as e:
                messagebox.showerror("エラー", f"ファイル保存エラー: {e}")
    
    def _save_attachment_to_directory(self, attachment: MailAttachment, directory: str):
        """添付ファイルを指定ディレクトリに保存"""
        if not attachment.data:
            return
        
        try:
            filepath = os.path.join(directory, attachment.filename)
            with open(filepath, 'wb') as f:
                f.write(attachment.data)
        except Exception as e:
            logger.error(f"添付ファイル保存エラー: {e}")
    
    def _open_attachment_temp(self, attachment: MailAttachment):
        """添付ファイルを一時ファイルとして開く"""
        if not attachment.data:
            messagebox.showwarning("警告", "添付ファイルのデータが利用できません")
            return
        
        try:
            # 一時ファイルを作成
            temp_dir = tempfile.mkdtemp()
            temp_file = os.path.join(temp_dir, attachment.filename)
            
            with open(temp_file, 'wb') as f:
                f.write(attachment.data)
            
            # システムデフォルトアプリで開く
            if os.name == 'nt':  # Windows
                os.startfile(temp_file)
            elif os.name == 'posix':  # macOS, Linux
                os.system(f'open "{temp_file}"' if 'darwin' in os.uname().sysname.lower() 
                         else f'xdg-open "{temp_file}"')
                
        except Exception as e:
            messagebox.showerror("エラー", f"ファイルを開けませんでした: {e}")


# ユーティリティ関数
def create_mail_viewer(parent, **kwargs) -> MailViewer:
    """
    メール表示コンポーネントを作成します
    
    Args:
        parent: 親ウィジェット
        **kwargs: MailViewerのコンストラクタ引数
        
    Returns:
        MailViewer: 作成されたメール表示コンポーネント
    """
    return MailViewer(parent, **kwargs)