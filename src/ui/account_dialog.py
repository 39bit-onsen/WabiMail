# -*- coding: utf-8 -*-
"""
アカウント設定ダイアログモジュール

G005アカウント追加・編集画面を実装します。
Gmail OAuth2認証とIMAP/SMTP/POP設定に対応した統合アカウント設定ダイアログです。

Author: WabiMail Development Team
Created: 2025-07-01
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Dict, Any, Callable
import threading
from dataclasses import asdict

from src.mail.account import Account, AccountType, AuthType, AccountSettings
from src.mail.account_manager import AccountManager
from src.auth.oauth2_manager import GmailOAuth2Manager
from src.config.oauth2_config import OAuth2Config, OAuth2Messages
from src.utils.logger import get_logger

# ロガーを取得
logger = get_logger(__name__)


class AccountDialog:
    """
    アカウント設定ダイアログクラス
    
    G005アカウント追加・編集画面の実装です。
    侘び寂びの美学に基づいた、シンプルで分かりやすいインターフェースを提供し、
    以下の機能をサポートします：
    
    • Gmail OAuth2認証（自動設定）
    • IMAP/SMTP手動設定
    • POP3設定
    • 接続テスト機能
    • アカウント編集
    
    Attributes:
        parent: 親ウィンドウ
        account: 編集対象アカウント（None の場合は新規作成）
        account_manager: アカウント管理器
        oauth2_manager: OAuth2認証管理器
        result_account: 設定結果のアカウント
        success_callback: 成功時のコールバック関数
    """
    
    def __init__(self, parent, account: Optional[Account] = None, 
                 success_callback: Optional[Callable[[Account], None]] = None):
        """
        アカウント設定ダイアログを初期化します
        
        Args:
            parent: 親ウィンドウ
            account: 編集対象アカウント（Noneの場合は新規作成）
            success_callback: 成功時のコールバック関数
        """
        self.parent = parent
        self.account = account
        self.account_manager = AccountManager()
        self.oauth2_manager = GmailOAuth2Manager()
        self.result_account: Optional[Account] = None
        self.success_callback = success_callback
        
        # フォーム変数
        self.name_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.account_type_var = tk.StringVar()
        self.auth_type_var = tk.StringVar()
        self.incoming_server_var = tk.StringVar()
        self.incoming_port_var = tk.IntVar()
        self.incoming_security_var = tk.StringVar()
        self.outgoing_server_var = tk.StringVar()
        self.outgoing_port_var = tk.IntVar()
        self.outgoing_security_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.display_name_var = tk.StringVar()
        self.signature_var = tk.StringVar()
        
        # UI要素の参照
        self.dialog = None
        self.notebook = None
        self.oauth2_frame = None
        self.manual_frame = None
        self.test_button = None
        self.save_button = None
        self.oauth2_status_label = None
        self.connection_status_label = None
        
        # 状態管理
        self.is_oauth2_authenticated = False
        self.is_connection_tested = False
        
        self._create_dialog()
        self._load_account_data()
        
        logger.info(f"アカウント設定ダイアログを開きました: {'編集' if account else '新規作成'}")
    
    def _create_dialog(self):
        """
        ダイアログウィンドウを作成します
        """
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("🌸 アカウント設定 - WabiMail")
        self.dialog.geometry("600x700")
        self.dialog.resizable(True, True)
        
        # モーダルダイアログに設定
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # 親ウィンドウの中央に配置
        self.dialog.geometry("+%d+%d" % (
            self.parent.winfo_rootx() + 50,
            self.parent.winfo_rooty() + 50
        ))
        
        # 侘び寂びスタイル適用
        self._setup_wabi_sabi_style()
        
        # メインフレーム
        main_frame = ttk.Frame(self.dialog, style="Wabi.TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)
        
        # タイトル
        title_text = "✏️ アカウント編集" if self.account else "➕ アカウント追加"
        title_label = ttk.Label(main_frame, text=title_text, 
                               style="Title.Wabi.TLabel")
        title_label.pack(pady=(0, 16))
        
        # アカウントタイプ選択
        self._create_account_type_selection(main_frame)
        
        # 設定タブ
        self._create_settings_notebook(main_frame)
        
        # アクションボタン
        self._create_action_buttons(main_frame)
        
        # ステータス表示
        self._create_status_area(main_frame)
        
        # ダイアログ終了時の処理
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_cancel)
    
    def _setup_wabi_sabi_style(self):
        """
        侘び寂びスタイルを設定します
        """
        style = ttk.Style()
        
        # ダイアログ用カラー
        bg_color = "#fefefe"
        accent_color = "#f5f5f5"
        text_color = "#333333"
        select_color = "#ffe8e8"
        
        # タイトル用スタイル
        style.configure("Title.Wabi.TLabel",
                       background=bg_color,
                       foreground=text_color,
                       font=("Yu Gothic UI", 12, "bold"))
        
        # セクション用スタイル
        style.configure("Section.Wabi.TLabel",
                       background=bg_color,
                       foreground=text_color,
                       font=("Yu Gothic UI", 10, "bold"))
        
        # 説明用スタイル
        style.configure("Description.Wabi.TLabel",
                       background=bg_color,
                       foreground="#666666",
                       font=("Yu Gothic UI", 8))
        
        # 成功・エラー用スタイル
        style.configure("Success.Wabi.TLabel",
                       background=bg_color,
                       foreground="#008000",
                       font=("Yu Gothic UI", 9))
        
        style.configure("Error.Wabi.TLabel",
                       background=bg_color,
                       foreground="#800000",
                       font=("Yu Gothic UI", 9))
        
        # ダイアログ背景
        self.dialog.configure(bg=bg_color)
    
    def _create_account_type_selection(self, parent):
        """
        アカウントタイプ選択部分を作成します
        
        Args:
            parent: 親ウィジェット
        """
        type_frame = ttk.LabelFrame(parent, text="📧 アカウントタイプ", 
                                   style="Wabi.TLabelframe")
        type_frame.pack(fill=tk.X, pady=(0, 16))
        
        # 基本情報フレーム
        basic_frame = ttk.Frame(type_frame, style="Wabi.TFrame")
        basic_frame.pack(fill=tk.X, padx=12, pady=8)
        
        # アカウント名
        ttk.Label(basic_frame, text="アカウント名:", 
                 style="Wabi.TLabel").grid(row=0, column=0, sticky=tk.W, pady=2)
        name_entry = ttk.Entry(basic_frame, textvariable=self.name_var, 
                              font=("Yu Gothic UI", 9), width=30)
        name_entry.grid(row=0, column=1, sticky=tk.EW, padx=(8, 0), pady=2)
        
        # メールアドレス
        ttk.Label(basic_frame, text="メールアドレス:", 
                 style="Wabi.TLabel").grid(row=1, column=0, sticky=tk.W, pady=2)
        email_entry = ttk.Entry(basic_frame, textvariable=self.email_var, 
                               font=("Yu Gothic UI", 9), width=30)
        email_entry.grid(row=1, column=1, sticky=tk.EW, padx=(8, 0), pady=2)
        
        # メールアドレス変更時の処理
        email_entry.bind("<KeyRelease>", self._on_email_change)
        
        # 表示名
        ttk.Label(basic_frame, text="表示名:", 
                 style="Wabi.TLabel").grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Entry(basic_frame, textvariable=self.display_name_var, 
                 font=("Yu Gothic UI", 9), width=30).grid(row=2, column=1, sticky=tk.EW, padx=(8, 0), pady=2)
        
        basic_frame.columnconfigure(1, weight=1)
        
        # アカウントタイプ選択
        type_selection_frame = ttk.Frame(type_frame, style="Wabi.TFrame")
        type_selection_frame.pack(fill=tk.X, padx=12, pady=(0, 8))
        
        ttk.Label(type_selection_frame, text="アカウントタイプ:", 
                 style="Wabi.TLabel").pack(anchor=tk.W)
        
        # ラジオボタン
        radio_frame = ttk.Frame(type_selection_frame, style="Wabi.TFrame")
        radio_frame.pack(fill=tk.X, pady=4)
        
        # Gmail
        gmail_radio = ttk.Radiobutton(radio_frame, text="📧 Gmail (OAuth2認証)", 
                                     variable=self.account_type_var, value="gmail",
                                     command=self._on_account_type_change)
        gmail_radio.pack(anchor=tk.W, pady=2)
        
        # IMAP
        imap_radio = ttk.Radiobutton(radio_frame, text="📬 IMAP (手動設定)", 
                                    variable=self.account_type_var, value="imap",
                                    command=self._on_account_type_change)
        imap_radio.pack(anchor=tk.W, pady=2)
        
        # POP3
        pop3_radio = ttk.Radiobutton(radio_frame, text="📪 POP3 (手動設定)", 
                                    variable=self.account_type_var, value="pop3",
                                    command=self._on_account_type_change)
        pop3_radio.pack(anchor=tk.W, pady=2)
        
        # デフォルト選択
        self.account_type_var.set("gmail")
    
    def _create_settings_notebook(self, parent):
        """
        設定タブを作成します
        
        Args:
            parent: 親ウィジェット
        """
        self.notebook = ttk.Notebook(parent, style="Wabi.TNotebook")
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 16))
        
        # OAuth2設定タブ
        self._create_oauth2_tab()
        
        # 手動設定タブ
        self._create_manual_settings_tab()
        
        # 詳細設定タブ
        self._create_advanced_settings_tab()
        
        # 初期タブ選択
        self._update_tab_visibility()
    
    def _create_oauth2_tab(self):
        """
        OAuth2設定タブを作成します
        """
        self.oauth2_frame = ttk.Frame(self.notebook, style="Wabi.TFrame")
        self.notebook.add(self.oauth2_frame, text="🔐 OAuth2認証")
        
        # タイトル
        ttk.Label(self.oauth2_frame, text="Gmail OAuth2認証設定", 
                 style="Section.Wabi.TLabel").pack(pady=(16, 8))
        
        # 説明
        description = """Gmail アカウントを安全に接続するために OAuth2 認証を使用します。
以下のボタンをクリックして、ブラウザでGoogleアカウントにサインインしてください。"""
        
        ttk.Label(self.oauth2_frame, text=description, 
                 style="Description.Wabi.TLabel", 
                 wraplength=500, justify=tk.LEFT).pack(pady=(0, 16))
        
        # 必要スコープ表示
        scopes_frame = ttk.LabelFrame(self.oauth2_frame, text="📜 必要な権限", 
                                     style="Wabi.TLabelframe")
        scopes_frame.pack(fill=tk.X, padx=16, pady=(0, 16))
        
        scopes_text = ""
        for scope in OAuth2Config.GMAIL_SCOPES:
            description = OAuth2Messages.get_scope_description(scope)
            scopes_text += f"• {description}\n"
        
        ttk.Label(scopes_frame, text=scopes_text.strip(), 
                 style="Description.Wabi.TLabel", 
                 justify=tk.LEFT).pack(padx=8, pady=8)
        
        # OAuth2認証ボタン
        auth_button_frame = ttk.Frame(self.oauth2_frame, style="Wabi.TFrame")
        auth_button_frame.pack(pady=16)
        
        self.oauth2_auth_button = ttk.Button(auth_button_frame, 
                                           text="🌐 Gmail認証を開始", 
                                           command=self._start_oauth2_auth,
                                           style="Wabi.TButton")
        self.oauth2_auth_button.pack(pady=8)
        
        # OAuth2認証状態表示
        self.oauth2_status_label = ttk.Label(self.oauth2_frame, text="", 
                                           style="Wabi.TLabel")
        self.oauth2_status_label.pack(pady=8)
        
        # client_secret.json 状態確認
        self._check_client_secret_status()
    
    def _create_manual_settings_tab(self):
        """
        手動設定タブを作成します
        """
        self.manual_frame = ttk.Frame(self.notebook, style="Wabi.TFrame")
        self.notebook.add(self.manual_frame, text="⚙️ 手動設定")
        
        # スクロール可能フレーム
        canvas = tk.Canvas(self.manual_frame, bg="#fefefe")
        scrollbar = ttk.Scrollbar(self.manual_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style="Wabi.TFrame")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 受信サーバー設定
        self._create_incoming_server_settings(scrollable_frame)
        
        # 送信サーバー設定
        self._create_outgoing_server_settings(scrollable_frame)
        
        # 認証設定
        self._create_auth_settings(scrollable_frame)
    
    def _create_incoming_server_settings(self, parent):
        """
        受信サーバー設定を作成します
        
        Args:
            parent: 親ウィジェット
        """
        incoming_frame = ttk.LabelFrame(parent, text="📥 受信サーバー (IMAP/POP3)", 
                                       style="Wabi.TLabelframe")
        incoming_frame.pack(fill=tk.X, padx=16, pady=8)
        
        settings_frame = ttk.Frame(incoming_frame, style="Wabi.TFrame")
        settings_frame.pack(fill=tk.X, padx=12, pady=8)
        
        # サーバー
        ttk.Label(settings_frame, text="サーバー:", 
                 style="Wabi.TLabel").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Entry(settings_frame, textvariable=self.incoming_server_var, 
                 font=("Yu Gothic UI", 9), width=25).grid(row=0, column=1, sticky=tk.EW, padx=(8, 0), pady=2)
        
        # ポート
        ttk.Label(settings_frame, text="ポート:", 
                 style="Wabi.TLabel").grid(row=0, column=2, sticky=tk.W, padx=(16, 0), pady=2)
        port_spinbox = tk.Spinbox(settings_frame, textvariable=self.incoming_port_var,
                                 from_=1, to=65535, width=8, font=("Yu Gothic UI", 9))
        port_spinbox.grid(row=0, column=3, padx=(8, 0), pady=2)
        
        # セキュリティ
        ttk.Label(settings_frame, text="暗号化:", 
                 style="Wabi.TLabel").grid(row=1, column=0, sticky=tk.W, pady=2)
        security_combo = ttk.Combobox(settings_frame, textvariable=self.incoming_security_var,
                                     values=["SSL", "STARTTLS", "なし"], state="readonly", width=10)
        security_combo.grid(row=1, column=1, sticky=tk.W, padx=(8, 0), pady=2)
        
        settings_frame.columnconfigure(1, weight=1)
        
        # デフォルト値設定
        self.incoming_port_var.set(993)
        self.incoming_security_var.set("SSL")
    
    def _create_outgoing_server_settings(self, parent):
        """
        送信サーバー設定を作成します
        
        Args:
            parent: 親ウィジェット
        """
        outgoing_frame = ttk.LabelFrame(parent, text="📤 送信サーバー (SMTP)", 
                                       style="Wabi.TLabelframe")
        outgoing_frame.pack(fill=tk.X, padx=16, pady=8)
        
        settings_frame = ttk.Frame(outgoing_frame, style="Wabi.TFrame")
        settings_frame.pack(fill=tk.X, padx=12, pady=8)
        
        # サーバー
        ttk.Label(settings_frame, text="サーバー:", 
                 style="Wabi.TLabel").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Entry(settings_frame, textvariable=self.outgoing_server_var, 
                 font=("Yu Gothic UI", 9), width=25).grid(row=0, column=1, sticky=tk.EW, padx=(8, 0), pady=2)
        
        # ポート
        ttk.Label(settings_frame, text="ポート:", 
                 style="Wabi.TLabel").grid(row=0, column=2, sticky=tk.W, padx=(16, 0), pady=2)
        port_spinbox = tk.Spinbox(settings_frame, textvariable=self.outgoing_port_var,
                                 from_=1, to=65535, width=8, font=("Yu Gothic UI", 9))
        port_spinbox.grid(row=0, column=3, padx=(8, 0), pady=2)
        
        # セキュリティ
        ttk.Label(settings_frame, text="暗号化:", 
                 style="Wabi.TLabel").grid(row=1, column=0, sticky=tk.W, pady=2)
        security_combo = ttk.Combobox(settings_frame, textvariable=self.outgoing_security_var,
                                     values=["STARTTLS", "SSL", "なし"], state="readonly", width=10)
        security_combo.grid(row=1, column=1, sticky=tk.W, padx=(8, 0), pady=2)
        
        settings_frame.columnconfigure(1, weight=1)
        
        # デフォルト値設定
        self.outgoing_port_var.set(587)
        self.outgoing_security_var.set("STARTTLS")
    
    def _create_auth_settings(self, parent):
        """
        認証設定を作成します
        
        Args:
            parent: 親ウィジェット
        """
        auth_frame = ttk.LabelFrame(parent, text="🔐 認証", 
                                   style="Wabi.TLabelframe")
        auth_frame.pack(fill=tk.X, padx=16, pady=8)
        
        settings_frame = ttk.Frame(auth_frame, style="Wabi.TFrame")
        settings_frame.pack(fill=tk.X, padx=12, pady=8)
        
        # 認証タイプ
        ttk.Label(settings_frame, text="認証方式:", 
                 style="Wabi.TLabel").grid(row=0, column=0, sticky=tk.W, pady=2)
        auth_combo = ttk.Combobox(settings_frame, textvariable=self.auth_type_var,
                                 values=["password", "app_password"], state="readonly", width=15)
        auth_combo.grid(row=0, column=1, sticky=tk.W, padx=(8, 0), pady=2)
        
        # パスワード
        ttk.Label(settings_frame, text="パスワード:", 
                 style="Wabi.TLabel").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Entry(settings_frame, textvariable=self.password_var, 
                 show="*", font=("Yu Gothic UI", 9), width=25).grid(row=1, column=1, sticky=tk.EW, padx=(8, 0), pady=2)
        
        settings_frame.columnconfigure(1, weight=1)
        
        # デフォルト値設定
        self.auth_type_var.set("password")
    
    def _create_advanced_settings_tab(self):
        """
        詳細設定タブを作成します
        """
        advanced_frame = ttk.Frame(self.notebook, style="Wabi.TFrame")
        self.notebook.add(advanced_frame, text="🔧 詳細設定")
        
        # 署名設定
        signature_frame = ttk.LabelFrame(advanced_frame, text="✏️ メール署名", 
                                        style="Wabi.TLabelframe")
        signature_frame.pack(fill=tk.X, padx=16, pady=16)
        
        ttk.Label(signature_frame, text="署名:", 
                 style="Wabi.TLabel").pack(anchor=tk.W, padx=12, pady=(8, 4))
        
        signature_text = tk.Text(signature_frame, height=4, width=50,
                               font=("Yu Gothic UI", 9), bg="#fefefe", fg="#333333")
        signature_text.pack(fill=tk.X, padx=12, pady=(0, 8))
        
        # 署名テキストを変数に連動
        def update_signature(*args):
            self.signature_var.set(signature_text.get(1.0, tk.END).strip())
        
        signature_text.bind("<KeyRelease>", update_signature)
        signature_text.bind("<FocusOut>", update_signature)
        
        # 同期設定
        sync_frame = ttk.LabelFrame(advanced_frame, text="🔄 同期設定", 
                                   style="Wabi.TLabelframe")
        sync_frame.pack(fill=tk.X, padx=16, pady=(0, 16))
        
        self.sync_enabled_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(sync_frame, text="自動同期を有効にする",
                       variable=self.sync_enabled_var).pack(anchor=tk.W, padx=12, pady=8)
        
        self.is_default_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(sync_frame, text="このアカウントをデフォルトに設定",
                       variable=self.is_default_var).pack(anchor=tk.W, padx=12, pady=(0, 8))
    
    def _create_action_buttons(self, parent):
        """
        アクションボタンを作成します
        
        Args:
            parent: 親ウィジェット
        """
        button_frame = ttk.Frame(parent, style="Wabi.TFrame")
        button_frame.pack(fill=tk.X, pady=(0, 16))
        
        # 接続テストボタン
        self.test_button = ttk.Button(button_frame, text="🔍 接続テスト", 
                                     command=self._test_connection,
                                     style="Wabi.TButton")
        self.test_button.pack(side=tk.LEFT, padx=(0, 8))
        
        # 右側のボタン群
        right_buttons = ttk.Frame(button_frame, style="Wabi.TFrame")
        right_buttons.pack(side=tk.RIGHT)
        
        # キャンセルボタン
        ttk.Button(right_buttons, text="キャンセル", 
                  command=self._on_cancel,
                  style="Wabi.TButton").pack(side=tk.LEFT, padx=(0, 8))
        
        # 保存ボタン
        self.save_button = ttk.Button(right_buttons, text="💾 保存", 
                                     command=self._on_save,
                                     style="Wabi.TButton")
        self.save_button.pack(side=tk.LEFT)
    
    def _create_status_area(self, parent):
        """
        ステータス表示エリアを作成します
        
        Args:
            parent: 親ウィジェット
        """
        status_frame = ttk.Frame(parent, style="Wabi.TFrame", relief=tk.SUNKEN, borderwidth=1)
        status_frame.pack(fill=tk.X)
        
        self.connection_status_label = ttk.Label(status_frame, text="設定を入力してください", 
                                               style="Wabi.TLabel")
        self.connection_status_label.pack(side=tk.LEFT, padx=4, pady=2)
    
    def _load_account_data(self):
        """
        既存アカウントデータを読み込みます（編集モード時）
        """
        if not self.account:
            return
        
        try:
            # 基本情報
            self.name_var.set(self.account.name)
            self.email_var.set(self.account.email_address)
            self.display_name_var.set(self.account.display_name)
            self.signature_var.set(self.account.signature)
            
            # アカウントタイプ
            self.account_type_var.set(self.account.account_type.value)
            self.auth_type_var.set(self.account.auth_type.value)
            
            # サーバー設定
            self.incoming_server_var.set(self.account.settings.incoming_server)
            self.incoming_port_var.set(self.account.settings.incoming_port)
            self.incoming_security_var.set(self.account.settings.incoming_security)
            self.outgoing_server_var.set(self.account.settings.outgoing_server)
            self.outgoing_port_var.set(self.account.settings.outgoing_port)
            self.outgoing_security_var.set(self.account.settings.outgoing_security)
            
            # 詳細設定
            self.sync_enabled_var.set(self.account.sync_enabled)
            self.is_default_var.set(self.account.is_default)
            
            # OAuth2認証状態確認
            if self.account.requires_oauth2():
                self.is_oauth2_authenticated = self.oauth2_manager.is_authenticated(self.account.email_address)
                self._update_oauth2_status()
            
            self._update_tab_visibility()
            
            logger.info(f"アカウントデータを読み込みました: {self.account.email_address}")
            
        except Exception as e:
            logger.error(f"アカウントデータ読み込みエラー: {e}")
            messagebox.showerror("エラー", f"アカウントデータの読み込みに失敗しました: {e}")
    
    def _on_email_change(self, event):
        """
        メールアドレス変更イベント
        """
        email = self.email_var.get().strip()
        
        # Gmailアドレスの場合は自動的にGmailタイプに設定
        if email.endswith("@gmail.com") or email.endswith("@googlemail.com"):
            self.account_type_var.set("gmail")
            self._on_account_type_change()
            
        # 表示名が空の場合は自動設定
        if not self.display_name_var.get().strip() and email:
            display_name = email.split('@')[0]
            self.display_name_var.set(display_name)
    
    def _on_account_type_change(self):
        """
        アカウントタイプ変更イベント
        """
        account_type = self.account_type_var.get()
        
        if account_type == "gmail":
            # Gmailの場合はプリセット設定を適用
            self.incoming_server_var.set("imap.gmail.com")
            self.incoming_port_var.set(993)
            self.incoming_security_var.set("SSL")
            self.outgoing_server_var.set("smtp.gmail.com")
            self.outgoing_port_var.set(587)
            self.outgoing_security_var.set("STARTTLS")
            self.auth_type_var.set("oauth2")
        elif account_type == "imap":
            # IMAP設定例
            self.incoming_port_var.set(993)
            self.incoming_security_var.set("SSL")
            self.outgoing_port_var.set(587)
            self.outgoing_security_var.set("STARTTLS")
            self.auth_type_var.set("password")
        elif account_type == "pop3":
            # POP3設定例
            self.incoming_port_var.set(995)
            self.incoming_security_var.set("SSL")
            self.outgoing_port_var.set(587)
            self.outgoing_security_var.set("STARTTLS")
            self.auth_type_var.set("password")
        
        self._update_tab_visibility()
        self._update_status("設定を確認してください")
    
    def _update_tab_visibility(self):
        """
        アカウントタイプに応じてタブの表示を更新します
        """
        account_type = self.account_type_var.get()
        
        if account_type == "gmail":
            # OAuth2タブを表示、手動設定タブを無効化
            self.notebook.tab(0, state="normal")
            self.notebook.tab(1, state="disabled")
            self.notebook.select(0)  # OAuth2タブを選択
        else:
            # 手動設定タブを表示、OAuth2タブを無効化
            self.notebook.tab(0, state="disabled")
            self.notebook.tab(1, state="normal")
            self.notebook.select(1)  # 手動設定タブを選択
    
    def _check_client_secret_status(self):
        """
        client_secret.jsonの状態を確認します
        """
        if self.oauth2_manager.is_client_secret_available():
            status_text = "✅ client_secret.json が利用可能です"
            self.oauth2_auth_button.config(state="normal")
        else:
            status_text = "❌ client_secret.json が見つかりません"
            self.oauth2_auth_button.config(state="disabled")
            
            # 設定方法を表示
            help_text = OAuth2Messages.CLIENT_SECRET_NOT_FOUND
            ttk.Label(self.oauth2_frame, text=help_text, 
                     style="Description.Wabi.TLabel", 
                     wraplength=500, justify=tk.LEFT).pack(pady=8)
        
        ttk.Label(self.oauth2_frame, text=status_text, 
                 style="Success.Wabi.TLabel" if self.oauth2_manager.is_client_secret_available() else "Error.Wabi.TLabel").pack()
    
    def _start_oauth2_auth(self):
        """
        OAuth2認証を開始します
        """
        email = self.email_var.get().strip()
        if not email:
            messagebox.showwarning("警告", "メールアドレスを入力してください")
            return
        
        def auth_in_background():
            """
            バックグラウンドでOAuth2認証を実行します
            """
            try:
                self.dialog.after(0, lambda: self._update_oauth2_status("🌐 認証を開始しています..."))
                self.dialog.after(0, lambda: self.oauth2_auth_button.config(state="disabled"))
                
                # OAuth2認証フローを開始
                success, message = self.oauth2_manager.start_oauth2_flow(email)
                
                if success:
                    self.is_oauth2_authenticated = True
                    self.dialog.after(0, lambda: self._update_oauth2_status("✅ Gmail認証が完了しました", "success"))
                    self.dialog.after(0, lambda: self._update_status("OAuth2認証が完了しました"))
                else:
                    self.is_oauth2_authenticated = False
                    self.dialog.after(0, lambda: self._update_oauth2_status(f"❌ 認証に失敗しました: {message}", "error"))
                    self.dialog.after(0, lambda: self._update_status("OAuth2認証に失敗しました"))
                
                self.dialog.after(0, lambda: self.oauth2_auth_button.config(state="normal"))
                
            except Exception as e:
                logger.error(f"OAuth2認証エラー: {e}")
                self.dialog.after(0, lambda: self._update_oauth2_status(f"❌ エラー: {e}", "error"))
                self.dialog.after(0, lambda: self.oauth2_auth_button.config(state="normal"))
        
        # バックグラウンドスレッドで実行
        thread = threading.Thread(target=auth_in_background, daemon=True)
        thread.start()
    
    def _update_oauth2_status(self, message: str = "", status_type: str = "normal"):
        """
        OAuth2認証状態を更新します
        
        Args:
            message: ステータスメッセージ
            status_type: ステータスタイプ（normal/success/error）
        """
        if self.is_oauth2_authenticated and not message:
            message = "✅ Gmail認証が完了しています"
            status_type = "success"
        elif not message:
            message = "❌ Gmail認証が必要です"
            status_type = "error"
        
        style = "Wabi.TLabel"
        if status_type == "success":
            style = "Success.Wabi.TLabel"
        elif status_type == "error":
            style = "Error.Wabi.TLabel"
        
        self.oauth2_status_label.config(text=message, style=style)
    
    def _test_connection(self):
        """
        接続テストを実行します
        """
        def test_in_background():
            """
            バックグラウンドで接続テストを実行します
            """
            try:
                self.dialog.after(0, lambda: self._update_status("接続テストを実行中..."))
                self.dialog.after(0, lambda: self.test_button.config(state="disabled"))
                
                # テスト用アカウントを作成
                test_account = self._create_account_from_form()
                if not test_account:
                    return
                
                # 接続テスト実行
                from src.mail.mail_client_factory import MailClientFactory
                
                # 受信テスト
                receive_client = MailClientFactory.create_receive_client(test_account)
                if receive_client:
                    success, message = receive_client.test_connection()
                    if success:
                        self.is_connection_tested = True
                        self.dialog.after(0, lambda: self._update_status("✅ 接続テストが成功しました"))
                    else:
                        self.is_connection_tested = False
                        self.dialog.after(0, lambda: self._update_status(f"❌ 接続テストが失敗しました: {message}"))
                else:
                    self.is_connection_tested = False
                    self.dialog.after(0, lambda: self._update_status("❌ メールクライアントを作成できませんでした"))
                
                self.dialog.after(0, lambda: self.test_button.config(state="normal"))
                
            except Exception as e:
                logger.error(f"接続テストエラー: {e}")
                self.is_connection_tested = False
                self.dialog.after(0, lambda: self._update_status(f"❌ 接続テストエラー: {e}"))
                self.dialog.after(0, lambda: self.test_button.config(state="normal"))
        
        # バックグラウンドスレッドで実行
        thread = threading.Thread(target=test_in_background, daemon=True)
        thread.start()
    
    def _create_account_from_form(self) -> Optional[Account]:
        """
        フォームデータからアカウントオブジェクトを作成します
        
        Returns:
            Account: 作成されたアカウントオブジェクト
        """
        try:
            # 基本情報の検証
            name = self.name_var.get().strip()
            email = self.email_var.get().strip()
            
            if not name:
                messagebox.showwarning("警告", "アカウント名を入力してください")
                return None
            
            if not email:
                messagebox.showwarning("警告", "メールアドレスを入力してください")
                return None
            
            # アカウント作成
            account = Account(
                account_id=self.account.account_id if self.account else None,
                name=name,
                email_address=email,
                account_type=AccountType(self.account_type_var.get()),
                auth_type=AuthType(self.auth_type_var.get()),
                display_name=self.display_name_var.get().strip() or email.split('@')[0],
                signature=self.signature_var.get().strip(),
                sync_enabled=getattr(self, 'sync_enabled_var', tk.BooleanVar(value=True)).get(),
                is_default=getattr(self, 'is_default_var', tk.BooleanVar(value=False)).get()
            )
            
            # サーバー設定
            account.settings = AccountSettings(
                incoming_server=self.incoming_server_var.get().strip(),
                incoming_port=self.incoming_port_var.get(),
                incoming_security=self.incoming_security_var.get(),
                outgoing_server=self.outgoing_server_var.get().strip(),
                outgoing_port=self.outgoing_port_var.get(),
                outgoing_security=self.outgoing_security_var.get(),
                requires_auth=True
            )
            
            # プリセット設定適用
            account.apply_preset_settings()
            
            # 検証
            is_valid, errors = account.validate()
            if not is_valid:
                messagebox.showerror("入力エラー", "\n".join(errors))
                return None
            
            return account
            
        except Exception as e:
            logger.error(f"アカウント作成エラー: {e}")
            messagebox.showerror("エラー", f"アカウントの作成に失敗しました: {e}")
            return None
    
    def _on_save(self):
        """
        保存ボタンクリックイベント
        """
        try:
            # アカウント作成
            account = self._create_account_from_form()
            if not account:
                return
            
            # OAuth2認証が必要な場合の確認
            if account.requires_oauth2() and not self.is_oauth2_authenticated:
                result = messagebox.askyesno(
                    "確認", 
                    "OAuth2認証が完了していませんが、保存しますか？\n"
                    "後でメールの送受信時に認証が必要になります。"
                )
                if not result:
                    return
            
            # アカウント保存
            if self.account:
                # 既存アカウントの更新
                success = self.account_manager.update_account(account)
                action = "更新"
            else:
                # 新規アカウントの追加
                success = self.account_manager.add_account(account)
                action = "追加"
            
            if success:
                self.result_account = account
                messagebox.showinfo("成功", f"アカウントを{action}しました")
                
                # 成功コールバック呼び出し
                if self.success_callback:
                    self.success_callback(account)
                
                self._close_dialog()
            else:
                messagebox.showerror("エラー", f"アカウントの{action}に失敗しました")
                
        except Exception as e:
            logger.error(f"アカウント保存エラー: {e}")
            messagebox.showerror("エラー", f"アカウントの保存に失敗しました: {e}")
    
    def _on_cancel(self):
        """
        キャンセルボタンクリックイベント
        """
        self._close_dialog()
    
    def _close_dialog(self):
        """
        ダイアログを閉じます
        """
        logger.info("アカウント設定ダイアログを閉じます")
        self.dialog.destroy()
    
    def _update_status(self, message: str):
        """
        ステータスを更新します
        
        Args:
            message: ステータスメッセージ
        """
        if self.connection_status_label:
            self.connection_status_label.config(text=message)
    
    def show(self) -> Optional[Account]:
        """
        ダイアログを表示します
        
        Returns:
            Account: 設定されたアカウント（キャンセル時はNone）
        """
        # ダイアログを表示（モーダル）
        self.dialog.wait_window()
        return self.result_account


def show_account_dialog(parent, account: Optional[Account] = None, 
                       success_callback: Optional[Callable[[Account], None]] = None) -> Optional[Account]:
    """
    アカウント設定ダイアログを表示します
    
    Args:
        parent: 親ウィンドウ
        account: 編集対象アカウント（Noneの場合は新規作成）
        success_callback: 成功時のコールバック関数
        
    Returns:
        Account: 設定されたアカウント（キャンセル時はNone）
    """
    dialog = AccountDialog(parent, account, success_callback)
    return dialog.show()


if __name__ == "__main__":
    # テスト用メイン関数
    root = tk.Tk()
    root.withdraw()  # メインウィンドウを非表示
    
    result = show_account_dialog(root)
    if result:
        print(f"設定されたアカウント: {result}")
    else:
        print("キャンセルされました")
    
    root.destroy()