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
from src.mail.mail_message import MailMessage, MessageFlag
from src.mail.mail_client_factory import MailClientFactory
from src.config.app_config import AppConfig
from src.ui.mail_list import MailList
from src.ui.mail_viewer import MailViewer
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
        self.mail_list = None
        self.mail_viewer = None
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
        
        # 設定メニュー
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="設定", menu=settings_menu)
        settings_menu.add_command(label="🛠️ 設定画面", command=self._show_settings)
        settings_menu.add_separator()
        settings_menu.add_command(label="⚙️ アカウント設定", command=self._show_account_settings)
        
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
        
        # 新しいMailListコンポーネントを使用
        self.mail_list = MailList(list_frame,
                                 on_selection_change=self._on_mail_selection_change,
                                 on_double_click=self._on_mail_double_click,
                                 on_context_menu=self._on_mail_context_menu)
        self.mail_list.pack(fill=tk.BOTH, expand=True)
    
    def _create_message_view_pane(self):
        """
        右ペイン：メール本文表示を作成します
        """
        # メール表示ペインフレーム
        view_frame = ttk.Frame(self.content_paned, style="Wabi.TFrame")
        self.content_paned.add(view_frame, weight=2)
        
        # 新しいMailViewerコンポーネントを使用
        self.mail_viewer = MailViewer(view_frame,
                                     on_reply=self._on_mail_reply,
                                     on_forward=self._on_mail_forward,
                                     on_delete=self._on_mail_delete)
        self.mail_viewer.pack(fill=tk.BOTH, expand=True)
    
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
        # 新しいMailListコンポーネントを使用
        self.current_messages = messages
        folder_name = "受信トレイ"  # 現在は固定
        self.mail_list.set_messages(messages, folder_name)
    
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
    
    def _on_mail_selection_change(self, selected_messages: List[MailMessage]):
        """
        メール選択変更イベント
        
        Args:
            selected_messages: 選択されたメッセージリスト
        """
        if selected_messages:
            self.selected_message = selected_messages[0]
            self.mail_viewer.display_message(self.selected_message)
        else:
            self.selected_message = None
            self.mail_viewer.display_message(None)
    
    def _on_mail_double_click(self, message: MailMessage):
        """
        メールダブルクリックイベント
        
        Args:
            message: ダブルクリックされたメッセージ
        """
        # 将来的に別ウィンドウでメール表示等の機能を実装
        logger.info(f"メールをダブルクリック: {message.subject}")
    
    def _on_mail_context_menu(self, action: str, data):
        """
        メールコンテキストメニューイベント
        
        Args:
            action: アクション名
            data: アクションデータ（メッセージまたはメッセージリスト）
        """
        if action == "reply":
            self._on_mail_reply(data, reply_all=False)
        elif action == "forward":
            self._on_mail_forward(data)
        elif action == "delete":
            self._on_mail_delete(data)
    
    def _on_mail_reply(self, data, reply_all=False):
        """
        メール返信処理
        
        Args:
            data: 返信対象のメッセージまたはメッセージリスト
            reply_all: 全員に返信かどうか
        """
        message = data if isinstance(data, MailMessage) else data[0] if data else None
        if not message:
            return
            
        if not self.current_account:
            messagebox.showwarning(
                "アカウント未選択",
                "返信するには、まずアカウントを選択してください。",
                parent=self.root
            )
            return
        
        reply_type = "全員に返信" if reply_all else "返信"
        self._update_status(f"「{message.subject}」に{reply_type}...")
        
        try:
            from src.ui.compose_window import show_compose_window
            
            def on_reply_sent(reply_message):
                """返信送信完了時のコールバック"""
                self._update_status(f"✅ 返信を送信しました: {reply_message.subject}")
                # 元メッセージに返信済みフラグを追加
                if not message.has_flag(MessageFlag.ANSWERED):
                    message.add_flag(MessageFlag.ANSWERED)
                    self.mail_list.refresh_message_display(message)
                logger.info(f"返信送信完了: {reply_message.subject}")
            
            # 返信ウィンドウを表示
            compose_window = show_compose_window(
                parent=self.root,
                account=self.current_account,
                message_type="reply",
                original_message=message,
                on_sent=on_reply_sent
            )
            
            if compose_window:
                logger.info(f"返信画面を開きました: {message.subject}")
            else:
                self._update_status("返信画面の表示に失敗しました")
                
        except Exception as e:
            logger.error(f"返信処理エラー: {e}")
            self._update_status("返信画面でエラーが発生しました")
            messagebox.showerror(
                "エラー",
                f"返信画面の表示でエラーが発生しました:\n{e}",
                parent=self.root
            )
    
    def _on_mail_forward(self, data):
        """
        メール転送処理
        
        Args:
            data: 転送対象のメッセージまたはメッセージリスト
        """
        message = data if isinstance(data, MailMessage) else data[0] if data else None
        if not message:
            return
            
        if not self.current_account:
            messagebox.showwarning(
                "アカウント未選択",
                "転送するには、まずアカウントを選択してください。",
                parent=self.root
            )
            return
        
        self._update_status(f"「{message.subject}」を転送...")
        
        try:
            from src.ui.compose_window import show_compose_window
            
            def on_forward_sent(forward_message):
                """転送送信完了時のコールバック"""
                self._update_status(f"✅ 転送を送信しました: {forward_message.subject}")
                logger.info(f"転送送信完了: {forward_message.subject}")
            
            # 転送ウィンドウを表示
            compose_window = show_compose_window(
                parent=self.root,
                account=self.current_account,
                message_type="forward",
                original_message=message,
                on_sent=on_forward_sent
            )
            
            if compose_window:
                logger.info(f"転送画面を開きました: {message.subject}")
            else:
                self._update_status("転送画面の表示に失敗しました")
                
        except Exception as e:
            logger.error(f"転送処理エラー: {e}")
            self._update_status("転送画面でエラーが発生しました")
            messagebox.showerror(
                "エラー",
                f"転送画面の表示でエラーが発生しました:\n{e}",
                parent=self.root
            )
    
    def _on_mail_delete(self, data):
        """
        メール削除処理
        
        Args:
            data: 削除対象のメッセージまたはメッセージリスト
        """
        messages = data if isinstance(data, list) else [data] if data else []
        if messages:
            if len(messages) == 1:
                result = messagebox.askyesno("確認", 
                                           f"「{messages[0].subject}」を削除しますか？",
                                           icon=messagebox.QUESTION)
            else:
                result = messagebox.askyesno("確認", 
                                           f"{len(messages)}件のメッセージを削除しますか？",
                                           icon=messagebox.QUESTION)
            
            if result:
                for message in messages:
                    logger.info(f"メール削除処理: {message.subject}")
                    # TODO: 実際の削除処理
                    pass
                self._update_status(f"{len(messages)}件のメッセージを削除しました")
    
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
        メッセージを表示します（新しいMailViewerコンポーネントを使用）
        
        Args:
            message: 表示するメッセージ
        """
        # 新しいMailViewerコンポーネントを使用してメッセージを表示
        self.mail_viewer.display_message(message)
        
        # 未読メッセージの場合は既読にマーク
        if message and not message.is_read():
            message.mark_as_read()
            # MailListの表示を更新
            self.mail_list.refresh_message_display(message)
            logger.info(f"メッセージを既読にマーク: {message.subject}")
    
    def _refresh_message_list_item(self, message: MailMessage):
        """
        メッセージリストの特定アイテムを更新します（新しいMailListコンポーネント用）
        
        Args:
            message: 更新するメッセージ
        """
        # 新しいMailListコンポーネントのrefresh_message_displayメソッドを使用
        if hasattr(self.mail_list, 'refresh_message_display'):
            self.mail_list.refresh_message_display(message)
        else:
            # フォールバック: メッセージリスト全体を再更新
            self.mail_list.set_messages(self.current_messages, "受信トレイ")
    
    # メニューアクション
    def _create_new_message(self):
        """
        新規メール作成
        """
        if not self.current_account:
            messagebox.showwarning(
                "アカウント未選択",
                "メールを作成するには、まずアカウントを選択してください。",
                parent=self.root
            )
            return
        
        self._update_status("新規メール作成画面を開きます...")
        
        try:
            from src.ui.compose_window import show_compose_window
            
            def on_message_sent(message):
                """メール送信完了時のコールバック"""
                self._update_status(f"✅ メールを送信しました: {message.subject}")
                # 送信済みフォルダに追加（将来実装）
                logger.info(f"メール送信完了: {message.subject}")
            
            # メール作成ウィンドウを表示
            compose_window = show_compose_window(
                parent=self.root,
                account=self.current_account,
                message_type="new",
                on_sent=on_message_sent
            )
            
            if compose_window:
                logger.info("新規メール作成画面を開きました")
            else:
                self._update_status("メール作成画面の表示に失敗しました")
                
        except Exception as e:
            logger.error(f"新規メール作成エラー: {e}")
            self._update_status("メール作成画面でエラーが発生しました")
            messagebox.showerror(
                "エラー",
                f"メール作成画面の表示でエラーが発生しました:\n{e}",
                parent=self.root
            )
    
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
            self._on_mail_reply(self.selected_message, reply_all=False)
    
    def _forward_message(self):
        """
        メッセージを転送
        """
        if self.selected_message:
            self._on_mail_forward(self.selected_message)
    
    def _delete_message(self):
        """
        メッセージを削除
        """
        if self.selected_message:
            self._on_mail_delete(self.selected_message)
    
    def _show_settings(self):
        """
        設定画面を表示
        """
        try:
            from src.ui.settings_window import show_settings_window
            
            def on_settings_changed(changed_settings):
                """設定変更時のコールバック"""
                logger.info("設定が変更されました")
                self._update_status("⚙️ 設定が更新されました")
                
                # UI関連の設定が変更された場合はスタイルを再適用
                if any(key.startswith(('ui.', 'app.theme')) for key in changed_settings.keys()):
                    self._setup_wabi_sabi_style()
                    logger.info("UIスタイルを再適用しました")
            
            settings_window = show_settings_window(
                parent=self.root,
                config=self.config,
                on_settings_changed=on_settings_changed
            )
            
            if settings_window:
                self._update_status("🛠️ 設定画面を開きました")
                logger.info("設定画面を表示しました")
            
        except Exception as e:
            logger.error(f"設定画面表示エラー: {e}")
            messagebox.showerror("エラー", f"設定画面の表示でエラーが発生しました:\n{e}")
    
    def _show_account_settings(self):
        """
        アカウント設定画面を表示
        """
        try:
            from src.ui.account_dialog import show_account_dialog
            
            if not self.current_account:
                # 新規アカウント追加
                self._add_account()
                return
            
            # 既存アカウントの編集
            def on_account_updated(updated_account):
                """アカウント更新時のコールバック"""
                logger.info(f"アカウントが更新されました: {updated_account.name}")
                self._update_status(f"⚙️ アカウント設定を更新しました: {updated_account.name}")
                
                # アカウントリストを再読み込み
                self._load_accounts()
            
            dialog = show_account_dialog(
                parent=self.root,
                account=self.current_account,
                on_account_saved=on_account_updated
            )
            
            if dialog:
                self._update_status("⚙️ アカウント設定画面を開きました")
                logger.info("アカウント設定画面を表示しました")
            
        except Exception as e:
            logger.error(f"アカウント設定画面表示エラー: {e}")
            messagebox.showerror("エラー", f"アカウント設定画面の表示でエラーが発生しました:\n{e}")
    
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