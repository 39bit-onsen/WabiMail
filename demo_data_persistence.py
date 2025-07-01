#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
データ永続化デモアプリケーション

Task 11: データ永続化システムの動作確認用デモ
- SecureStorageの暗号化機能
- AccountStorageのアカウント管理
- MailStorageのメールキャッシュ
- 統合ストレージシステム
"""

import sys
import os
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime
import tempfile

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.storage.secure_storage import SecureStorage
from src.storage.account_storage import AccountStorage
from src.storage.mail_storage import MailStorage
from src.mail.account import Account, AccountType, AuthType, AccountSettings
from src.mail.mail_message import MailMessage, MailAttachment


class DataPersistenceDemo:
    """データ永続化デモクラス"""
    
    def __init__(self):
        """デモアプリケーションを初期化"""
        self.root = tk.Tk()
        self.root.title("🌸 WabiMail データ永続化デモ")
        self.root.geometry("800x600")
        
        # デモ用一時ディレクトリ
        self.demo_dir = Path(tempfile.mkdtemp(prefix="wabimail_demo_"))
        
        # ストレージシステム初期化
        self.secure_storage = SecureStorage(str(self.demo_dir))
        self.account_storage = AccountStorage(str(self.demo_dir))
        self.mail_storage = MailStorage(str(self.demo_dir))
        
        # UI作成
        self._create_ui()
        
        print("🌸 WabiMail データ永続化デモ")
        print("="*60)
        print("🔒 デモ内容:")
        print("• セキュア暗号化ストレージ")
        print("• アカウント情報の安全な保存")
        print("• メールキャッシュシステム")
        print("• 統合データ管理")
        print(f"📁 デモディレクトリ: {self.demo_dir}")
        print()
        print("✨ 各ボタンをクリックして機能をお試しください")
    
    def _create_ui(self):
        """デモUI作成"""
        # メインタイトル
        title_label = tk.Label(
            self.root,
            text="🌸 WabiMail データ永続化デモ",
            font=("Yu Gothic UI", 16, "bold"),
            pady=15
        )
        title_label.pack()
        
        # ノートブック（タブ）
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 各タブを作成
        self._create_secure_storage_tab()
        self._create_account_storage_tab()
        self._create_mail_storage_tab()
        self._create_integration_tab()
        
        # ステータス表示
        self.status_label = tk.Label(
            self.root,
            text="デモの準備ができました",
            font=("Yu Gothic UI", 9),
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_label.pack(fill=tk.X, padx=5, pady=5)
        
        # 終了ボタン
        quit_button = tk.Button(
            self.root,
            text="❌ デモ終了",
            font=("Yu Gothic UI", 10),
            command=self._cleanup_and_quit,
            bg="#ffe0e0",
            relief=tk.FLAT,
            pady=3
        )
        quit_button.pack(pady=5)
    
    def _create_secure_storage_tab(self):
        """セキュアストレージタブ"""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="🔒 セキュアストレージ")
        
        # 説明
        desc_label = tk.Label(
            tab_frame,
            text="暗号化された安全なデータストレージシステムをテストします",
            font=("Yu Gothic UI", 10),
            pady=10
        )
        desc_label.pack()
        
        # 暗号化テストセクション
        crypto_frame = tk.LabelFrame(tab_frame, text="暗号化・復号テスト", font=("Yu Gothic UI", 11))
        crypto_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # テキスト入力
        tk.Label(crypto_frame, text="暗号化するテキスト:", font=("Yu Gothic UI", 9)).pack(anchor=tk.W, padx=10, pady=5)
        self.crypto_input = tk.Entry(crypto_frame, font=("Yu Gothic UI", 9), width=60)
        self.crypto_input.pack(padx=10, pady=5)
        self.crypto_input.insert(0, "これは秘密のデータです 🔐")
        
        # 暗号化ボタン
        encrypt_button = tk.Button(
            crypto_frame,
            text="🔒 暗号化",
            command=self._demo_encryption,
            bg="#f0f8ff",
            relief=tk.FLAT,
            pady=3
        )
        encrypt_button.pack(pady=5)
        
        # 結果表示
        tk.Label(crypto_frame, text="暗号化結果:", font=("Yu Gothic UI", 9)).pack(anchor=tk.W, padx=10, pady=(10,0))
        self.crypto_result = scrolledtext.ScrolledText(crypto_frame, height=4, font=("Consolas", 8))
        self.crypto_result.pack(fill=tk.X, padx=10, pady=5)
        
        # 設定保存テストセクション
        settings_frame = tk.LabelFrame(tab_frame, text="設定保存テスト", font=("Yu Gothic UI", 11))
        settings_frame.pack(fill=tk.X, padx=20, pady=10)
        
        settings_button = tk.Button(
            settings_frame,
            text="⚙️ 設定保存・読み込みテスト",
            command=self._demo_settings,
            bg="#f0f8ff",
            relief=tk.FLAT,
            pady=3
        )
        settings_button.pack(pady=10)
    
    def _create_account_storage_tab(self):
        """アカウントストレージタブ"""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="📧 アカウントストレージ")
        
        # 説明
        desc_label = tk.Label(
            tab_frame,
            text="アカウント情報の暗号化保存・管理システムをテストします",
            font=("Yu Gothic UI", 10),
            pady=10
        )
        desc_label.pack()
        
        # アカウント作成セクション
        create_frame = tk.LabelFrame(tab_frame, text="テストアカウント作成", font=("Yu Gothic UI", 11))
        create_frame.pack(fill=tk.X, padx=20, pady=10)
        
        create_button = tk.Button(
            create_frame,
            text="📧 テストアカウントを作成",
            command=self._demo_create_account,
            bg="#f0f8ff",
            relief=tk.FLAT,
            pady=5
        )
        create_button.pack(pady=10)
        
        # アカウント一覧セクション
        list_frame = tk.LabelFrame(tab_frame, text="アカウント一覧", font=("Yu Gothic UI", 11))
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        list_button = tk.Button(
            list_frame,
            text="📋 アカウント一覧を更新",
            command=self._demo_list_accounts,
            bg="#f0f8ff",
            relief=tk.FLAT,
            pady=3
        )
        list_button.pack(pady=5)
        
        self.account_list = scrolledtext.ScrolledText(list_frame, height=8, font=("Yu Gothic UI", 9))
        self.account_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def _create_mail_storage_tab(self):
        """メールストレージタブ"""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="📬 メールストレージ")
        
        # 説明
        desc_label = tk.Label(
            tab_frame,
            text="メールのローカルキャッシュ・検索システムをテストします",
            font=("Yu Gothic UI", 10),
            pady=10
        )
        desc_label.pack()
        
        # メールキャッシュセクション
        cache_frame = tk.LabelFrame(tab_frame, text="メールキャッシュテスト", font=("Yu Gothic UI", 11))
        cache_frame.pack(fill=tk.X, padx=20, pady=10)
        
        cache_button = tk.Button(
            cache_frame,
            text="📬 テストメールをキャッシュ",
            command=self._demo_cache_mail,
            bg="#f0f8ff",
            relief=tk.FLAT,
            pady=5
        )
        cache_button.pack(pady=10)
        
        # 検索セクション
        search_frame = tk.LabelFrame(tab_frame, text="メール検索", font=("Yu Gothic UI", 11))
        search_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # 検索入力
        search_input_frame = tk.Frame(search_frame)
        search_input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(search_input_frame, text="検索キーワード:", font=("Yu Gothic UI", 9)).pack(side=tk.LEFT)
        self.search_input = tk.Entry(search_input_frame, font=("Yu Gothic UI", 9))
        self.search_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.search_input.insert(0, "テスト")
        
        search_button = tk.Button(
            search_input_frame,
            text="🔍 検索",
            command=self._demo_search_mail,
            bg="#f0f8ff",
            relief=tk.FLAT
        )
        search_button.pack(side=tk.RIGHT)
        
        # 検索結果表示
        self.search_result = scrolledtext.ScrolledText(search_frame, height=6, font=("Yu Gothic UI", 9))
        self.search_result.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def _create_integration_tab(self):
        """統合タブ"""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="🔗 統合テスト")
        
        # 説明
        desc_label = tk.Label(
            tab_frame,
            text="すべてのストレージシステムの統合動作をテストします",
            font=("Yu Gothic UI", 10),
            pady=10
        )
        desc_label.pack()
        
        # 統合テストボタン
        integration_button = tk.Button(
            tab_frame,
            text="🚀 完全統合テスト実行",
            command=self._demo_full_integration,
            bg="#90EE90",
            relief=tk.FLAT,
            font=("Yu Gothic UI", 12, "bold"),
            pady=10
        )
        integration_button.pack(pady=20)
        
        # ストレージ情報セクション
        info_frame = tk.LabelFrame(tab_frame, text="ストレージ情報", font=("Yu Gothic UI", 11))
        info_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        info_button = tk.Button(
            info_frame,
            text="📊 ストレージ情報を更新",
            command=self._demo_storage_info,
            bg="#f0f8ff",
            relief=tk.FLAT,
            pady=3
        )
        info_button.pack(pady=5)
        
        self.storage_info = scrolledtext.ScrolledText(info_frame, height=10, font=("Consolas", 9))
        self.storage_info.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def _demo_encryption(self):
        """暗号化デモ"""
        try:
            text = self.crypto_input.get()
            if not text:
                messagebox.showwarning("警告", "暗号化するテキストを入力してください")
                return
            
            # 暗号化
            encrypted = self.secure_storage.encrypt_data(text)
            
            # 復号
            decrypted = self.secure_storage.decrypt_data(encrypted)
            
            # 結果表示
            result = f"元のテキスト: {text}\n\n"
            result += f"暗号化データ: {encrypted[:100]}...\n\n"
            result += f"復号結果: {decrypted}\n\n"
            result += f"検証: {'✅ 成功' if text == decrypted else '❌ 失敗'}"
            
            self.crypto_result.delete(1.0, tk.END)
            self.crypto_result.insert(1.0, result)
            
            self._update_status("🔒 暗号化・復号テストが完了しました")
            
        except Exception as e:
            messagebox.showerror("エラー", f"暗号化テストエラー: {e}")
    
    def _demo_settings(self):
        """設定保存デモ"""
        try:
            # 設定を保存
            settings = {
                "theme": "wabi_sabi_light",
                "font_size": 12,
                "auto_check": True,
                "check_interval": 300
            }
            
            for key, value in settings.items():
                self.secure_storage.save_app_setting(f"demo.{key}", value)
            
            # 設定を読み込み
            loaded_settings = {}
            for key in settings.keys():
                loaded_settings[key] = self.secure_storage.load_app_setting(f"demo.{key}")
            
            # 結果確認
            success = all(settings[key] == loaded_settings[key] for key in settings.keys())
            
            if success:
                messagebox.showinfo("成功", f"設定の保存・読み込みが成功しました\n\n設定項目: {len(settings)}個")
                self._update_status("⚙️ 設定保存・読み込みテストが完了しました")
            else:
                messagebox.showerror("エラー", "設定の保存・読み込みで不整合が発生しました")
                
        except Exception as e:
            messagebox.showerror("エラー", f"設定テストエラー: {e}")
    
    def _demo_create_account(self):
        """アカウント作成デモ"""
        try:
            # デモ用アカウントを作成
            demo_accounts = [
                {
                    "id": "demo_gmail_001",
                    "name": "デモGmailアカウント",
                    "email": "demo@gmail.com",
                    "type": AccountType.GMAIL,
                    "auth": AuthType.OAUTH2
                },
                {
                    "id": "demo_imap_001", 
                    "name": "デモIMAPアカウント",
                    "email": "demo@example.com",
                    "type": AccountType.IMAP,
                    "auth": AuthType.PASSWORD
                }
            ]
            
            created_count = 0
            for account_data in demo_accounts:
                account = Account(
                    account_id=account_data["id"],
                    name=account_data["name"],
                    email_address=account_data["email"],
                    account_type=account_data["type"],
                    auth_type=account_data["auth"],
                    settings=AccountSettings(
                        incoming_server="mail.example.com",
                        incoming_port=993,
                        incoming_security="SSL",
                        outgoing_server="smtp.example.com",
                        outgoing_port=587,
                        outgoing_security="STARTTLS",
                        requires_auth=True
                    )
                )
                
                success, message = self.account_storage.save_account(account)
                if success:
                    created_count += 1
            
            messagebox.showinfo("成功", f"{created_count}個のデモアカウントを作成しました")
            self._update_status(f"📧 {created_count}個のアカウントを作成しました")
            
            # アカウント一覧を更新
            self._demo_list_accounts()
            
        except Exception as e:
            messagebox.showerror("エラー", f"アカウント作成エラー: {e}")
    
    def _demo_list_accounts(self):
        """アカウント一覧デモ"""
        try:
            accounts = self.account_storage.list_accounts()
            
            result = f"📧 登録アカウント一覧 ({len(accounts)}個)\n"
            result += "=" * 50 + "\n\n"
            
            for i, account in enumerate(accounts, 1):
                result += f"{i}. {account['name']}\n"
                result += f"   メール: {account['email_address']}\n"
                result += f"   タイプ: {account['account_type']}\n"
                result += f"   認証: {account['auth_type']}\n"
                result += f"   更新: {account['updated_at']}\n\n"
            
            if not accounts:
                result += "登録されているアカウントはありません。\n"
                result += "「テストアカウントを作成」ボタンでアカウントを作成してください。"
            
            self.account_list.delete(1.0, tk.END)
            self.account_list.insert(1.0, result)
            
            self._update_status(f"📋 アカウント一覧を更新しました ({len(accounts)}個)")
            
        except Exception as e:
            messagebox.showerror("エラー", f"アカウント一覧取得エラー: {e}")
    
    def _demo_cache_mail(self):
        """メールキャッシュデモ"""
        try:
            # デモ用メッセージを作成
            demo_messages = [
                {
                    "uid": "demo_001",
                    "subject": "🌸 WabiMail テストメール 1",
                    "sender": "test1@wabimail.example.com",
                    "body": "これは侘び寂びの美学に基づいたメールクライアントのテストメールです。"
                },
                {
                    "uid": "demo_002", 
                    "subject": "📧 重要なお知らせ",
                    "sender": "info@wabimail.example.com",
                    "body": "新機能のデータ永続化システムが実装されました。"
                },
                {
                    "uid": "demo_003",
                    "subject": "🔒 セキュリティアップデート",
                    "sender": "security@wabimail.example.com", 
                    "body": "暗号化機能が強化され、より安全にデータを保存できるようになりました。"
                }
            ]
            
            cached_count = 0
            for msg_data in demo_messages:
                message = MailMessage(
                    subject=msg_data["subject"],
                    sender=msg_data["sender"],
                    recipients=["user@wabimail.example.com"],
                    body_text=msg_data["body"],
                    date_received=datetime.now()
                )
                message.uid = msg_data["uid"]
                
                # 添付ファイルも追加
                if "重要" in msg_data["subject"]:
                    attachment = MailAttachment(
                        filename="重要文書.pdf",
                        content_type="application/pdf",
                        size=1024,
                        data=b"fake pdf content"
                    )
                    message.attachments.append(attachment)
                
                success = self.mail_storage.cache_message("demo_account", "INBOX", message)
                if success:
                    cached_count += 1
            
            messagebox.showinfo("成功", f"{cached_count}個のメールをキャッシュしました")
            self._update_status(f"📬 {cached_count}個のメールをキャッシュしました")
            
        except Exception as e:
            messagebox.showerror("エラー", f"メールキャッシュエラー: {e}")
    
    def _demo_search_mail(self):
        """メール検索デモ"""
        try:
            query = self.search_input.get().strip()
            if not query:
                messagebox.showwarning("警告", "検索キーワードを入力してください")
                return
            
            # 検索実行
            results = self.mail_storage.search_cached_messages("demo_account", query)
            
            # 結果表示
            result_text = f"🔍 検索結果: '{query}' ({len(results)}件)\n"
            result_text += "=" * 50 + "\n\n"
            
            for i, message in enumerate(results, 1):
                result_text += f"{i}. {message.subject}\n"
                result_text += f"   送信者: {message.sender}\n"
                result_text += f"   日時: {message.date_received.strftime('%Y-%m-%d %H:%M')}\n"
                result_text += f"   添付: {len(message.attachments)}個\n"
                result_text += f"   本文: {message.body_text[:50]}...\n\n"
            
            if not results:
                result_text += "検索条件に一致するメールが見つかりませんでした。\n"
                result_text += "「テストメールをキャッシュ」ボタンでメールを追加してから検索してください。"
            
            self.search_result.delete(1.0, tk.END)
            self.search_result.insert(1.0, result_text)
            
            self._update_status(f"🔍 検索完了: {len(results)}件のメールが見つかりました")
            
        except Exception as e:
            messagebox.showerror("エラー", f"メール検索エラー: {e}")
    
    def _demo_full_integration(self):
        """完全統合テストデモ"""
        try:
            result = "🚀 完全統合テスト実行結果\n"
            result += "=" * 60 + "\n\n"
            
            # 1. アカウント作成・保存
            test_account = Account(
                account_id="integration_test",
                name="統合テストアカウント",
                email_address="integration@wabimail.example.com",
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
            
            success1, _ = self.account_storage.save_account(test_account)
            result += f"1. アカウント保存: {'✅ 成功' if success1 else '❌ 失敗'}\n"
            
            # 2. OAuth2トークン保存
            token_data = {
                "access_token": "integration_access_token",
                "refresh_token": "integration_refresh_token",
                "expires_in": 3600
            }
            success2 = self.account_storage.save_oauth2_token("integration_test", token_data)
            result += f"2. OAuth2トークン保存: {'✅ 成功' if success2 else '❌ 失敗'}\n"
            
            # 3. メールキャッシュ
            test_message = MailMessage(
                subject="統合テストメール",
                sender="integration@wabimail.example.com",
                recipients=["test@example.com"],
                body_text="統合テスト用のメールメッセージです。",
                date_received=datetime.now()
            )
            test_message.uid = "integration_001"
            
            success3 = self.mail_storage.cache_message("integration_test", "INBOX", test_message)
            result += f"3. メールキャッシュ: {'✅ 成功' if success3 else '❌ 失敗'}\n"
            
            # 4. データ読み込み検証
            loaded_account = self.account_storage.load_account("integration_test")
            loaded_token = self.account_storage.load_oauth2_token("integration_test")
            loaded_message = self.mail_storage.load_cached_message("integration_test", "INBOX", "integration_001")
            
            success4 = all([loaded_account, loaded_token, loaded_message])
            result += f"4. データ読み込み検証: {'✅ 成功' if success4 else '❌ 失敗'}\n\n"
            
            # 5. 統合結果
            overall_success = all([success1, success2, success3, success4])
            result += f"🎯 統合テスト結果: {'✅ 全て成功' if overall_success else '❌ 一部失敗'}\n\n"
            
            # 詳細情報
            if overall_success:
                result += "📊 詳細情報:\n"
                result += f"- アカウント名: {loaded_account.name}\n"
                result += f"- メールアドレス: {loaded_account.email_address}\n"
                result += f"- トークン有効期限: {loaded_token['expires_in']}秒\n"
                result += f"- キャッシュメール件名: {loaded_message.subject}\n"
            
            messagebox.showinfo("統合テスト完了", "統合テストが完了しました。詳細は統合タブで確認してください。")
            self._update_status("🚀 完全統合テストが完了しました")
            
            # 統合タブのテキストエリアに結果を表示
            self.storage_info.delete(1.0, tk.END)
            self.storage_info.insert(1.0, result)
            
        except Exception as e:
            messagebox.showerror("エラー", f"統合テストエラー: {e}")
    
    def _demo_storage_info(self):
        """ストレージ情報デモ"""
        try:
            info_text = "📊 WabiMail ストレージシステム情報\n"
            info_text += "=" * 60 + "\n\n"
            
            # セキュアストレージ情報
            secure_info = self.secure_storage.get_storage_info()
            info_text += "🔒 セキュアストレージ:\n"
            info_text += f"   ディレクトリ: {secure_info.get('storage_dir', 'N/A')}\n"
            info_text += f"   データベースサイズ: {secure_info.get('database_size_bytes', 0):,} bytes\n"
            info_text += f"   暗号化: {'有効' if secure_info.get('encryption_enabled') else '無効'}\n"
            info_text += f"   アカウント数: {secure_info.get('accounts_count', 0)}\n"
            info_text += f"   トークン数: {secure_info.get('tokens_count', 0)}\n"
            info_text += f"   設定項目数: {secure_info.get('settings_count', 0)}\n\n"
            
            # アカウントストレージ情報  
            account_info = self.account_storage.get_storage_info()
            info_text += "📧 アカウントストレージ:\n"
            info_text += f"   登録アカウント数: {account_info.get('accounts_count', 0)}\n\n"
            
            # メールストレージ情報
            mail_stats = self.mail_storage.get_cache_stats()
            info_text += "📬 メールストレージ:\n"
            info_text += f"   総メッセージ数: {mail_stats.get('total_messages', 0)}\n"
            info_text += f"   アカウント数: {mail_stats.get('account_count', 0)}\n"
            info_text += f"   フォルダ数: {mail_stats.get('total_folders', 0)}\n\n"
            
            # ファイルシステム情報
            info_text += "📁 ファイルシステム:\n"
            info_text += f"   デモディレクトリ: {self.demo_dir}\n"
            
            db_path = self.demo_dir / "wabimail_data.db"
            if db_path.exists():
                db_size = db_path.stat().st_size
                info_text += f"   データベースファイル: {db_size:,} bytes\n"
            
            self.storage_info.delete(1.0, tk.END)
            self.storage_info.insert(1.0, info_text)
            
            self._update_status("📊 ストレージ情報を更新しました")
            
        except Exception as e:
            messagebox.showerror("エラー", f"ストレージ情報取得エラー: {e}")
    
    def _update_status(self, message: str):
        """ステータス更新"""
        self.status_label.config(text=message)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
    
    def _cleanup_and_quit(self):
        """クリーンアップして終了"""
        try:
            # ストレージを閉じる
            self.secure_storage.close()
            self.account_storage.close()
            self.mail_storage.close()
            
            # 一時ディレクトリをクリーンアップ
            import shutil
            shutil.rmtree(self.demo_dir, ignore_errors=True)
            
            print(f"🧹 クリーンアップ完了: {self.demo_dir}")
            self.root.quit()
            
        except Exception as e:
            print(f"クリーンアップエラー: {e}")
            self.root.quit()
    
    def run(self):
        """デモアプリケーションを実行"""
        try:
            self.root.protocol("WM_DELETE_WINDOW", self._cleanup_and_quit)
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
        demo = DataPersistenceDemo()
        demo.run()
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()