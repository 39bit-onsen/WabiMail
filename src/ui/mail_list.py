# -*- coding: utf-8 -*-
"""
メールリスト表示コンポーネント

WabiMailのメール一覧表示機能を実装します。
効率的なメールリスト表示、ソート機能、フィルタリング、
侘び寂びの美学に基づいた見やすいレイアウトを提供します。

Author: WabiMail Development Team
Created: 2025-07-01
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Optional, Dict, Any, Callable
import threading
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from src.mail.mail_message import MailMessage, MessageFlag
from src.utils.logger import get_logger

# ロガーを取得
logger = get_logger(__name__)


class SortColumn(Enum):
    """ソート可能なカラム"""
    DATE = "date"
    SENDER = "sender"
    SUBJECT = "subject"
    SIZE = "size"
    FLAGS = "flags"


class SortOrder(Enum):
    """ソート順序"""
    ASCENDING = "asc"
    DESCENDING = "desc"


@dataclass
class MailListFilter:
    """メールリストフィルター設定"""
    unread_only: bool = False
    flagged_only: bool = False
    has_attachments: bool = False
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    sender_filter: str = ""
    subject_filter: str = ""


class MailList(ttk.Frame):
    """
    メールリスト表示コンポーネントクラス
    
    メール一覧の表示を担当するUIコンポーネントです。
    侘び寂びの美学に基づいた、見やすく使いやすいメールリストを実現します。
    
    機能:
    • 高速なメールリスト表示
    • 複数カラムでのソート
    • 高度なフィルタリング
    • 仮想スクロール（大量メール対応）
    • コンテキストメニュー
    • キーボードナビゲーション
    • 選択状態の管理
    
    Attributes:
        master: 親ウィジェット
        on_selection_change: 選択変更コールバック
        on_double_click: ダブルクリックコールバック
        on_context_menu: コンテキストメニューコールバック
        messages: 表示中のメッセージリスト
        filtered_messages: フィルタリング後のメッセージリスト
        selected_messages: 選択中のメッセージリスト
        sort_column: 現在のソートカラム
        sort_order: 現在のソート順序
        filter_settings: フィルター設定
    """
    
    def __init__(self, master, 
                 on_selection_change: Optional[Callable] = None,
                 on_double_click: Optional[Callable] = None,
                 on_context_menu: Optional[Callable] = None):
        """
        メールリストコンポーネントを初期化します
        
        Args:
            master: 親ウィジェット
            on_selection_change: 選択変更時のコールバック
            on_double_click: ダブルクリック時のコールバック
            on_context_menu: 右クリック時のコールバック
        """
        super().__init__(master)
        
        # コールバック関数
        self.on_selection_change = on_selection_change
        self.on_double_click = on_double_click
        self.on_context_menu = on_context_menu
        
        # データ管理
        self.messages: List[MailMessage] = []
        self.filtered_messages: List[MailMessage] = []
        self.selected_messages: List[MailMessage] = []
        
        # ソート・フィルター設定
        self.sort_column = SortColumn.DATE
        self.sort_order = SortOrder.DESCENDING
        self.filter_settings = MailListFilter()
        
        # UI要素の参照
        self.tree = None
        self.search_entry = None
        self.status_label = None
        self.filter_frame = None
        
        # 表示設定
        self.items_per_page = 100  # 仮想スクロール用
        self.current_page = 0
        self.show_preview = tk.BooleanVar(value=True)
        self.compact_view = tk.BooleanVar(value=False)
        
        # パフォーマンス設定
        self._update_pending = False
        self._last_update_time = datetime.now()
        
        # 侘び寂びスタイルの設定
        self._setup_wabi_sabi_style()
        
        # UIを構築
        self._create_widgets()
        
        logger.info("メールリストコンポーネントを初期化しました")
    
    def _setup_wabi_sabi_style(self):
        """
        侘び寂びの美学に基づいたスタイルを設定します
        """
        style = ttk.Style()
        
        # メールリスト用カラーパレット
        self.colors = {
            'bg': '#fefefe',           # 和紙白
            'text': '#333333',         # 墨色
            'accent': '#f5f5f5',       # 薄いグレー
            'selected': '#ffe8e8',     # 薄桜色
            'unread': '#4a6fa5',       # 未読色（和風青）
            'flagged': '#d4a574',      # 重要色（和風金）
            'border': '#e0e0e0',       # 境界線
            'hover': '#f0f8ff'         # ホバー色
        }
        
        # フォント設定
        self.fonts = {
            'header': ('Yu Gothic UI', 9, 'bold'),
            'normal': ('Yu Gothic UI', 9),
            'small': ('Yu Gothic UI', 8),
            'unread': ('Yu Gothic UI', 9, 'bold')
        }
        
        # Treeviewスタイル設定
        style.configure("MailList.Treeview",
                       background=self.colors['bg'],
                       foreground=self.colors['text'],
                       fieldbackground=self.colors['bg'],
                       selectbackground=self.colors['selected'],
                       selectforeground=self.colors['text'],
                       font=self.fonts['normal'],
                       borderwidth=0,
                       relief="flat")
        
        style.configure("MailList.Treeview.Heading",
                       background=self.colors['accent'],
                       foreground=self.colors['text'],
                       font=self.fonts['header'],
                       relief="flat")
        
        # 未読メール用スタイル
        style.configure("Unread.MailList.Treeview",
                       font=self.fonts['unread'])
    
    def _create_widgets(self):
        """
        UIウィジェットを作成します
        """
        # メインコンテナ
        main_container = ttk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # ヘッダーエリア（検索・フィルター）
        self._create_header_area(main_container)
        
        # メールリストTreeview
        self._create_treeview(main_container)
        
        # ステータスバー
        self._create_status_bar(main_container)
        
        # コンテキストメニュー
        self._create_context_menu()
        
        # キーボードバインド
        self._setup_keyboard_bindings()
    
    def _create_header_area(self, parent):
        """
        ヘッダーエリア（検索・フィルター）を作成します
        
        Args:
            parent: 親ウィジェット
        """
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, padx=8, pady=(8, 4))
        
        # 左側：タイトルと件数
        left_frame = ttk.Frame(header_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.title_label = ttk.Label(left_frame, text="📥 メール一覧", 
                                    font=self.fonts['header'])
        self.title_label.pack(side=tk.LEFT)
        
        self.count_label = ttk.Label(left_frame, text="(0件)", 
                                    font=self.fonts['small'])
        self.count_label.pack(side=tk.LEFT, padx=(8, 0))
        
        # 右側：検索とオプション
        right_frame = ttk.Frame(header_frame)
        right_frame.pack(side=tk.RIGHT)
        
        # 検索エントリ
        search_frame = ttk.Frame(right_frame)
        search_frame.pack(side=tk.LEFT, padx=(0, 8))
        
        ttk.Label(search_frame, text="🔍").pack(side=tk.LEFT)
        
        self.search_entry = ttk.Entry(search_frame, width=20)
        self.search_entry.pack(side=tk.LEFT, padx=(4, 0))
        self.search_entry.bind("<KeyRelease>", self._on_search_change)
        self.search_entry.bind("<Return>", self._on_search_enter)
        
        # 表示オプション
        options_frame = ttk.Frame(right_frame)
        options_frame.pack(side=tk.LEFT)
        
        # プレビュー表示切り替え
        self.preview_check = ttk.Checkbutton(options_frame, text="プレビュー", 
                                           variable=self.show_preview,
                                           command=self._on_preview_toggle)
        self.preview_check.pack(side=tk.LEFT, padx=(0, 4))
        
        # コンパクト表示切り替え
        self.compact_check = ttk.Checkbutton(options_frame, text="コンパクト", 
                                           variable=self.compact_view,
                                           command=self._on_compact_toggle)
        self.compact_check.pack(side=tk.LEFT, padx=(0, 4))
        
        # フィルターボタン
        self.filter_button = ttk.Button(options_frame, text="📋 フィルター", 
                                       command=self._on_filter_click)
        self.filter_button.pack(side=tk.LEFT)
        
        # フィルターフレーム（初期は非表示）
        self._create_filter_frame(parent)
    
    def _create_filter_frame(self, parent):
        """
        フィルターフレームを作成します
        
        Args:
            parent: 親ウィジェット
        """
        self.filter_frame = ttk.LabelFrame(parent, text="📋 フィルター設定")
        
        filter_content = ttk.Frame(self.filter_frame)
        filter_content.pack(fill=tk.X, padx=8, pady=4)
        
        # 上段：チェックボックスフィルター
        top_row = ttk.Frame(filter_content)
        top_row.pack(fill=tk.X, pady=(0, 4))
        
        self.unread_only_var = tk.BooleanVar()
        ttk.Checkbutton(top_row, text="未読のみ", 
                       variable=self.unread_only_var,
                       command=self._on_filter_change).pack(side=tk.LEFT, padx=(0, 16))
        
        self.flagged_only_var = tk.BooleanVar()
        ttk.Checkbutton(top_row, text="重要のみ", 
                       variable=self.flagged_only_var,
                       command=self._on_filter_change).pack(side=tk.LEFT, padx=(0, 16))
        
        self.attachments_only_var = tk.BooleanVar()
        ttk.Checkbutton(top_row, text="添付ありのみ", 
                       variable=self.attachments_only_var,
                       command=self._on_filter_change).pack(side=tk.LEFT)
        
        # 下段：テキストフィルター
        bottom_row = ttk.Frame(filter_content)
        bottom_row.pack(fill=tk.X, pady=(0, 4))
        
        # 送信者フィルター
        ttk.Label(bottom_row, text="送信者:").pack(side=tk.LEFT)
        self.sender_filter_entry = ttk.Entry(bottom_row, width=15)
        self.sender_filter_entry.pack(side=tk.LEFT, padx=(4, 16))
        self.sender_filter_entry.bind("<KeyRelease>", self._on_filter_change)
        
        # 件名フィルター
        ttk.Label(bottom_row, text="件名:").pack(side=tk.LEFT)
        self.subject_filter_entry = ttk.Entry(bottom_row, width=15)
        self.subject_filter_entry.pack(side=tk.LEFT, padx=(4, 16))
        self.subject_filter_entry.bind("<KeyRelease>", self._on_filter_change)
        
        # フィルタークリアボタン
        ttk.Button(bottom_row, text="クリア", 
                  command=self._on_filter_clear).pack(side=tk.LEFT)
    
    def _create_treeview(self, parent):
        """
        Treeviewウィジェットを作成します
        
        Args:
            parent: 親ウィジェット
        """
        # Treeviewコンテナ
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)
        
        # カラム定義
        columns = ("flags", "sender", "subject", "date", "size")
        
        self.tree = ttk.Treeview(tree_frame, 
                                columns=columns, 
                                show="headings",
                                style="MailList.Treeview",
                                selectmode="extended")
        
        # カラムヘッダー設定
        self.tree.heading("flags", text="", anchor=tk.W, 
                         command=lambda: self._on_column_click(SortColumn.FLAGS))
        self.tree.heading("sender", text="送信者", anchor=tk.W,
                         command=lambda: self._on_column_click(SortColumn.SENDER))
        self.tree.heading("subject", text="件名", anchor=tk.W,
                         command=lambda: self._on_column_click(SortColumn.SUBJECT))
        self.tree.heading("date", text="日時", anchor=tk.W,
                         command=lambda: self._on_column_click(SortColumn.DATE))
        self.tree.heading("size", text="サイズ", anchor=tk.W,
                         command=lambda: self._on_column_click(SortColumn.SIZE))
        
        # カラム幅設定
        self.tree.column("flags", width=50, minwidth=40, stretch=False)
        self.tree.column("sender", width=180, minwidth=120)
        self.tree.column("subject", width=300, minwidth=200)
        self.tree.column("date", width=120, minwidth=100, stretch=False)
        self.tree.column("size", width=80, minwidth=60, stretch=False)
        
        # スクロールバー
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # レイアウト
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # イベントバインド
        self.tree.bind("<<TreeviewSelect>>", self._on_selection_change_event)
        self.tree.bind("<Double-1>", self._on_double_click_event)
        self.tree.bind("<Button-3>", self._on_right_click_event)
        self.tree.bind("<Return>", self._on_enter_key)
        self.tree.bind("<Delete>", self._on_delete_key)
    
    def _create_status_bar(self, parent):
        """
        ステータスバーを作成します
        
        Args:
            parent: 親ウィジェット
        """
        status_frame = ttk.Frame(parent, relief=tk.SUNKEN, borderwidth=1)
        status_frame.pack(fill=tk.X, padx=8, pady=(4, 8))
        
        self.status_label = ttk.Label(status_frame, text="メールリストを読み込み中...")
        self.status_label.pack(side=tk.LEFT, padx=4, pady=2)
        
        # 選択状況表示
        self.selection_label = ttk.Label(status_frame, text="")
        self.selection_label.pack(side=tk.RIGHT, padx=4, pady=2)
    
    def _create_context_menu(self):
        """
        コンテキストメニューを作成します
        """
        self.context_menu = tk.Menu(self, tearoff=0)
        
        self.context_menu.add_command(label="📖 既読にする", 
                                     command=self._on_mark_read)
        self.context_menu.add_command(label="📩 未読にする", 
                                     command=self._on_mark_unread)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="⭐ 重要マーク", 
                                     command=self._on_mark_flagged)
        self.context_menu.add_command(label="⭐ 重要解除", 
                                     command=self._on_unmark_flagged)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="↩️ 返信", 
                                     command=self._on_reply)
        self.context_menu.add_command(label="↪️ 転送", 
                                     command=self._on_forward)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="🗑️ 削除", 
                                     command=self._on_delete)
    
    def _setup_keyboard_bindings(self):
        """
        キーボードバインドを設定します
        """
        self.tree.bind("<Control-a>", self._on_select_all)
        self.tree.bind("<F5>", self._on_refresh)
        self.tree.bind("<Control-f>", self._on_focus_search)
        
        # 矢印キーでの選択移動を改善
        self.tree.bind("<Up>", self._on_arrow_up)
        self.tree.bind("<Down>", self._on_arrow_down)
    
    def set_messages(self, messages: List[MailMessage], folder_name: str = "受信トレイ"):
        """
        メッセージリストを設定します
        
        Args:
            messages: 表示するメッセージリスト
            folder_name: フォルダ名
        """
        self.messages = messages.copy()
        self.title_label.config(text=f"📥 {folder_name}")
        
        # フィルターを適用して表示を更新
        self._apply_filters()
        self._update_display()
        
        logger.debug(f"メッセージリストを設定しました: {len(messages)}件")
    
    def add_messages(self, messages: List[MailMessage]):
        """
        メッセージを追加します
        
        Args:
            messages: 追加するメッセージリスト
        """
        self.messages.extend(messages)
        self._apply_filters()
        self._update_display()
        
        logger.debug(f"メッセージを追加しました: {len(messages)}件")
    
    def update_message(self, message: MailMessage):
        """
        メッセージを更新します
        
        Args:
            message: 更新するメッセージ
        """
        # 既存メッセージを検索して更新
        for i, msg in enumerate(self.messages):
            if msg.message_id == message.message_id:
                self.messages[i] = message
                break
        
        self._apply_filters()
        self._update_display()
    
    def remove_messages(self, message_ids: List[str]):
        """
        メッセージを削除します
        
        Args:
            message_ids: 削除するメッセージIDリスト
        """
        self.messages = [msg for msg in self.messages if msg.message_id not in message_ids]
        self._apply_filters()
        self._update_display()
        
        logger.debug(f"メッセージを削除しました: {len(message_ids)}件")
    
    def get_selected_messages(self) -> List[MailMessage]:
        """
        選択中のメッセージリストを取得します
        
        Returns:
            List[MailMessage]: 選択中のメッセージリスト
        """
        return self.selected_messages.copy()
    
    def get_selected_message(self) -> Optional[MailMessage]:
        """
        最初に選択されたメッセージを取得します
        
        Returns:
            Optional[MailMessage]: 選択されたメッセージ、なければNone
        """
        return self.selected_messages[0] if self.selected_messages else None
    
    def _apply_filters(self):
        """
        フィルター設定を適用します
        """
        # フィルター設定を更新
        self.filter_settings.unread_only = self.unread_only_var.get() if hasattr(self, 'unread_only_var') else False
        self.filter_settings.flagged_only = self.flagged_only_var.get() if hasattr(self, 'flagged_only_var') else False
        self.filter_settings.has_attachments = self.attachments_only_var.get() if hasattr(self, 'attachments_only_var') else False
        self.filter_settings.sender_filter = self.sender_filter_entry.get() if hasattr(self, 'sender_filter_entry') else ""
        self.filter_settings.subject_filter = self.subject_filter_entry.get() if hasattr(self, 'subject_filter_entry') else ""
        
        # 検索クエリ
        search_query = self.search_entry.get().lower() if hasattr(self, 'search_entry') else ""
        
        # フィルタリング実行
        self.filtered_messages = []
        
        for message in self.messages:
            # 基本フィルター
            if self.filter_settings.unread_only and message.is_read():
                continue
            if self.filter_settings.flagged_only and not message.is_flagged():
                continue
            if self.filter_settings.has_attachments and not message.has_attachments():
                continue
            
            # テキストフィルター
            if self.filter_settings.sender_filter:
                if self.filter_settings.sender_filter.lower() not in message.sender.lower():
                    continue
            
            if self.filter_settings.subject_filter:
                if self.filter_settings.subject_filter.lower() not in message.subject.lower():
                    continue
            
            # 検索クエリ
            if search_query:
                searchable_text = f"{message.sender} {message.subject} {message.body_text}".lower()
                if search_query not in searchable_text:
                    continue
            
            self.filtered_messages.append(message)
        
        # ソートを適用
        self._apply_sort()
    
    def _apply_sort(self):
        """
        ソート設定を適用します
        """
        reverse = (self.sort_order == SortOrder.DESCENDING)
        
        if self.sort_column == SortColumn.DATE:
            self.filtered_messages.sort(key=lambda msg: msg.get_display_date(), reverse=reverse)
        elif self.sort_column == SortColumn.SENDER:
            self.filtered_messages.sort(key=lambda msg: msg.sender.lower(), reverse=reverse)
        elif self.sort_column == SortColumn.SUBJECT:
            self.filtered_messages.sort(key=lambda msg: msg.subject.lower(), reverse=reverse)
        elif self.sort_column == SortColumn.SIZE:
            self.filtered_messages.sort(key=lambda msg: len(msg.body_text) + len(msg.body_html), reverse=reverse)
        elif self.sort_column == SortColumn.FLAGS:
            self.filtered_messages.sort(key=lambda msg: (not msg.is_read(), msg.is_flagged()), reverse=reverse)
    
    def _update_display(self):
        """
        表示を更新します
        """
        # 更新頻度制限
        now = datetime.now()
        if self._update_pending or (now - self._last_update_time).total_seconds() < 0.1:
            return
        
        self._update_pending = True
        self._last_update_time = now
        
        # 少し遅延させて更新（UI応答性向上）
        self.after(50, self._do_update_display)
    
    def _do_update_display(self):
        """
        実際の表示更新処理
        """
        try:
            # 既存のアイテムをクリア
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # メッセージを表示
            for message in self.filtered_messages:
                self._add_message_to_tree(message)
            
            # 件数を更新
            total_count = len(self.messages)
            filtered_count = len(self.filtered_messages)
            
            if total_count == filtered_count:
                count_text = f"({total_count}件)"
            else:
                count_text = f"({filtered_count}/{total_count}件)"
            
            self.count_label.config(text=count_text)
            
            # ステータスを更新
            self.status_label.config(text=f"メール一覧を更新しました")
            
        except Exception as e:
            logger.error(f"表示更新エラー: {e}")
            self.status_label.config(text=f"表示更新エラー: {e}")
        finally:
            self._update_pending = False
    
    def _add_message_to_tree(self, message: MailMessage):
        """
        メッセージをTreeviewに追加します
        
        Args:
            message: 追加するメッセージ
        """
        # フラグアイコン
        flags = ""
        if not message.is_read():
            flags += "📩"
        else:
            flags += "📖"
        
        if message.is_flagged():
            flags += "⭐"
        
        if message.has_attachments():
            flags += "📎"
        
        # 送信者表示（コンパクトモードで調整）
        sender = message.sender
        max_sender_length = 15 if self.compact_view.get() else 25
        if len(sender) > max_sender_length:
            sender = sender[:max_sender_length-3] + "..."
        
        # 件名表示
        subject = message.subject or "[件名なし]"
        
        # プレビュー表示
        if self.show_preview.get() and not self.compact_view.get():
            preview = message.get_body_preview(50)
            if preview != "[本文なし]":
                subject += f" - {preview}"
        
        max_subject_length = 40 if self.compact_view.get() else 80
        if len(subject) > max_subject_length:
            subject = subject[:max_subject_length-3] + "..."
        
        # 日時表示
        date_str = message.get_display_date().strftime("%m/%d %H:%M")
        
        # サイズ表示（推定）
        size = len(message.body_text) + len(message.body_html)
        if size < 1024:
            size_str = f"{size}B"
        elif size < 1024 * 1024:
            size_str = f"{size//1024}KB"
        else:
            size_str = f"{size//(1024*1024)}MB"
        
        # アイテムを挿入
        item_id = self.tree.insert("", "end", values=(
            flags, sender, subject, date_str, size_str
        ))
        
        # メッセージオブジェクトを関連付け
        self.tree.set(item_id, "message_obj", message)
        
        # 未読メールのスタイル適用
        if not message.is_read():
            self.tree.set(item_id, "tags", ("unread",))
            self.tree.tag_configure("unread", font=self.fonts['unread'])
    
    # イベントハンドラー
    def _on_selection_change_event(self, event):
        """選択変更イベント"""
        selection = self.tree.selection()
        self.selected_messages = []
        
        for item_id in selection:
            # メッセージオブジェクトを取得
            for message in self.filtered_messages:
                tree_values = self.tree.item(item_id, "values")
                if tree_values and len(tree_values) > 1:
                    # 送信者で判定（簡易）
                    if message.sender.startswith(tree_values[1].replace("...", "")):
                        self.selected_messages.append(message)
                        break
        
        # 選択状況を更新
        count = len(self.selected_messages)
        if count == 0:
            self.selection_label.config(text="")
        elif count == 1:
            self.selection_label.config(text="1件選択")
        else:
            self.selection_label.config(text=f"{count}件選択")
        
        # コールバック呼び出し
        if self.on_selection_change:
            self.on_selection_change(self.selected_messages)
    
    def _on_double_click_event(self, event):
        """ダブルクリックイベント"""
        if self.selected_messages and self.on_double_click:
            self.on_double_click(self.selected_messages[0])
    
    def _on_right_click_event(self, event):
        """右クリックイベント"""
        # アイテムを選択
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self._on_selection_change_event(event)
            
            # コンテキストメニューを表示
            try:
                self.context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.context_menu.grab_release()
    
    def _on_column_click(self, column: SortColumn):
        """カラムクリックイベント（ソート）"""
        if self.sort_column == column:
            # 同じカラムの場合は順序を反転
            self.sort_order = SortOrder.ASCENDING if self.sort_order == SortOrder.DESCENDING else SortOrder.DESCENDING
        else:
            # 新しいカラムの場合は降順から開始
            self.sort_column = column
            self.sort_order = SortOrder.DESCENDING
        
        self._apply_filters()
        self._update_display()
        
        # ヘッダーにソートインジケーターを表示
        self._update_sort_indicators()
    
    def _update_sort_indicators(self):
        """ソートインジケーターを更新"""
        # すべてのヘッダーをクリア
        for col in ["flags", "sender", "subject", "date", "size"]:
            self.tree.heading(col, text=self.tree.heading(col)["text"].replace(" ↑", "").replace(" ↓", ""))
        
        # 現在のソートカラムにインジケーター追加
        indicator = " ↑" if self.sort_order == SortOrder.ASCENDING else " ↓"
        
        if self.sort_column == SortColumn.SENDER:
            current_text = self.tree.heading("sender")["text"]
            self.tree.heading("sender", text=current_text + indicator)
        elif self.sort_column == SortColumn.SUBJECT:
            current_text = self.tree.heading("subject")["text"]
            self.tree.heading("subject", text=current_text + indicator)
        elif self.sort_column == SortColumn.DATE:
            current_text = self.tree.heading("date")["text"]
            self.tree.heading("date", text=current_text + indicator)
        elif self.sort_column == SortColumn.SIZE:
            current_text = self.tree.heading("size")["text"]
            self.tree.heading("size", text=current_text + indicator)
    
    def _on_search_change(self, event):
        """検索入力変更イベント"""
        # 遅延検索（0.5秒後に実行）
        if hasattr(self, '_search_timer'):
            self.after_cancel(self._search_timer)
        
        self._search_timer = self.after(500, self._execute_search)
    
    def _on_search_enter(self, event):
        """検索エンター押下イベント"""
        self._execute_search()
    
    def _execute_search(self):
        """検索を実行"""
        self._apply_filters()
        self._update_display()
    
    def _on_filter_change(self, event=None):
        """フィルター変更イベント"""
        self._apply_filters()
        self._update_display()
    
    def _on_filter_clear(self):
        """フィルタークリアイベント"""
        self.unread_only_var.set(False)
        self.flagged_only_var.set(False)
        self.attachments_only_var.set(False)
        self.sender_filter_entry.delete(0, tk.END)
        self.subject_filter_entry.delete(0, tk.END)
        self.search_entry.delete(0, tk.END)
        
        self._apply_filters()
        self._update_display()
    
    def _on_filter_click(self):
        """フィルターボタンクリックイベント"""
        if self.filter_frame.winfo_viewable():
            self.filter_frame.pack_forget()
            self.filter_button.config(text="📋 フィルター")
        else:
            self.filter_frame.pack(fill=tk.X, padx=8, pady=(0, 4), after=self.title_label.master)
            self.filter_button.config(text="📋 フィルター▼")
    
    def _on_preview_toggle(self):
        """プレビュー表示切り替えイベント"""
        self._update_display()
    
    def _on_compact_toggle(self):
        """コンパクト表示切り替えイベント"""
        self._update_display()
    
    # キーボードイベント
    def _on_enter_key(self, event):
        """エンターキーイベント"""
        if self.selected_messages and self.on_double_click:
            self.on_double_click(self.selected_messages[0])
    
    def _on_delete_key(self, event):
        """デリートキーイベント"""
        self._on_delete()
    
    def _on_select_all(self, event):
        """全選択イベント"""
        self.tree.selection_set(self.tree.get_children())
        return "break"
    
    def _on_refresh(self, event):
        """更新イベント"""
        self._update_display()
        return "break"
    
    def _on_focus_search(self, event):
        """検索フォーカスイベント"""
        self.search_entry.focus_set()
        return "break"
    
    def _on_arrow_up(self, event):
        """上矢印キーイベント"""
        selection = self.tree.selection()
        if selection:
            current = selection[0]
            prev_item = self.tree.prev(current)
            if prev_item:
                self.tree.selection_set(prev_item)
                self.tree.see(prev_item)
                return "break"
    
    def _on_arrow_down(self, event):
        """下矢印キーイベント"""
        selection = self.tree.selection()
        if selection:
            current = selection[0]
            next_item = self.tree.next(current)
            if next_item:
                self.tree.selection_set(next_item)
                self.tree.see(next_item)
                return "break"
    
    # コンテキストメニューアクション
    def _on_mark_read(self):
        """既読マークアクション"""
        for message in self.selected_messages:
            message.mark_as_read()
        self._update_display()
    
    def _on_mark_unread(self):
        """未読マークアクション"""
        for message in self.selected_messages:
            message.mark_as_unread()
        self._update_display()
    
    def _on_mark_flagged(self):
        """重要マークアクション"""
        for message in self.selected_messages:
            message.add_flag(MessageFlag.FLAGGED)
        self._update_display()
    
    def _on_unmark_flagged(self):
        """重要解除アクション"""
        for message in self.selected_messages:
            message.remove_flag(MessageFlag.FLAGGED)
        self._update_display()
    
    def _on_reply(self):
        """返信アクション"""
        if self.selected_messages and self.on_context_menu:
            self.on_context_menu("reply", self.selected_messages[0])
    
    def _on_forward(self):
        """転送アクション"""
        if self.selected_messages and self.on_context_menu:
            self.on_context_menu("forward", self.selected_messages[0])
    
    def _on_delete(self):
        """削除アクション"""
        if self.selected_messages and self.on_context_menu:
            result = messagebox.askyesno(
                "確認", 
                f"{len(self.selected_messages)}件のメールを削除しますか？",
                icon=messagebox.QUESTION
            )
            if result:
                self.on_context_menu("delete", self.selected_messages)


# ユーティリティ関数
def create_mail_list(parent, **kwargs) -> MailList:
    """
    メールリストコンポーネントを作成します
    
    Args:
        parent: 親ウィジェット
        **kwargs: MailListのコンストラクタ引数
        
    Returns:
        MailList: 作成されたメールリストコンポーネント
    """
    return MailList(parent, **kwargs)