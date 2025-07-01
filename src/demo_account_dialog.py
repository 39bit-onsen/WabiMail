#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
アカウント設定ダイアログのデモンストレーション

G005アカウント設定ダイアログの機能を実際に試すためのデモスクリプトです。
OAuth2認証、手動設定、接続テスト等の機能を確認します。

Author: WabiMail Development Team
Created: 2025-07-01
"""

import sys
from pathlib import Path
import tkinter as tk
from tkinter import messagebox

# プロジェクトルートをPythonパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.ui.account_dialog import show_account_dialog
from src.mail.account import Account, AccountType, AuthType
from src.utils.logger import setup_logger


def demo_new_account():
    """
    新規アカウント作成のデモ
    """
    print("\n" + "="*60)
    print("➕ 新規アカウント作成デモ")
    print("="*60)
    
    root = tk.Tk()
    root.withdraw()  # メインウィンドウを非表示
    
    def on_success(account):
        """成功時のコールバック"""
        print(f"\n✅ アカウントが作成されました:")
        print(f"  名前: {account.name}")
        print(f"  メールアドレス: {account.email_address}")
        print(f"  タイプ: {account.account_type.value}")
        print(f"  認証方式: {account.auth_type.value}")
        print(f"  受信サーバー: {account.settings.incoming_server}:{account.settings.incoming_port}")
        print(f"  送信サーバー: {account.settings.outgoing_server}:{account.settings.outgoing_port}")
        
        messagebox.showinfo("成功", f"アカウント「{account.name}」を作成しました")
    
    try:
        print("新規アカウント作成ダイアログを開きます...")
        result = show_account_dialog(root, success_callback=on_success)
        
        if result:
            print("✅ アカウント作成が完了しました")
        else:
            print("❌ アカウント作成がキャンセルされました")
            
    except Exception as e:
        print(f"❌ エラー: {e}")
    finally:
        root.destroy()


def demo_edit_account():
    """
    アカウント編集のデモ
    """
    print("\n" + "="*60)
    print("✏️ アカウント編集デモ")
    print("="*60)
    
    # サンプルアカウントを作成
    sample_account = Account(
        name="サンプルアカウント",
        email_address="sample@example.com",
        account_type=AccountType.IMAP,
        auth_type=AuthType.PASSWORD,
        display_name="サンプル",
        signature="--\nサンプル署名"
    )
    sample_account.apply_preset_settings()
    sample_account.settings.incoming_server = "imap.example.com"
    sample_account.settings.outgoing_server = "smtp.example.com"
    
    print("編集対象のサンプルアカウント:")
    print(f"  名前: {sample_account.name}")
    print(f"  メールアドレス: {sample_account.email_address}")
    print(f"  タイプ: {sample_account.account_type.value}")
    
    root = tk.Tk()
    root.withdraw()  # メインウィンドウを非表示
    
    def on_success(account):
        """成功時のコールバック"""
        print(f"\n✅ アカウントが更新されました:")
        print(f"  名前: {account.name}")
        print(f"  メールアドレス: {account.email_address}")
        print(f"  表示名: {account.display_name}")
        print(f"  署名: {account.signature}")
        
        messagebox.showinfo("成功", f"アカウント「{account.name}」を更新しました")
    
    try:
        print("アカウント編集ダイアログを開きます...")
        result = show_account_dialog(root, account=sample_account, success_callback=on_success)
        
        if result:
            print("✅ アカウント編集が完了しました")
        else:
            print("❌ アカウント編集がキャンセルされました")
            
    except Exception as e:
        print(f"❌ エラー: {e}")
    finally:
        root.destroy()


def demo_gmail_oauth2():
    """
    Gmail OAuth2設定のデモ
    """
    print("\n" + "="*60)
    print("🔐 Gmail OAuth2設定デモ")
    print("="*60)
    
    # Gmail用サンプルアカウント
    gmail_account = Account(
        name="Gmail テストアカウント",
        email_address="test@gmail.com",
        account_type=AccountType.GMAIL,
        auth_type=AuthType.OAUTH2
    )
    gmail_account.apply_preset_settings()
    
    print("Gmail OAuth2設定用のサンプルアカウント:")
    print(f"  名前: {gmail_account.name}")
    print(f"  メールアドレス: {gmail_account.email_address}")
    print(f"  認証方式: {gmail_account.auth_type.value}")
    
    root = tk.Tk()
    root.withdraw()  # メインウィンドウを非表示
    
    def on_success(account):
        """成功時のコールバック"""
        print(f"\n✅ Gmail OAuth2設定が完了しました:")
        print(f"  名前: {account.name}")
        print(f"  メールアドレス: {account.email_address}")
        print(f"  OAuth2必要: {account.requires_oauth2()}")
        print(f"  必要スコープ: {len(account.get_oauth2_scope_requirements())}個")
        
        messagebox.showinfo("成功", f"Gmail「{account.name}」の設定が完了しました")
    
    try:
        print("Gmail OAuth2設定ダイアログを開きます...")
        print("※ 実際のOAuth2認証には client_secret.json が必要です")
        result = show_account_dialog(root, account=gmail_account, success_callback=on_success)
        
        if result:
            print("✅ Gmail OAuth2設定が完了しました")
        else:
            print("❌ Gmail OAuth2設定がキャンセルされました")
            
    except Exception as e:
        print(f"❌ エラー: {e}")
    finally:
        root.destroy()


def demo_dialog_features():
    """
    ダイアログ機能のデモ
    """
    print("\n" + "="*60)
    print("🎯 アカウント設定ダイアログ機能デモ")
    print("="*60)
    
    print("🔧 実装済み機能:")
    print("• Gmail OAuth2認証設定")
    print("• IMAP/SMTP手動設定")
    print("• POP3設定")
    print("• 接続テスト機能")
    print("• アカウント編集機能")
    print("• 侘び寂びデザイン")
    print("• 入力検証")
    print("• プリセット設定自動適用")
    
    print("\n📧 対応アカウントタイプ:")
    print("• Gmail (OAuth2)")
    print("• IMAP (手動設定)")
    print("• POP3 (手動設定)")
    
    print("\n🔐 認証方式:")
    print("• OAuth2認証 (Gmail)")
    print("• パスワード認証")
    print("• アプリパスワード")
    
    print("\n⚙️ 設定機能:")
    print("• 受信サーバー設定 (IMAP/POP3)")
    print("• 送信サーバー設定 (SMTP)")
    print("• 暗号化設定 (SSL/STARTTLS)")
    print("• ポート設定")
    print("• メール署名")
    print("• 同期設定")
    print("• デフォルトアカウント設定")
    
    print("\n🎨 UI特徴:")
    print("• 侘び寂びの美学に基づいたデザイン")
    print("• タブ切り替えによる設定分類")
    print("• リアルタイム入力検証")
    print("• 接続テスト機能")
    print("• ヘルプメッセージ表示")


def main():
    """
    メイン関数
    """
    # ログを設定
    logger = setup_logger()
    logger.info("🔐 WabiMail アカウント設定ダイアログデモを開始します")
    
    try:
        print("🌸 WabiMail アカウント設定ダイアログデモ")
        print("="*60)
        print("G005 アカウント追加・編集画面の機能確認")
        print("侘び寂びの美学に基づいた統合アカウント設定")
        
        # 機能紹介
        demo_dialog_features()
        
        # インタラクティブなデモメニュー
        while True:
            print("\n" + "="*60)
            print("📋 デモメニュー")
            print("="*60)
            print("1. 新規アカウント作成デモ")
            print("2. アカウント編集デモ")
            print("3. Gmail OAuth2設定デモ")
            print("4. 機能説明の再表示")
            print("0. 終了")
            
            try:
                choice = input("\n選択してください (0-4): ").strip()
                
                if choice == "1":
                    demo_new_account()
                elif choice == "2":
                    demo_edit_account()
                elif choice == "3":
                    demo_gmail_oauth2()
                elif choice == "4":
                    demo_dialog_features()
                elif choice == "0":
                    print("\n🌸 デモを終了します。ありがとうございました。")
                    break
                else:
                    print("❌ 無効な選択です。0-4の数字を入力してください。")
                    
            except KeyboardInterrupt:
                print("\n\n🌸 デモを終了します。")
                break
            except Exception as e:
                print(f"❌ エラー: {e}")
        
        print("\n🔐 アカウント設定ダイアログデモ完了！")
        print("="*60)
        
    except Exception as e:
        logger.error(f"デモ実行中にエラーが発生しました: {e}")
        print(f"❌ エラー: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()