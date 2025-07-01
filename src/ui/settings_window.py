# -*- coding: utf-8 -*-
"""
設定画面ウィンドウモジュール

WabiMailの設定画面を実装します。
侘び寂びの美学に基づいた、シンプルで美しい設定インターフェースを提供します。

Author: WabiMail Development Team
Created: 2025-07-01
"""

import tkinter as tk
from tkinter import ttk, messagebox, colorchooser, filedialog
from typing import Dict, Any, Optional, Callable
import threading
import os
from pathlib import Path
from datetime import datetime

from src.config.app_config import AppConfig
from src.utils.logger import get_logger

# ロガーを取得
logger = get_logger(__name__)


class SettingsWindow:
    """
    設定画面ウィンドウクラス
    
    侘び寂びの美学に基づいた、美しく使いやすい設定画面を提供します。
    アプリケーションの各種設定を統合的に管理できるインターフェースを実現します。
    
    機能:
    • 一般設定（言語、テーマ、フォント）
    • 外観設定（色彩、レイアウト、サイズ）
    • メール設定（チェック間隔、通知）
    • セキュリティ設定（暗号化、認証）
    • ログ設定（ログレベル、出力先）
    • 侘び寂びテーマ設定
    • 設定のインポート・エクスポート
    
    Attributes:
        parent: 親ウィンドウ
        config: アプリケーション設定
        on_settings_changed: 設定変更コールバック
        window: 設定ウィンドウ
        notebook: タブウィジェット
        settings_vars: 設定変数辞書
        changes_made: 変更フラグ
    """
    
    def __init__(self, parent, config: AppConfig, 
                 on_settings_changed: Optional[Callable] = None):
        """
        設定ウィンドウを初期化します
        
        Args:
            parent: 親ウィンドウ
            config: アプリケーション設定
            on_settings_changed: 設定変更時のコールバック
        """
        self.parent = parent
        self.config = config
        self.on_settings_changed = on_settings_changed
        
        # ウィンドウ状態
        self.window = None
        self.notebook = None
        self.settings_vars = {}
        self.changes_made = False
        
        # UI要素の参照
        self.status_label = None
        
        # 侘び寂びスタイルの設定
        self._setup_wabi_sabi_style()
        
        # ウィンドウを作成
        self._create_window()
        
        logger.info("設定ウィンドウを初期化しました")
    
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
            "focus": "#d4c4b0",        # フォーカス色
            "disabled": "#999999",     # 無効状態
            "success": "#4a7c59",      # 成功色
            "warning": "#b8860b",      # 警告色
            "error": "#cd5c5c"         # エラー色
        }
        
        self.wabi_fonts = {
            "header": ("Yu Gothic UI", 14, "bold"),
            "subheader": ("Yu Gothic UI", 12, "normal"),
            "body": ("Yu Gothic UI", 10, "normal"),
            "small": ("Yu Gothic UI", 9, "normal")
        }
    
    def _create_window(self):
        """
        設定ウィンドウを作成します
        """
        # 新しいウィンドウを作成
        self.window = tk.Toplevel(self.parent)
        
        # ウィンドウタイトル
        self.window.title("🌸 WabiMail 設定")
        
        # ウィンドウサイズと位置
        window_width = 700
        window_height = 600
        
        # 親ウィンドウの中央に配置
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        x = parent_x + (parent_width - window_width) // 2
        y = parent_y + (parent_height - window_height) // 2
        
        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.window.minsize(600, 500)
        
        # ウィンドウ設定
        self.window.configure(bg=self.wabi_colors["bg"])
        self.window.transient(self.parent)
        self.window.grab_set()
        
        # ウィンドウ閉じる時の処理
        self.window.protocol("WM_DELETE_WINDOW", self._on_window_close)
        
        # UI要素を作成
        self._create_header()
        self._create_notebook()
        self._create_button_frame()
        self._create_status_bar()
        
        # 設定値をロード
        self._load_settings()
        
        logger.info("設定ウィンドウを作成しました")
    
    def _create_header(self):
        """
        ヘッダーセクションを作成します
        """
        header_frame = ttk.Frame(self.window, style="Header.Wabi.TFrame")
        header_frame.pack(fill=tk.X, padx=16, pady=(16, 8))
        
        # タイトル
        title_label = ttk.Label(
            header_frame,
            text="🌸 WabiMail 設定",
            style="HeaderTitle.Wabi.TLabel",
            font=self.wabi_fonts["header"]
        )
        title_label.pack(side=tk.LEFT)
        
        # 説明文
        desc_label = ttk.Label(
            header_frame,
            text="侘び寂びの美学に基づいた設定をカスタマイズできます",
            style="HeaderDesc.Wabi.TLabel",
            font=self.wabi_fonts["small"]
        )
        desc_label.pack(side=tk.RIGHT)
    
    def _create_notebook(self):
        """
        タブウィジェットを作成します
        """
        # ノートブック作成
        self.notebook = ttk.Notebook(self.window, style="Settings.Wabi.TNotebook")
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=16, pady=8)
        
        # 各タブを作成
        self._create_general_tab()
        self._create_appearance_tab()
        self._create_mail_tab()
        self._create_security_tab()
        self._create_wabi_sabi_tab()
        self._create_advanced_tab()
        
        # タブ変更イベント
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)
    
    def _create_general_tab(self):
        """
        一般設定タブを作成します
        """
        general_frame = ttk.Frame(self.notebook, style="TabContent.Wabi.TFrame")
        self.notebook.add(general_frame, text="⚙️ 一般")
        
        # スクロール可能フレーム
        canvas = tk.Canvas(general_frame, bg=self.wabi_colors["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(general_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style="Scrollable.Wabi.TFrame")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 言語設定
        lang_frame = ttk.LabelFrame(scrollable_frame, text="🌐 言語設定", style="Section.Wabi.TLabelframe")
        lang_frame.pack(fill=tk.X, padx=16, pady=8)
        
        ttk.Label(lang_frame, text="表示言語:", style="Label.Wabi.TLabel").pack(anchor=tk.W, padx=8, pady=4)
        
        lang_var = tk.StringVar()
        self.settings_vars["app.language"] = lang_var
        
        lang_combo = ttk.Combobox(
            lang_frame,
            textvariable=lang_var,
            values=["ja", "en"],
            state="readonly",
            style="Setting.Wabi.TCombobox"
        )
        lang_combo.pack(fill=tk.X, padx=8, pady=4)
        lang_combo.bind("<<ComboboxSelected>>", self._on_setting_changed)
        
        # 起動設定
        startup_frame = ttk.LabelFrame(scrollable_frame, text="🚀 起動設定", style="Section.Wabi.TLabelframe")
        startup_frame.pack(fill=tk.X, padx=16, pady=8)
        
        startup_var = tk.BooleanVar()
        self.settings_vars["startup.auto_start"] = startup_var
        
        startup_check = ttk.Checkbutton(
            startup_frame,
            text="システム起動時にWabiMailを自動開始",
            variable=startup_var,
            style="Setting.Wabi.TCheckbutton",
            command=self._on_setting_changed
        )
        startup_check.pack(anchor=tk.W, padx=8, pady=4)
        
        minimize_var = tk.BooleanVar()
        self.settings_vars["startup.minimize_to_tray"] = minimize_var
        
        minimize_check = ttk.Checkbutton(
            startup_frame,
            text="最小化時にシステムトレイに格納",
            variable=minimize_var,
            style="Setting.Wabi.TCheckbutton",
            command=self._on_setting_changed
        )
        minimize_check.pack(anchor=tk.W, padx=8, pady=4)
        
        # アップデート設定
        update_frame = ttk.LabelFrame(scrollable_frame, text="🔄 アップデート設定", style="Section.Wabi.TLabelframe")
        update_frame.pack(fill=tk.X, padx=16, pady=8)
        
        auto_update_var = tk.BooleanVar()
        self.settings_vars["update.auto_check"] = auto_update_var
        
        auto_update_check = ttk.Checkbutton(
            update_frame,
            text="自動的にアップデートを確認",
            variable=auto_update_var,
            style="Setting.Wabi.TCheckbutton",
            command=self._on_setting_changed
        )
        auto_update_check.pack(anchor=tk.W, padx=8, pady=4)
        
        # アップデート確認ボタン
        update_button = ttk.Button(
            update_frame,
            text="今すぐアップデートを確認",
            style="Action.Wabi.TButton",
            command=self._check_updates
        )
        update_button.pack(anchor=tk.W, padx=8, pady=4)
    
    def _create_appearance_tab(self):
        """
        外観設定タブを作成します
        """
        appearance_frame = ttk.Frame(self.notebook, style="TabContent.Wabi.TFrame")
        self.notebook.add(appearance_frame, text="🎨 外観")
        
        # スクロール可能フレーム
        canvas = tk.Canvas(appearance_frame, bg=self.wabi_colors["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(appearance_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style="Scrollable.Wabi.TFrame")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # テーマ設定
        theme_frame = ttk.LabelFrame(scrollable_frame, text="🌸 テーマ設定", style="Section.Wabi.TLabelframe")
        theme_frame.pack(fill=tk.X, padx=16, pady=8)
        
        ttk.Label(theme_frame, text="テーマ:", style="Label.Wabi.TLabel").pack(anchor=tk.W, padx=8, pady=4)
        
        theme_var = tk.StringVar()
        self.settings_vars["app.theme"] = theme_var
        
        theme_combo = ttk.Combobox(
            theme_frame,
            textvariable=theme_var,
            values=["wabi_sabi_light", "wabi_sabi_dark", "minimal_white", "zen_mode"],
            state="readonly",
            style="Setting.Wabi.TCombobox"
        )
        theme_combo.pack(fill=tk.X, padx=8, pady=4)
        theme_combo.bind("<<ComboboxSelected>>", self._on_theme_changed)
        
        # フォント設定
        font_frame = ttk.LabelFrame(scrollable_frame, text="📝 フォント設定", style="Section.Wabi.TLabelframe")
        font_frame.pack(fill=tk.X, padx=16, pady=8)
        
        # フォントファミリー
        ttk.Label(font_frame, text="フォント:", style="Label.Wabi.TLabel").pack(anchor=tk.W, padx=8, pady=4)
        
        font_family_var = tk.StringVar()
        self.settings_vars["ui.font.family"] = font_family_var
        
        font_combo = ttk.Combobox(
            font_frame,
            textvariable=font_family_var,
            values=["Yu Gothic UI", "Meiryo", "MS Gothic", "Arial", "Times New Roman"],
            style="Setting.Wabi.TCombobox"
        )
        font_combo.pack(fill=tk.X, padx=8, pady=4)
        font_combo.bind("<<ComboboxSelected>>", self._on_setting_changed)
        
        # フォントサイズ
        ttk.Label(font_frame, text="フォントサイズ:", style="Label.Wabi.TLabel").pack(anchor=tk.W, padx=8, pady=4)
        
        font_size_var = tk.IntVar()
        self.settings_vars["ui.font.size"] = font_size_var
        
        font_size_spin = ttk.Spinbox(
            font_frame,
            from_=8,
            to=24,
            textvariable=font_size_var,
            style="Setting.Wabi.TSpinbox",
            command=self._on_setting_changed
        )
        font_size_spin.pack(fill=tk.X, padx=8, pady=4)
        
        # 色彩設定
        color_frame = ttk.LabelFrame(scrollable_frame, text="🎨 色彩設定", style="Section.Wabi.TLabelframe")
        color_frame.pack(fill=tk.X, padx=16, pady=8)
        
        # 背景色
        bg_color_frame = ttk.Frame(color_frame)
        bg_color_frame.pack(fill=tk.X, padx=8, pady=4)
        
        ttk.Label(bg_color_frame, text="背景色:", style="Label.Wabi.TLabel").pack(side=tk.LEFT)
        
        bg_color_var = tk.StringVar()
        self.settings_vars["ui.colors.background"] = bg_color_var
        
        bg_color_button = ttk.Button(
            bg_color_frame,
            text="色を選択",
            style="ColorPicker.Wabi.TButton",
            command=lambda: self._pick_color(bg_color_var, "背景色")
        )
        bg_color_button.pack(side=tk.RIGHT)
        
        # レイアウト設定
        layout_frame = ttk.LabelFrame(scrollable_frame, text="📐 レイアウト設定", style="Section.Wabi.TLabelframe")
        layout_frame.pack(fill=tk.X, padx=16, pady=8)
        
        # 左ペイン幅
        ttk.Label(layout_frame, text="左ペイン幅:", style="Label.Wabi.TLabel").pack(anchor=tk.W, padx=8, pady=4)
        
        left_pane_var = tk.IntVar()
        self.settings_vars["ui.layout.left_pane_width"] = left_pane_var
        
        left_pane_scale = ttk.Scale(
            layout_frame,
            from_=150,
            to=400,
            variable=left_pane_var,
            orient=tk.HORIZONTAL,
            style="Setting.Wabi.TScale",
            command=self._on_setting_changed
        )
        left_pane_scale.pack(fill=tk.X, padx=8, pady=4)
        
        # プレビュー表示
        preview_var = tk.BooleanVar()
        self.settings_vars["ui.layout.show_preview"] = preview_var
        
        preview_check = ttk.Checkbutton(
            layout_frame,
            text="メールプレビューを表示",
            variable=preview_var,
            style="Setting.Wabi.TCheckbutton",
            command=self._on_setting_changed
        )
        preview_check.pack(anchor=tk.W, padx=8, pady=4)
    
    def _create_mail_tab(self):
        """
        メール設定タブを作成します
        """
        mail_frame = ttk.Frame(self.notebook, style="TabContent.Wabi.TFrame")
        self.notebook.add(mail_frame, text="📧 メール")
        
        # スクロール可能フレーム
        canvas = tk.Canvas(mail_frame, bg=self.wabi_colors["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(mail_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style="Scrollable.Wabi.TFrame")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # メールチェック設定
        check_frame = ttk.LabelFrame(scrollable_frame, text="🔄 メールチェック", style="Section.Wabi.TLabelframe")
        check_frame.pack(fill=tk.X, padx=16, pady=8)
        
        auto_check_var = tk.BooleanVar()
        self.settings_vars["mail.auto_check"] = auto_check_var
        
        auto_check_check = ttk.Checkbutton(
            check_frame,
            text="自動的にメールをチェック",
            variable=auto_check_var,
            style="Setting.Wabi.TCheckbutton",
            command=self._on_setting_changed
        )
        auto_check_check.pack(anchor=tk.W, padx=8, pady=4)
        
        # チェック間隔
        ttk.Label(check_frame, text="チェック間隔（分）:", style="Label.Wabi.TLabel").pack(anchor=tk.W, padx=8, pady=4)
        
        check_interval_var = tk.IntVar()
        self.settings_vars["mail.check_interval"] = check_interval_var
        
        check_interval_spin = ttk.Spinbox(
            check_frame,
            from_=1,
            to=60,
            textvariable=check_interval_var,
            style="Setting.Wabi.TSpinbox",
            command=self._on_setting_changed
        )
        check_interval_spin.pack(fill=tk.X, padx=8, pady=4)
        
        # 通知設定
        notification_frame = ttk.LabelFrame(scrollable_frame, text="🔔 通知設定", style="Section.Wabi.TLabelframe")
        notification_frame.pack(fill=tk.X, padx=16, pady=8)
        
        notifications_enabled_var = tk.BooleanVar()
        self.settings_vars["mail.notifications.enabled"] = notifications_enabled_var
        
        notifications_check = ttk.Checkbutton(
            notification_frame,
            text="新着メール通知を有効にする",
            variable=notifications_enabled_var,
            style="Setting.Wabi.TCheckbutton",
            command=self._on_setting_changed
        )
        notifications_check.pack(anchor=tk.W, padx=8, pady=4)
        
        sound_var = tk.BooleanVar()
        self.settings_vars["mail.notifications.sound"] = sound_var
        
        sound_check = ttk.Checkbutton(
            notification_frame,
            text="通知音を再生（侘び寂びの精神に反するため推奨しません）",
            variable=sound_var,
            style="Setting.Wabi.TCheckbutton",
            command=self._on_setting_changed
        )
        sound_check.pack(anchor=tk.W, padx=8, pady=4)
        
        # 署名設定
        signature_frame = ttk.LabelFrame(scrollable_frame, text="✍️ 署名設定", style="Section.Wabi.TLabelframe")
        signature_frame.pack(fill=tk.X, padx=16, pady=8)
        
        signature_enabled_var = tk.BooleanVar()
        self.settings_vars["mail.signature.enabled"] = signature_enabled_var
        
        signature_check = ttk.Checkbutton(
            signature_frame,
            text="メールに署名を自動挿入",
            variable=signature_enabled_var,
            style="Setting.Wabi.TCheckbutton",
            command=self._on_setting_changed
        )
        signature_check.pack(anchor=tk.W, padx=8, pady=4)
        
        ttk.Label(signature_frame, text="署名内容:", style="Label.Wabi.TLabel").pack(anchor=tk.W, padx=8, pady=4)
        
        signature_text = tk.Text(
            signature_frame,
            height=4,
            wrap=tk.WORD,
            font=self.wabi_fonts["body"],
            bg=self.wabi_colors["entry_bg"],
            fg=self.wabi_colors["fg"]
        )
        signature_text.pack(fill=tk.X, padx=8, pady=4)
        signature_text.bind("<KeyRelease>", self._on_setting_changed)
        
        self.settings_vars["mail.signature.text"] = signature_text
    
    def _create_security_tab(self):
        """
        セキュリティ設定タブを作成します
        """
        security_frame = ttk.Frame(self.notebook, style="TabContent.Wabi.TFrame")
        self.notebook.add(security_frame, text="🔒 セキュリティ")
        
        # スクロール可能フレーム
        canvas = tk.Canvas(security_frame, bg=self.wabi_colors["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(security_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style="Scrollable.Wabi.TFrame")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 暗号化設定
        encryption_frame = ttk.LabelFrame(scrollable_frame, text="🔐 暗号化設定", style="Section.Wabi.TLabelframe")
        encryption_frame.pack(fill=tk.X, padx=16, pady=8)
        
        encryption_var = tk.BooleanVar()
        self.settings_vars["security.encryption_enabled"] = encryption_var
        
        encryption_check = ttk.Checkbutton(
            encryption_frame,
            text="アカウント情報を暗号化して保存",
            variable=encryption_var,
            style="Setting.Wabi.TCheckbutton",
            command=self._on_setting_changed
        )
        encryption_check.pack(anchor=tk.W, padx=8, pady=4)
        
        # パスワード管理
        password_frame = ttk.LabelFrame(scrollable_frame, text="🔑 パスワード管理", style="Section.Wabi.TLabelframe")
        password_frame.pack(fill=tk.X, padx=16, pady=8)
        
        remember_passwords_var = tk.BooleanVar()
        self.settings_vars["security.remember_passwords"] = remember_passwords_var
        
        remember_check = ttk.Checkbutton(
            password_frame,
            text="パスワードを記憶する",
            variable=remember_passwords_var,
            style="Setting.Wabi.TCheckbutton",
            command=self._on_setting_changed
        )
        remember_check.pack(anchor=tk.W, padx=8, pady=4)
        
        # 自動ロック
        auto_lock_frame = ttk.LabelFrame(scrollable_frame, text="🔒 自動ロック", style="Section.Wabi.TLabelframe")
        auto_lock_frame.pack(fill=tk.X, padx=16, pady=8)
        
        auto_lock_var = tk.BooleanVar()
        self.settings_vars["security.auto_lock"] = auto_lock_var
        
        auto_lock_check = ttk.Checkbutton(
            auto_lock_frame,
            text="一定時間経過後に自動ロック",
            variable=auto_lock_var,
            style="Setting.Wabi.TCheckbutton",
            command=self._on_setting_changed
        )
        auto_lock_check.pack(anchor=tk.W, padx=8, pady=4)
        
        ttk.Label(auto_lock_frame, text="ロック時間（分）:", style="Label.Wabi.TLabel").pack(anchor=tk.W, padx=8, pady=4)
        
        lock_timeout_var = tk.IntVar()
        self.settings_vars["security.lock_timeout"] = lock_timeout_var
        
        lock_timeout_spin = ttk.Spinbox(
            auto_lock_frame,
            from_=1,
            to=120,
            textvariable=lock_timeout_var,
            style="Setting.Wabi.TSpinbox",
            command=self._on_setting_changed
        )
        lock_timeout_spin.pack(fill=tk.X, padx=8, pady=4)
    
    def _create_wabi_sabi_tab(self):
        """
        侘び寂び設定タブを作成します
        """
        wabi_frame = ttk.Frame(self.notebook, style="TabContent.Wabi.TFrame")
        self.notebook.add(wabi_frame, text="🌸 侘び寂び")
        
        # スクロール可能フレーム
        canvas = tk.Canvas(wabi_frame, bg=self.wabi_colors["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(wabi_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style="Scrollable.Wabi.TFrame")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollregion=canvas.bbox("all"))
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 侘び寂び哲学説明
        philosophy_frame = ttk.LabelFrame(scrollable_frame, text="🌸 侘び寂びとは", style="Section.Wabi.TLabelframe")
        philosophy_frame.pack(fill=tk.X, padx=16, pady=8)
        
        philosophy_text = """侘び寂び（わびさび）は、日本古来の美意識です。

「侘び」- 質素で静かなものの中に美しさを見出すこと
「寂び」- 時間の経過とともに生まれる風情や趣を愛でること

WabiMailは、この精神をデジタルの世界に取り入れ、
シンプルで心地よいメール体験を提供します。"""
        
        philosophy_label = ttk.Label(
            philosophy_frame,
            text=philosophy_text,
            style="Description.Wabi.TLabel",
            justify=tk.LEFT,
            wraplength=600
        )
        philosophy_label.pack(padx=8, pady=8)
        
        # 侘び寂び設定
        wabi_settings_frame = ttk.LabelFrame(scrollable_frame, text="🌸 侘び寂び体験設定", style="Section.Wabi.TLabelframe")
        wabi_settings_frame.pack(fill=tk.X, padx=16, pady=8)
        
        # ミニマリズム度
        ttk.Label(wabi_settings_frame, text="ミニマリズム度:", style="Label.Wabi.TLabel").pack(anchor=tk.W, padx=8, pady=4)
        
        minimalism_var = tk.IntVar()
        self.settings_vars["wabi_sabi.minimalism_level"] = minimalism_var
        
        minimalism_scale = ttk.Scale(
            wabi_settings_frame,
            from_=1,
            to=5,
            variable=minimalism_var,
            orient=tk.HORIZONTAL,
            style="WabiSabi.Wabi.TScale",
            command=self._on_wabi_setting_changed
        )
        minimalism_scale.pack(fill=tk.X, padx=8, pady=4)
        
        # アニメーション設定
        animation_var = tk.BooleanVar()
        self.settings_vars["wabi_sabi.subtle_animations"] = animation_var
        
        animation_check = ttk.Checkbutton(
            wabi_settings_frame,
            text="控えめなアニメーション効果",
            variable=animation_var,
            style="Setting.Wabi.TCheckbutton",
            command=self._on_setting_changed
        )
        animation_check.pack(anchor=tk.W, padx=8, pady=4)
        
        # 季節テーマ
        seasonal_var = tk.BooleanVar()
        self.settings_vars["wabi_sabi.seasonal_theme"] = seasonal_var
        
        seasonal_check = ttk.Checkbutton(
            wabi_settings_frame,
            text="季節に応じたテーマ変更",
            variable=seasonal_var,
            style="Setting.Wabi.TCheckbutton",
            command=self._on_setting_changed
        )
        seasonal_check.pack(anchor=tk.W, padx=8, pady=4)
        
        # 侘び寂び引用
        quotes_frame = ttk.LabelFrame(scrollable_frame, text="📜 侘び寂びの言葉", style="Section.Wabi.TLabelframe")
        quotes_frame.pack(fill=tk.X, padx=16, pady=8)
        
        quote_text = """「美しいものは、見る人の心の中にある」
「不完全であることの美しさ」
「時の流れが生み出す静寂な美」

静寂の中の美しさを追求して"""
        
        quote_label = ttk.Label(
            quotes_frame,
            text=quote_text,
            style="Quote.Wabi.TLabel",
            justify=tk.CENTER,
            font=("Yu Gothic UI", 9, "italic")
        )
        quote_label.pack(padx=8, pady=8)
    
    def _create_advanced_tab(self):
        """
        高度な設定タブを作成します
        """
        advanced_frame = ttk.Frame(self.notebook, style="TabContent.Wabi.TFrame")
        self.notebook.add(advanced_frame, text="🔧 高度")
        
        # スクロール可能フレーム
        canvas = tk.Canvas(advanced_frame, bg=self.wabi_colors["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(advanced_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style="Scrollable.Wabi.TFrame")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # ログ設定
        logging_frame = ttk.LabelFrame(scrollable_frame, text="📊 ログ設定", style="Section.Wabi.TLabelframe")
        logging_frame.pack(fill=tk.X, padx=16, pady=8)
        
        ttk.Label(logging_frame, text="ログレベル:", style="Label.Wabi.TLabel").pack(anchor=tk.W, padx=8, pady=4)
        
        log_level_var = tk.StringVar()
        self.settings_vars["logging.level"] = log_level_var
        
        log_level_combo = ttk.Combobox(
            logging_frame,
            textvariable=log_level_var,
            values=["DEBUG", "INFO", "WARNING", "ERROR"],
            state="readonly",
            style="Setting.Wabi.TCombobox"
        )
        log_level_combo.pack(fill=tk.X, padx=8, pady=4)
        log_level_combo.bind("<<ComboboxSelected>>", self._on_setting_changed)
        
        file_logging_var = tk.BooleanVar()
        self.settings_vars["logging.file_enabled"] = file_logging_var
        
        file_logging_check = ttk.Checkbutton(
            logging_frame,
            text="ファイルへのログ出力",
            variable=file_logging_var,
            style="Setting.Wabi.TCheckbutton",
            command=self._on_setting_changed
        )
        file_logging_check.pack(anchor=tk.W, padx=8, pady=4)
        
        # 設定管理
        config_frame = ttk.LabelFrame(scrollable_frame, text="⚙️ 設定管理", style="Section.Wabi.TLabelframe")
        config_frame.pack(fill=tk.X, padx=16, pady=8)
        
        # 設定エクスポート
        export_button = ttk.Button(
            config_frame,
            text="設定をエクスポート",
            style="Action.Wabi.TButton",
            command=self._export_settings
        )
        export_button.pack(fill=tk.X, padx=8, pady=4)
        
        # 設定インポート
        import_button = ttk.Button(
            config_frame,
            text="設定をインポート",
            style="Action.Wabi.TButton",
            command=self._import_settings
        )
        import_button.pack(fill=tk.X, padx=8, pady=4)
        
        # 設定リセット
        reset_button = ttk.Button(
            config_frame,
            text="設定をリセット",
            style="Warning.Wabi.TButton",
            command=self._reset_settings
        )
        reset_button.pack(fill=tk.X, padx=8, pady=4)
        
        # 開発者設定
        dev_frame = ttk.LabelFrame(scrollable_frame, text="🛠️ 開発者設定", style="Section.Wabi.TLabelframe")
        dev_frame.pack(fill=tk.X, padx=16, pady=8)
        
        debug_mode_var = tk.BooleanVar()
        self.settings_vars["debug.enabled"] = debug_mode_var
        
        debug_check = ttk.Checkbutton(
            dev_frame,
            text="デバッグモードを有効にする",
            variable=debug_mode_var,
            style="Setting.Wabi.TCheckbutton",
            command=self._on_setting_changed
        )
        debug_check.pack(anchor=tk.W, padx=8, pady=4)
        
        # 設定フォルダを開く
        config_folder_button = ttk.Button(
            dev_frame,
            text="設定フォルダを開く",
            style="Action.Wabi.TButton",
            command=self._open_config_folder
        )
        config_folder_button.pack(fill=tk.X, padx=8, pady=4)
    
    def _create_button_frame(self):
        """
        ボタンフレームを作成します
        """
        button_frame = ttk.Frame(self.window, style="ButtonFrame.Wabi.TFrame")
        button_frame.pack(fill=tk.X, padx=16, pady=8)
        
        # 右寄せボタン
        right_frame = ttk.Frame(button_frame)
        right_frame.pack(side=tk.RIGHT)
        
        # キャンセルボタン
        cancel_button = ttk.Button(
            right_frame,
            text="キャンセル",
            style="Cancel.Wabi.TButton",
            command=self._cancel_settings
        )
        cancel_button.pack(side=tk.RIGHT, padx=(0, 8))
        
        # 適用ボタン
        apply_button = ttk.Button(
            right_frame,
            text="適用",
            style="Apply.Wabi.TButton",
            command=self._apply_settings
        )
        apply_button.pack(side=tk.RIGHT, padx=(0, 8))
        
        # OKボタン
        ok_button = ttk.Button(
            right_frame,
            text="OK",
            style="OK.Wabi.TButton",
            command=self._ok_settings
        )
        ok_button.pack(side=tk.RIGHT, padx=(0, 8))
        
        # 左寄せボタン
        left_frame = ttk.Frame(button_frame)
        left_frame.pack(side=tk.LEFT)
        
        # ヘルプボタン
        help_button = ttk.Button(
            left_frame,
            text="ヘルプ",
            style="Help.Wabi.TButton",
            command=self._show_help
        )
        help_button.pack(side=tk.LEFT)
    
    def _create_status_bar(self):
        """
        ステータスバーを作成します
        """
        status_frame = ttk.Frame(self.window, style="StatusBar.Wabi.TFrame")
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = ttk.Label(
            status_frame,
            text="⚙️ 設定を編集中...",
            style="Status.Wabi.TLabel"
        )
        self.status_label.pack(side=tk.LEFT, padx=8, pady=4)
    
    def _load_settings(self):
        """
        現在の設定値をUIにロードします
        """
        try:
            # 設定値をUIコンポーネントにロード
            for key, var in self.settings_vars.items():
                if key == "mail.signature.text":
                    # Textウィジェットの場合
                    value = self.config.get(key, "")
                    var.delete("1.0", tk.END)
                    var.insert("1.0", value)
                else:
                    # 変数の場合
                    value = self.config.get(key, self._get_default_value(key))
                    if hasattr(var, 'set'):
                        var.set(value)
            
            self._update_status("✅ 設定を読み込みました")
            logger.info("設定をUIにロードしました")
            
        except Exception as e:
            logger.error(f"設定読み込みエラー: {e}")
            self._update_status("❌ 設定読み込みでエラーが発生しました")
    
    def _get_default_value(self, key: str):
        """
        設定キーのデフォルト値を取得します
        
        Args:
            key: 設定キー
            
        Returns:
            デフォルト値
        """
        defaults = {
            "app.language": "ja",
            "app.theme": "wabi_sabi_light",
            "ui.font.family": "Yu Gothic UI",
            "ui.font.size": 10,
            "ui.colors.background": "#FEFEFE",
            "ui.layout.left_pane_width": 250,
            "ui.layout.show_preview": True,
            "mail.auto_check": True,
            "mail.check_interval": 5,
            "mail.notifications.enabled": True,
            "mail.notifications.sound": False,
            "mail.signature.enabled": False,
            "mail.signature.text": "",
            "security.encryption_enabled": True,
            "security.remember_passwords": True,
            "security.auto_lock": False,
            "security.lock_timeout": 15,
            "startup.auto_start": False,
            "startup.minimize_to_tray": False,
            "update.auto_check": True,
            "logging.level": "INFO",
            "logging.file_enabled": True,
            "wabi_sabi.minimalism_level": 3,
            "wabi_sabi.subtle_animations": True,
            "wabi_sabi.seasonal_theme": True,
            "debug.enabled": False
        }
        
        return defaults.get(key, None)
    
    def _on_setting_changed(self, event=None):
        """
        設定変更イベント
        """
        self.changes_made = True
        self._update_status("📝 設定が変更されました")
    
    def _on_theme_changed(self, event=None):
        """
        テーマ変更イベント
        """
        self._on_setting_changed()
        self._update_status("🎨 テーマが変更されました（適用ボタンを押してください）")
    
    def _on_wabi_setting_changed(self, event=None):
        """
        侘び寂び設定変更イベント
        """
        self._on_setting_changed()
        self._update_status("🌸 侘び寂び設定が変更されました")
    
    def _on_tab_changed(self, event=None):
        """
        タブ変更イベント
        """
        selected_tab = self.notebook.tab("current", "text")
        self._update_status(f"📋 {selected_tab} タブを表示中")
    
    def _pick_color(self, color_var, title):
        """
        色選択ダイアログを表示します
        
        Args:
            color_var: 色を格納する変数
            title: ダイアログタイトル
        """
        current_color = color_var.get() or "#FFFFFF"
        color = colorchooser.askcolor(
            title=title,
            color=current_color,
            parent=self.window
        )[1]
        
        if color:
            color_var.set(color)
            self._on_setting_changed()
            self._update_status(f"🎨 {title}を変更しました: {color}")
    
    def _check_updates(self):
        """
        アップデートを確認します
        """
        self._update_status("🔄 アップデートを確認中...")
        
        def check_in_background():
            try:
                # アップデート確認の模擬処理
                import time
                time.sleep(2)
                
                # UIスレッドで結果を表示
                self.window.after(0, lambda: self._show_update_result(True, "最新版です"))
                
            except Exception as e:
                self.window.after(0, lambda: self._show_update_result(False, str(e)))
        
        threading.Thread(target=check_in_background, daemon=True).start()
    
    def _show_update_result(self, success, message):
        """
        アップデート確認結果を表示します
        """
        if success:
            self._update_status("✅ アップデート確認完了")
            messagebox.showinfo("アップデート確認", message, parent=self.window)
        else:
            self._update_status("❌ アップデート確認に失敗しました")
            messagebox.showerror("エラー", f"アップデート確認でエラーが発生しました:\n{message}", parent=self.window)
    
    def _export_settings(self):
        """
        設定をエクスポートします
        """
        file_path = filedialog.asksaveasfilename(
            title="設定をエクスポート",
            defaultextension=".yaml",
            filetypes=[("YAML files", "*.yaml"), ("JSON files", "*.json")],
            parent=self.window
        )
        
        if file_path:
            try:
                import yaml
                settings = self.config.get_all()
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    yaml.dump(settings, f, default_flow_style=False, allow_unicode=True)
                
                self._update_status(f"✅ 設定をエクスポートしました: {file_path}")
                messagebox.showinfo("エクスポート完了", f"設定を正常にエクスポートしました:\n{file_path}", parent=self.window)
                
            except Exception as e:
                logger.error(f"設定エクスポートエラー: {e}")
                self._update_status("❌ 設定エクスポートに失敗しました")
                messagebox.showerror("エラー", f"設定のエクスポートに失敗しました:\n{e}", parent=self.window)
    
    def _import_settings(self):
        """
        設定をインポートします
        """
        file_path = filedialog.askopenfilename(
            title="設定をインポート",
            filetypes=[("YAML files", "*.yaml"), ("JSON files", "*.json")],
            parent=self.window
        )
        
        if file_path:
            result = messagebox.askyesno(
                "設定インポート確認",
                "現在の設定は上書きされます。よろしいですか？",
                parent=self.window
            )
            
            if result:
                try:
                    import yaml
                    with open(file_path, 'r', encoding='utf-8') as f:
                        imported_settings = yaml.safe_load(f)
                    
                    # 設定を更新
                    self.config._config = imported_settings
                    self.config.save_config()
                    
                    # UIを再読み込み
                    self._load_settings()
                    
                    self._update_status(f"✅ 設定をインポートしました: {file_path}")
                    messagebox.showinfo("インポート完了", f"設定を正常にインポートしました:\n{file_path}", parent=self.window)
                    
                except Exception as e:
                    logger.error(f"設定インポートエラー: {e}")
                    self._update_status("❌ 設定インポートに失敗しました")
                    messagebox.showerror("エラー", f"設定のインポートに失敗しました:\n{e}", parent=self.window)
    
    def _reset_settings(self):
        """
        設定をリセットします
        """
        result = messagebox.askyesno(
            "設定リセット確認",
            "すべての設定をデフォルト値にリセットします。\nこの操作は取り消せません。よろしいですか？",
            icon=messagebox.WARNING,
            parent=self.window
        )
        
        if result:
            try:
                self.config.reset_to_default()
                self._load_settings()
                
                self._update_status("✅ 設定をリセットしました")
                messagebox.showinfo("リセット完了", "設定を正常にリセットしました。", parent=self.window)
                
            except Exception as e:
                logger.error(f"設定リセットエラー: {e}")
                self._update_status("❌ 設定リセットに失敗しました")
                messagebox.showerror("エラー", f"設定のリセットに失敗しました:\n{e}", parent=self.window)
    
    def _open_config_folder(self):
        """
        設定フォルダを開きます
        """
        try:
            import subprocess
            import platform
            
            config_path = str(self.config.config_dir)
            
            if platform.system() == "Windows":
                subprocess.run(["explorer", config_path])
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", config_path])
            else:  # Linux
                subprocess.run(["xdg-open", config_path])
            
            self._update_status(f"📂 設定フォルダを開きました: {config_path}")
            
        except Exception as e:
            logger.error(f"設定フォルダオープンエラー: {e}")
            self._update_status("❌ 設定フォルダを開けませんでした")
            messagebox.showerror("エラー", f"設定フォルダを開けませんでした:\n{e}", parent=self.window)
    
    def _save_current_settings(self):
        """
        現在のUI設定を保存します
        """
        try:
            # UIコンポーネントから値を取得して設定に反映
            for key, var in self.settings_vars.items():
                if key == "mail.signature.text":
                    # Textウィジェットの場合
                    value = var.get("1.0", tk.END).strip()
                else:
                    # 変数の場合
                    value = var.get()
                
                self.config.set(key, value)
            
            # 設定を保存
            self.config.save_config()
            
            return True
            
        except Exception as e:
            logger.error(f"設定保存エラー: {e}")
            return False
    
    def _apply_settings(self):
        """
        設定を適用します
        """
        if self._save_current_settings():
            self.changes_made = False
            self._update_status("✅ 設定を適用しました")
            
            # コールバックを実行
            if self.on_settings_changed:
                try:
                    self.on_settings_changed()
                except Exception as e:
                    logger.warning(f"設定変更コールバックエラー: {e}")
            
            messagebox.showinfo("設定適用", "設定を正常に適用しました。", parent=self.window)
            logger.info("設定を適用しました")
        else:
            self._update_status("❌ 設定の適用に失敗しました")
            messagebox.showerror("エラー", "設定の適用に失敗しました。", parent=self.window)
    
    def _ok_settings(self):
        """
        OKボタン処理（適用して閉じる）
        """
        if self.changes_made:
            if self._save_current_settings():
                # コールバックを実行
                if self.on_settings_changed:
                    try:
                        self.on_settings_changed()
                    except Exception as e:
                        logger.warning(f"設定変更コールバックエラー: {e}")
                
                self.window.destroy()
                logger.info("設定を適用してウィンドウを閉じました")
            else:
                messagebox.showerror("エラー", "設定の保存に失敗しました。", parent=self.window)
        else:
            self.window.destroy()
            logger.info("設定ウィンドウを閉じました")
    
    def _cancel_settings(self):
        """
        キャンセルボタン処理
        """
        if self.changes_made:
            result = messagebox.askyesno(
                "確認",
                "変更された設定は保存されません。よろしいですか？",
                parent=self.window
            )
            if not result:
                return
        
        self.window.destroy()
        logger.info("設定をキャンセルしてウィンドウを閉じました")
    
    def _show_help(self):
        """
        ヘルプを表示します
        """
        help_text = """🌸 WabiMail 設定ヘルプ

【一般設定】
• 言語、起動、アップデート設定

【外観設定】 
• テーマ、フォント、色彩、レイアウト設定

【メール設定】
• チェック間隔、通知、署名設定

【セキュリティ設定】
• 暗号化、パスワード管理、自動ロック

【侘び寂び設定】
• 侘び寂びの美学に基づく体験設定

【高度な設定】
• ログ、設定管理、開発者向け機能

🌸 静寂の中の美しさを追求して"""
        
        messagebox.showinfo("ヘルプ", help_text, parent=self.window)
    
    def _on_window_close(self):
        """
        ウィンドウ閉じるイベント
        """
        self._cancel_settings()
    
    def _update_status(self, message: str):
        """
        ステータスメッセージを更新します
        
        Args:
            message: ステータスメッセージ
        """
        if self.status_label:
            self.status_label.config(text=message)
        logger.debug(f"設定画面ステータス: {message}")


def show_settings_window(parent, config: AppConfig, 
                        on_settings_changed: Optional[Callable] = None):
    """
    設定ウィンドウを表示します
    
    Args:
        parent: 親ウィンドウ
        config: アプリケーション設定
        on_settings_changed: 設定変更コールバック
    
    Returns:
        SettingsWindow: 作成された設定ウィンドウインスタンス
    """
    try:
        settings_window = SettingsWindow(
            parent=parent,
            config=config,
            on_settings_changed=on_settings_changed
        )
        
        return settings_window
        
    except Exception as e:
        logger.error(f"設定ウィンドウ表示エラー: {e}")
        messagebox.showerror(
            "エラー",
            f"設定ウィンドウの表示に失敗しました:\n{e}",
            parent=parent
        )
        return None