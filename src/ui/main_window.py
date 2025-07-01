# -*- coding: utf-8 -*-
"""
メインウィンドウモジュール

WabiMailのメインGUIウィンドウを実装します。
侘び寂びの美学に基づいた、シンプルで美しい3ペインレイアウトを提供します。

Author: WabiMail Development Team
Created: 2025-07-01
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import List, Optional, Dict, Any
import threading
from datetime import datetime

from src.mail.account import Account
from src.mail.account_manager import AccountManager
from src.mail.mail_message import MailMessage
from src.mail.mail_client_factory import MailClientFactory
from src.config.app_config import AppConfig
from src.utils.logger import get_logger

# ロガーを取得
logger = get_logger(__name__)


class WabiMailMainWindow:
    """
    WabiMailメインウィンドウクラス
    
    侘び寂びの美学に基づいた、静かで美しいメールクライアントのGUIを提供します。
    3ペインレイアウト（左：アカウント/フォルダ、中央：メール一覧、右：本文表示）を実装し、
    シンプルで使いやすいインターフェースを実現します。
    
    Attributes:
        root (tk.Tk): メインウィンドウ
        config (AppConfig): アプリケーション設定
        account_manager (AccountManager): アカウント管理器
        current_account (Optional[Account]): 現在選択中のアカウント
        current_folder (str): 現在選択中のフォルダ
        current_messages (List[MailMessage]): 現在表示中のメッセージリスト
        selected_message (Optional[MailMessage]): 現在選択中のメッセージ
    """
    
    def __init__(self):
        """
        メインウィンドウを初期化します
        """
        self.root = tk.Tk()
        self.config = AppConfig()
        self.account_manager = AccountManager()
        
        # 状態管理
        self.current_account: Optional[Account] = None
        self.current_folder = "INBOX"
        self.current_messages: List[MailMessage] = []
        self.selected_message: Optional[MailMessage] = None
        
        # UI要素の参照
        self.account_tree = None
        self.message_list = None
        self.message_text = None
        self.status_label = None
        
        # ウィンドウの初期化
        self._setup_window()
        self._create_menu()
        self._create_main_layout()
        self._load_accounts()
        
        logger.info("WabiMailメインウィンドウを初期化しました")
    
    def _setup_window(self):
        """
        メインウィンドウの基本設定を行います
        """
        # ウィンドウタイトルとアイコン
        self.root.title("🌸 WabiMail - 侘び寂びメールクライアント")
        
        # ウィンドウサイズ（黄金比を意識した比率）
        window_width = 1200
        window_height = 750
        
        # 画面中央に配置
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.minsize(800, 500)
        
        # 侘び寂びスタイルの設定
        self._setup_wabi_sabi_style()
        
        # 終了時の処理
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _setup_wabi_sabi_style(self):
        """
        侘び寂びの美学に基づいたスタイルを設定します
        """
        # ベースカラー（和紙色）
        bg_color = "#fefefe"        # 和紙白
        accent_color = "#f5f5f5"    # 薄いグレー
        text_color = "#333333"      # 墨色
        select_color = "#ffe8e8"    # 薄桜色
        
        # ルートウィンドウの背景色
        self.root.configure(bg=bg_color)
        
        # TTKスタイルの設定
        style = ttk.Style()
        
        # Treeviewスタイル（アカウント・メールリスト用）
        style.configure("Wabi.Treeview",
                       background=bg_color,
                       foreground=text_color,
                       fieldbackground=bg_color,
                       selectbackground=select_color,
                       selectforeground=text_color,
                       borderwidth=1,
                       relief="flat")
        
        style.configure("Wabi.Treeview.Heading",
                       background=accent_color,
                       foreground=text_color,
                       font=("Yu Gothic UI", 10, "normal"))
        
        # PanedWindowスタイル
        style.configure("Wabi.TPanedwindow",
                       background=bg_color,
                       borderwidth=1)
        
        # Frameスタイル
        style.configure("Wabi.TFrame",
                       background=bg_color,
                       borderwidth=0)
        
        # Labelスタイル
        style.configure("Wabi.TLabel",
                       background=bg_color,
                       foreground=text_color,
                       font=("Yu Gothic UI", 9))
        
        # Buttonスタイル
        style.configure("Wabi.TButton",
                       background=accent_color,
                       foreground=text_color,
                       borderwidth=1,
                       focuscolor="none",
                       font=("Yu Gothic UI", 9))
        
        style.map("Wabi.TButton",
                 background=[("active", select_color),
                           ("pressed", "#f0f0f0")])
    
    def _create_menu(self):
        """
        メニューバーを作成します
        """
        menubar = tk.Menu(self.root, bg="#fefefe", fg="#333333")
        self.root.config(menu=menubar)
        
        # ファイルメニュー
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="ファイル", menu=file_menu)
        file_menu.add_command(label="新規メール作成", command=self._create_new_message)
        file_menu.add_separator()
        file_menu.add_command(label="アカウント追加", command=self._add_account)
        file_menu.add_separator()
        file_menu.add_command(label="終了", command=self._on_closing)
        
        # 表示メニュー
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="表示", menu=view_menu)
        view_menu.add_command(label="最新の情報に更新", command=self._refresh_current_folder)
        view_menu.add_separator()
        view_menu.add_command(label="フォルダを展開", command=self._expand_all_folders)
        view_menu.add_command(label="フォルダを折りたたみ", command=self._collapse_all_folders)
        
        # ヘルプメニュー
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="ヘルプ", menu=help_menu)
        help_menu.add_command(label="WabiMailについて", command=self._show_about)
    
    def _create_main_layout(self):
        """
        メインレイアウト（3ペイン）を作成します
        """
        # メインコンテナ
        main_frame = ttk.Frame(self.root, style="Wabi.TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        
        # ツールバー
        self._create_toolbar(main_frame)
        
        # 3ペインのPanedWindow
        self.main_paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL, style="Wabi.TPanedwindow")
        self.main_paned.pack(fill=tk.BOTH, expand=True, pady=(8, 0))
        
        # 左ペイン：アカウント・フォルダツリー
        self._create_account_pane()
        
        # 中央・右ペイン用のPanedWindow
        self.content_paned = ttk.PanedWindow(self.main_paned, orient=tk.HORIZONTAL, style="Wabi.TPanedwindow")
        self.main_paned.add(self.content_paned, weight=3)
        
        # 中央ペイン：メール一覧
        self._create_message_list_pane()
        
        # 右ペイン：メール本文表示
        self._create_message_view_pane()
        
        # ステータスバー
        self._create_status_bar(main_frame)
        
        # 初期サイズ調整
        self.root.after(100, self._adjust_pane_sizes)
    
    def _create_toolbar(self, parent):
        """
        ツールバーを作成します
        
        Args:
            parent: 親ウィジェット
        """
        toolbar_frame = ttk.Frame(parent, style="Wabi.TFrame")
        toolbar_frame.pack(fill=tk.X, pady=(0, 4))
        
        # 新規メール作成ボタン
        ttk.Button(toolbar_frame, text="📝 新規メール作成", 
                  command=self._create_new_message, 
                  style="Wabi.TButton").pack(side=tk.LEFT, padx=(0, 8))
        
        # 更新ボタン
        ttk.Button(toolbar_frame, text="🔄 更新", 
                  command=self._refresh_current_folder, 
                  style="Wabi.TButton").pack(side=tk.LEFT, padx=(0, 8))
        
        # アカウント追加ボタン
        ttk.Button(toolbar_frame, text="➕ アカウント追加", 
                  command=self._add_account, 
                  style="Wabi.TButton").pack(side=tk.LEFT, padx=(0, 8))
        
        # 検索フィールド（将来拡張用）
        search_frame = ttk.Frame(toolbar_frame, style="Wabi.TFrame")
        search_frame.pack(side=tk.RIGHT)
        
        ttk.Label(search_frame, text="🔍", style="Wabi.TLabel").pack(side=tk.LEFT, padx=(0, 4))
        self.search_entry = tk.Entry(search_frame, width=20, 
                                    bg="#fefefe", fg="#333333", 
                                    font=("Yu Gothic UI", 9))
        self.search_entry.pack(side=tk.LEFT)
        self.search_entry.bind("<Return>", self._on_search)
    
    def _create_account_pane(self):
        """
        左ペイン：アカウント・フォルダツリーを作成します
        """
        # アカウントペインフレーム
        account_frame = ttk.Frame(self.main_paned, style="Wabi.TFrame")
        self.main_paned.add(account_frame, weight=1)
        
        # タイトル
        ttk.Label(account_frame, text="📧 アカウント・フォルダ", 
                 style="Wabi.TLabel", font=("Yu Gothic UI", 10, "bold")).pack(
                 fill=tk.X, padx=8, pady=(8, 4))
        
        # ツリービュー
        tree_frame = ttk.Frame(account_frame, style="Wabi.TFrame")
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))
        
        # スクロールバー付きツリービュー
        tree_scroll = ttk.Scrollbar(tree_frame)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.account_tree = ttk.Treeview(tree_frame, style="Wabi.Treeview",
                                        yscrollcommand=tree_scroll.set)
        self.account_tree.pack(fill=tk.BOTH, expand=True)
        tree_scroll.config(command=self.account_tree.yview)
        
        # ツリービューの設定
        self.account_tree.heading("#0", text="アカウント・フォルダ", anchor=tk.W)
        self.account_tree.column("#0", width=200, minwidth=150)
        
        # イベントバインド
        self.account_tree.bind("<<TreeviewSelect>>", self._on_account_tree_select)
        self.account_tree.bind("<Double-1>", self._on_account_tree_double_click)
    
    def _create_message_list_pane(self):
        """
        中央ペイン：メール一覧を作成します
        """
        # メール一覧ペインフレーム
        list_frame = ttk.Frame(self.content_paned, style="Wabi.TFrame")
        self.content_paned.add(list_frame, weight=2)
        
        # タイトル
        self.list_title_label = ttk.Label(list_frame, text="📥 メール一覧", 
                                         style="Wabi.TLabel", font=("Yu Gothic UI", 10, "bold"))
        self.list_title_label.pack(fill=tk.X, padx=8, pady=(8, 4))
        
        # メール一覧
        list_content_frame = ttk.Frame(list_frame, style="Wabi.TFrame")
        list_content_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))
        
        # スクロールバー付きTreeview
        list_scroll = ttk.Scrollbar(list_content_frame)
        list_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # メール一覧のカラム設定
        columns = ("flags", "sender", "subject", "date")
        self.message_list = ttk.Treeview(list_content_frame, style="Wabi.Treeview",
                                        columns=columns, show="headings",
                                        yscrollcommand=list_scroll.set)
        self.message_list.pack(fill=tk.BOTH, expand=True)
        list_scroll.config(command=self.message_list.yview)
        
        # カラムヘッダー設定
        self.message_list.heading("flags", text="", anchor=tk.W)
        self.message_list.heading("sender", text="送信者", anchor=tk.W)
        self.message_list.heading("subject", text="件名", anchor=tk.W)
        self.message_list.heading("date", text="日時", anchor=tk.W)
        
        # カラム幅設定
        self.message_list.column("flags", width=40, minwidth=30)
        self.message_list.column("sender", width=150, minwidth=100)
        self.message_list.column("subject", width=300, minwidth=200)
        self.message_list.column("date", width=120, minwidth=100)
        
        # イベントバインド
        self.message_list.bind("<<TreeviewSelect>>", self._on_message_select)
        self.message_list.bind("<Double-1>", self._on_message_double_click)
    
    def _create_message_view_pane(self):
        """
        右ペイン：メール本文表示を作成します
        """
        # メール表示ペインフレーム
        view_frame = ttk.Frame(self.content_paned, style="Wabi.TFrame")
        self.content_paned.add(view_frame, weight=2)
        
        # タイトルとアクションボタン
        view_header = ttk.Frame(view_frame, style="Wabi.TFrame")
        view_header.pack(fill=tk.X, padx=8, pady=(8, 4))
        
        ttk.Label(view_header, text="📖 メール内容", 
                 style="Wabi.TLabel", font=("Yu Gothic UI", 10, "bold")).pack(side=tk.LEFT)
        
        # アクションボタン
        action_frame = ttk.Frame(view_header, style="Wabi.TFrame")
        action_frame.pack(side=tk.RIGHT)
        
        ttk.Button(action_frame, text="↩️ 返信", 
                  command=self._reply_message, 
                  style="Wabi.TButton").pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(action_frame, text="↪️ 転送", 
                  command=self._forward_message, 
                  style="Wabi.TButton").pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(action_frame, text="🗑️ 削除", 
                  command=self._delete_message, 
                  style="Wabi.TButton").pack(side=tk.LEFT)
        
        # メール本文表示エリア
        text_frame = ttk.Frame(view_frame, style="Wabi.TFrame")
        text_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))
        
        # スクロールバー付きテキストウィジェット
        text_scroll = ttk.Scrollbar(text_frame)
        text_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.message_text = tk.Text(text_frame, 
                                   bg="#fefefe", fg="#333333",
                                   font=("Yu Gothic UI", 10),
                                   wrap=tk.WORD, state=tk.DISABLED,
                                   yscrollcommand=text_scroll.set)
        self.message_text.pack(fill=tk.BOTH, expand=True)
        text_scroll.config(command=self.message_text.yview)
    
    def _create_status_bar(self, parent):
        """
        ステータスバーを作成します
        
        Args:
            parent: 親ウィジェット
        """
        status_frame = ttk.Frame(parent, style="Wabi.TFrame", relief=tk.SUNKEN, borderwidth=1)
        status_frame.pack(fill=tk.X, pady=(4, 0))
        
        self.status_label = ttk.Label(status_frame, text="WabiMailへようこそ", 
                                     style="Wabi.TLabel")
        self.status_label.pack(side=tk.LEFT, padx=4, pady=2)
        
        # 接続状態表示
        self.connection_label = ttk.Label(status_frame, text="", 
                                         style="Wabi.TLabel")
        self.connection_label.pack(side=tk.RIGHT, padx=4, pady=2)
    
    def _adjust_pane_sizes(self):
        """
        ペインの初期サイズを調整します
        """
        # メインペインの調整（左ペイン：その他 = 1:4）
        total_width = self.root.winfo_width()
        left_width = total_width // 5
        self.main_paned.sashpos(0, left_width)
        
        # コンテンツペインの調整（中央：右 = 1:1）
        content_width = total_width - left_width
        self.content_paned.sashpos(0, content_width // 2)
    
    def _load_accounts(self):
        """
        保存されているアカウントを読み込みます
        """
        try:
            accounts = self.account_manager.list_accounts()
            
            if not accounts:
                # アカウントが未登録の場合
                self._update_status("アカウントが登録されていません。アカウントを追加してください。")
                self._show_welcome_message()
            else:
                # アカウントをツリーに追加
                for account in accounts:
                    self._add_account_to_tree(account)
                
                # 最初のアカウントを選択
                if accounts:
                    self._select_account(accounts[0])
                
                self._update_status(f"{len(accounts)}個のアカウントを読み込みました")
            
        except Exception as e:
            logger.error(f"アカウント読み込みエラー: {e}")
            self._update_status("アカウントの読み込みに失敗しました")
    
    def _add_account_to_tree(self, account: Account):
        """
        アカウントをツリーに追加します
        
        Args:
            account: 追加するアカウント
        """
        # アカウントノードを追加
        account_icon = "📧" if account.account_type.value == "gmail" else "📬"
        account_node = self.account_tree.insert("", "end", 
                                               text=f"{account_icon} {account.name}",
                                               values=(account.account_id,))
        
        # 標準フォルダを追加
        folders = ["受信トレイ", "送信済み", "下書き", "迷惑メール", "ゴミ箱"]
        folder_icons = ["📥", "📤", "📝", "⚠️", "🗑️"]
        
        for folder, icon in zip(folders, folder_icons):
            self.account_tree.insert(account_node, "end",
                                   text=f"{icon} {folder}",
                                   values=(account.account_id, folder))
    
    def _show_welcome_message(self):
        """
        ウェルカムメッセージを表示します
        """
        welcome_text = """🌸 WabiMailへようこそ

侘び寂びの美学に基づいた、静かで美しいメールクライアントです。

はじめに、メールアカウントを追加してください：
• 「アカウント追加」ボタンをクリック
• Gmail、IMAP、SMTP、POP3に対応
• 複数のアカウントを一つの画面で管理

WabiMailは、シンプルで心地よいメール体験を提供します。
余計な装飾を省き、本質的な機能に集中した設計です。

どうぞごゆっくりお楽しみください。"""
        
        self.message_text.config(state=tk.NORMAL)
        self.message_text.delete(1.0, tk.END)
        self.message_text.insert(1.0, welcome_text)
        self.message_text.config(state=tk.DISABLED)
    
    def _select_account(self, account: Account):
        """
        アカウントを選択します
        
        Args:
            account: 選択するアカウント
        """
        self.current_account = account
        self.current_folder = "INBOX"
        self._update_status(f"アカウント「{account.name}」を選択しました")
        self._load_messages()
    
    def _load_messages(self):
        """
        現在選択中のアカウント・フォルダのメッセージを読み込みます
        """
        if not self.current_account:
            return
        
        def load_in_background():
            """
            バックグラウンドでメッセージを読み込みます
            """
            try:
                self._update_status("メッセージを読み込み中...")
                self._update_connection_status("接続中...")
                
                # メール受信クライアントを作成
                client = MailClientFactory.create_receive_client(self.current_account)
                if not client:
                    raise Exception("メールクライアントを作成できませんでした")
                
                # 接続テスト（実際の認証情報がある場合のみ）
                success, message = client.test_connection()
                if not success:
                    logger.warning(f"接続テスト失敗: {message}")
                    # 実際の環境では認証情報がないため、サンプルメッセージを作成
                    messages = self._create_sample_messages()
                else:
                    # 実際の接続が成功した場合
                    messages = client.fetch_messages(limit=50)
                
                # UIスレッドで結果を更新
                self.root.after(0, lambda: self._update_message_list(messages))
                self.root.after(0, lambda: self._update_status(f"{len(messages)}件のメッセージを読み込みました"))
                self.root.after(0, lambda: self._update_connection_status("オフライン（サンプルデータ）"))
                
            except Exception as e:
                logger.error(f"メッセージ読み込みエラー: {e}")
                # サンプルメッセージを表示
                messages = self._create_sample_messages()
                self.root.after(0, lambda: self._update_message_list(messages))
                self.root.after(0, lambda: self._update_status("サンプルメッセージを表示しています"))
                self.root.after(0, lambda: self._update_connection_status("オフライン（サンプルデータ）"))
        
        # バックグラウンドスレッドで実行
        thread = threading.Thread(target=load_in_background, daemon=True)
        thread.start()
    
    def _create_sample_messages(self) -> List[MailMessage]:
        """
        サンプルメッセージを作成します（開発・デモ用）
        
        Returns:
            List[MailMessage]: サンプルメッセージのリスト
        """
        from src.mail.mail_message import MailMessage, MessageFlag
        
        messages = []
        
        # サンプルメッセージ1
        msg1 = MailMessage(
            subject="🌸 WabiMail開発進捗報告",
            sender="dev-team@wabimail.example.com",
            recipients=[self.current_account.email_address],
            body_text="""WabiMail開発チームです。

基本GUI実装が完了いたしました。

【完了した機能】
• 3ペインレイアウト
• アカウント管理
• メール一覧表示
• 本文表示機能

侘び寂びの美学に基づいた、静かで美しいインターフェースをお楽しみください。

--
WabiMail開発チーム
🌸 静寂の中の美しさを追求して""",
            date_received=datetime.now()
        )
        msg1.add_flag(MessageFlag.FLAGGED)
        messages.append(msg1)
        
        # サンプルメッセージ2
        msg2 = MailMessage(
            subject="メール通信テスト",
            sender="test@example.com",
            recipients=[self.current_account.email_address],
            body_text="これはメール通信機能のテストメッセージです。",
            date_received=datetime.now()
        )
        messages.append(msg2)
        
        # サンプルメッセージ3
        msg3 = MailMessage(
            subject="侘び寂びの美学について",
            sender="philosophy@wabimail.example.com",
            recipients=[self.current_account.email_address],
            body_text="""侘び寂び（わびさび）は、日本古来の美意識の一つです。

「侘び」は、質素で静かなものの中に美しさを見出すこと。
「寂び」は、時間の経過とともに生まれる風情や趣を愛でること。

WabiMailは、この精神をデジタルの世界に取り入れ、
シンプルで心地よいメール体験を提供します。

余計な装飾を省き、本質的な機能に集中することで、
使う人の心に静かな安らぎをもたらします。""",
            date_received=datetime.now()
        )
        msg3.mark_as_read()
        messages.append(msg3)
        
        return messages
    
    def _update_message_list(self, messages: List[MailMessage]):
        """
        メッセージ一覧を更新します
        
        Args:
            messages: 表示するメッセージリスト
        """
        # 既存のアイテムをクリア
        for item in self.message_list.get_children():
            self.message_list.delete(item)
        
        # メッセージを追加
        self.current_messages = messages
        
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
            
            # 送信者表示
            sender = message.sender
            if len(sender) > 20:
                sender = sender[:17] + "..."
            
            # 件名表示
            subject = message.subject
            if len(subject) > 40:
                subject = subject[:37] + "..."
            
            # 日時表示
            date_str = message.get_display_date().strftime("%m/%d %H:%M")
            
            # アイテムを追加
            item_id = self.message_list.insert("", "end", 
                                              values=(flags, sender, subject, date_str))
            
            # メッセージオブジェクトを関連付け
            self.message_list.set(item_id, "message_obj", message)
        
        # タイトルを更新
        folder_name = "受信トレイ"  # 現在は固定
        self.list_title_label.config(text=f"📥 {folder_name} ({len(messages)}件)")
    
    def _update_status(self, message: str):
        """
        ステータスを更新します
        
        Args:
            message: ステータスメッセージ
        """
        if self.status_label:
            self.status_label.config(text=message)
    
    def _update_connection_status(self, status: str):
        """
        接続状態を更新します
        
        Args:
            status: 接続状態メッセージ
        """
        if self.connection_label:
            self.connection_label.config(text=status)
    
    # イベントハンドラー
    def _on_account_tree_select(self, event):
        """
        アカウントツリー選択イベント
        """
        selection = self.account_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        values = self.account_tree.item(item, "values")
        
        if len(values) >= 1:
            account_id = values[0]
            
            # アカウントを検索
            account = self.account_manager.get_account(account_id)
            if account and account != self.current_account:
                self._select_account(account)
            
            # フォルダが選択された場合
            if len(values) >= 2:
                folder = values[1]
                if folder != self.current_folder:
                    self.current_folder = folder
                    self._load_messages()
    
    def _on_account_tree_double_click(self, event):
        """
        アカウントツリーダブルクリックイベント
        """
        selection = self.account_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        values = self.account_tree.item(item, "values")
        
        # アカウントノードの場合のみ編集ダイアログを開く
        if len(values) >= 1 and len(values) < 2:  # フォルダではなくアカウント
            account_id = values[0]
            account = self.account_manager.get_account(account_id)
            
            if account:
                self._edit_account(account)
    
    def _edit_account(self, account: Account):
        """
        アカウントを編集します
        
        Args:
            account: 編集対象のアカウント
        """
        try:
            from src.ui.account_dialog import show_account_dialog
            
            def on_account_updated(updated_account):
                """アカウント更新成功時のコールバック"""
                # ツリー表示を更新
                self._refresh_account_tree()
                
                # 更新されたアカウントを選択
                self._select_account(updated_account)
                
                self._update_status(f"アカウント「{updated_account.name}」を更新しました")
                logger.info(f"アカウントを更新しました: {updated_account.email_address}")
            
            # アカウント設定ダイアログを表示（編集モード）
            result = show_account_dialog(self.root, account=account, success_callback=on_account_updated)
            
            if not result:
                self._update_status("アカウント編集がキャンセルされました")
                
        except Exception as e:
            logger.error(f"アカウント編集エラー: {e}")
            self._update_status("アカウント編集でエラーが発生しました")
            messagebox.showerror("エラー", f"アカウント編集でエラーが発生しました: {e}")
    
    def _refresh_account_tree(self):
        """
        アカウントツリーを再構築します
        """
        # 既存のアイテムをクリア
        for item in self.account_tree.get_children():
            self.account_tree.delete(item)
        
        # アカウントを再読み込み
        self._load_accounts()
    
    def _on_message_select(self, event):
        """
        メッセージ選択イベント
        """
        selection = self.message_list.selection()
        if not selection:
            return
        
        item = selection[0]
        # メッセージオブジェクトを取得
        for message in self.current_messages:
            if self.message_list.item(item, "values")[1] in message.sender:
                self.selected_message = message
                self._display_message(message)
                break
    
    def _on_message_double_click(self, event):
        """
        メッセージダブルクリックイベント
        """
        if self.selected_message:
            # 別ウィンドウでメッセージを開く（将来実装）
            pass
    
    def _on_search(self, event):
        """
        検索イベント
        """
        query = self.search_entry.get().strip()
        if query:
            self._update_status(f"「{query}」を検索中...")
            # TODO: 検索機能の実装
        else:
            self._load_messages()
    
    def _display_message(self, message: MailMessage):
        """
        メッセージを表示します
        
        Args:
            message: 表示するメッセージ
        """
        self.message_text.config(state=tk.NORMAL)
        self.message_text.delete(1.0, tk.END)
        
        # ヘッダー情報
        header_text = f"""差出人: {message.sender}
宛先: {', '.join(message.recipients)}
件名: {message.subject}
日時: {message.get_display_date().strftime('%Y年%m月%d日 %H:%M:%S')}

{'='*50}

"""
        
        # 本文
        body_text = message.body_text or "[本文なし]"
        
        # 添付ファイル情報
        if message.has_attachments():
            attachment_text = f"\n\n{'='*50}\n添付ファイル ({message.get_attachment_count()}件):\n"
            for i, attachment in enumerate(message.attachments, 1):
                attachment_text += f"{i}. {attachment.filename} ({attachment.size:,}バイト)\n"
        else:
            attachment_text = ""
        
        # 全体のテキストを設定
        full_text = header_text + body_text + attachment_text
        self.message_text.insert(1.0, full_text)
        self.message_text.config(state=tk.DISABLED)
        
        # 未読メッセージの場合は既読にマーク
        if not message.is_read():
            message.mark_as_read()
            # UI更新（実際の実装では保存も必要）
            self._refresh_message_list_item(message)
    
    def _refresh_message_list_item(self, message: MailMessage):
        """
        メッセージリストの特定アイテムを更新します
        
        Args:
            message: 更新するメッセージ
        """
        # 該当アイテムを検索してフラグを更新
        for item_id in self.message_list.get_children():
            item_values = self.message_list.item(item_id, "values")
            if item_values[1] in message.sender:  # 送信者で判定（簡易）
                # フラグを更新
                flags = ""
                if message.is_read():
                    flags += "📖"
                else:
                    flags += "📩"
                if message.is_flagged():
                    flags += "⭐"
                if message.has_attachments():
                    flags += "📎"
                
                # アイテムを更新
                values = list(item_values)
                values[0] = flags
                self.message_list.item(item_id, values=values)
                break
    
    # メニューアクション
    def _create_new_message(self):
        """
        新規メール作成
        """
        self._update_status("新規メール作成画面を開きます...")
        # TODO: メール作成画面の実装
    
    def _add_account(self):
        """
        アカウント追加
        """
        self._update_status("アカウント追加画面を開きます...")
        
        try:
            from src.ui.account_dialog import show_account_dialog
            
            def on_account_added(account):
                """アカウント追加成功時のコールバック"""
                # ツリーにアカウントを追加
                self._add_account_to_tree(account)
                
                # 追加されたアカウントを選択
                self._select_account(account)
                
                self._update_status(f"アカウント「{account.name}」を追加しました")
                logger.info(f"アカウントを追加しました: {account.email_address}")
            
            # アカウント設定ダイアログを表示
            result = show_account_dialog(self.root, success_callback=on_account_added)
            
            if not result:
                self._update_status("アカウント追加がキャンセルされました")
                
        except Exception as e:
            logger.error(f"アカウント追加エラー: {e}")
            self._update_status("アカウント追加でエラーが発生しました")
            messagebox.showerror("エラー", f"アカウント追加でエラーが発生しました: {e}")
    
    def _refresh_current_folder(self):
        """
        現在のフォルダを更新
        """
        if self.current_account:
            self._load_messages()
        else:
            self._update_status("アカウントが選択されていません")
    
    def _expand_all_folders(self):
        """
        すべてのフォルダを展開
        """
        for item in self.account_tree.get_children():
            self.account_tree.item(item, open=True)
    
    def _collapse_all_folders(self):
        """
        すべてのフォルダを折りたたみ
        """
        for item in self.account_tree.get_children():
            self.account_tree.item(item, open=False)
    
    def _reply_message(self):
        """
        メッセージに返信
        """
        if self.selected_message:
            self._update_status(f"「{self.selected_message.subject}」に返信...")
            # TODO: 返信画面の実装
    
    def _forward_message(self):
        """
        メッセージを転送
        """
        if self.selected_message:
            self._update_status(f"「{self.selected_message.subject}」を転送...")
            # TODO: 転送画面の実装
    
    def _delete_message(self):
        """
        メッセージを削除
        """
        if self.selected_message:
            result = messagebox.askyesno("確認", 
                                       f"「{self.selected_message.subject}」を削除しますか？",
                                       icon=messagebox.QUESTION)
            if result:
                self._update_status("メッセージを削除しました")
                # TODO: 実際の削除処理
    
    def _show_about(self):
        """
        WabiMailについて
        """
        about_text = """🌸 WabiMail - 侘び寂びメールクライアント

バージョン: 1.0.0 開発版
作成者: WabiMail Development Team

侘び寂びの美学に基づいた、静かで美しいメールクライアント。
シンプルで心地よいメール体験を提供します。

• 複数アカウント対応（Gmail、IMAP、SMTP、POP3）
• 3ペインレイアウト
• 和の美意識を取り入れたデザイン
• オープンソース・無料

🌸 静寂の中の美しさを追求して"""
        
        messagebox.showinfo("WabiMailについて", about_text)
    
    def _on_closing(self):
        """
        ウィンドウ終了処理
        """
        logger.info("WabiMailを終了します")
        self.root.destroy()
    
    def run(self):
        """
        メインループを開始します
        """
        logger.info("WabiMail GUIを開始します")
        self.root.mainloop()


def main():
    """
    メイン関数
    """
    try:
        app = WabiMailMainWindow()
        app.run()
    except Exception as e:
        logger.error(f"アプリケーション起動エラー: {e}")
        print(f"エラー: {e}")


if __name__ == "__main__":
    main()