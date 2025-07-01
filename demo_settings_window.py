#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
設定画面デモアプリケーション

Task 10: 設定画面の動作確認用デモアプリケーション
- 設定画面の表示・操作確認
- 各種設定項目の動作確認
- テーマ切り替え機能の確認
"""

import sys
import os
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.config.app_config import AppConfig
from src.ui.settings_window import show_settings_window


class SettingsWindowDemo:
    """設定画面デモクラス"""
    
    def __init__(self):
        """デモアプリケーションを初期化"""
        self.root = tk.Tk()
        self.root.title("🌸 WabiMail 設定画面デモ")
        self.root.geometry("500x400")
        
        # テスト用設定ディレクトリ
        demo_config_dir = Path.home() / ".wabimail_demo"
        demo_config_dir.mkdir(exist_ok=True)
        
        # デモ用設定
        self.config = AppConfig(str(demo_config_dir))
        
        # UI作成
        self._create_ui()
        
        print("🌸 WabiMail 設定画面デモ")
        print("="*50)
        print("🛠️ デモ内容:")
        print("• 設定画面の表示")
        print("• 一般設定の変更")
        print("• 外観設定の変更")
        print("• メール設定の変更")
        print("• セキュリティ設定の変更")
        print("• 侘び寂び設定の変更")
        print("• 設定のインポート・エクスポート")
        print()
        print("✨ 各ボタンをクリックして機能をお試しください")
    
    def _create_ui(self):
        """デモUI作成"""
        # メインタイトル
        title_label = tk.Label(
            self.root,
            text="🌸 WabiMail 設定画面デモ",
            font=("Yu Gothic UI", 16, "bold"),
            pady=20
        )
        title_label.pack()
        
        # 説明文
        desc_text = """侘び寂びの美学に基づいた設定画面をお試しください。
シンプルで美しい設定インターフェースを実現しています。"""
        
        desc_label = tk.Label(
            self.root,
            text=desc_text,
            font=("Yu Gothic UI", 10),
            justify=tk.CENTER,
            pady=10
        )
        desc_label.pack()
        
        # 現在の設定情報
        current_frame = tk.LabelFrame(
            self.root,
            text="📋 現在の設定",
            font=("Yu Gothic UI", 12),
            pady=10
        )
        current_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.current_info_label = tk.Label(
            current_frame,
            text=self._get_current_settings_info(),
            font=("Yu Gothic UI", 9),
            justify=tk.LEFT
        )
        self.current_info_label.pack(padx=10, pady=5)
        
        # デモボタン
        demo_frame = tk.LabelFrame(
            self.root,
            text="🔧 設定画面デモ",
            font=("Yu Gothic UI", 12),
            pady=10
        )
        demo_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # 設定画面を開くボタン
        open_button = tk.Button(
            demo_frame,
            text="🛠️ 設定画面を開く",
            font=("Yu Gothic UI", 12, "bold"),
            command=self._demo_open_settings,
            bg="#8b7355",
            fg="white",
            relief=tk.FLAT,
            pady=8
        )
        open_button.pack(fill=tk.X, padx=10, pady=10)
        
        # サンプル設定変更ボタン
        sample_button = tk.Button(
            demo_frame,
            text="🎨 サンプル設定を適用",
            font=("Yu Gothic UI", 11),
            command=self._demo_apply_sample_settings,
            bg="#f8f8f8",
            relief=tk.FLAT,
            pady=5
        )
        sample_button.pack(fill=tk.X, padx=10, pady=5)
        
        # 設定リセットボタン
        reset_button = tk.Button(
            demo_frame,
            text="🔄 設定をリセット",
            font=("Yu Gothic UI", 11),
            command=self._demo_reset_settings,
            bg="#f8f8f8",
            relief=tk.FLAT,
            pady=5
        )
        reset_button.pack(fill=tk.X, padx=10, pady=5)
        
        # 設定情報更新ボタン
        refresh_button = tk.Button(
            demo_frame,
            text="🔄 設定情報を更新",
            font=("Yu Gothic UI", 10),
            command=self._refresh_current_info,
            bg="#e8e8e8",
            relief=tk.FLAT,
            pady=3
        )
        refresh_button.pack(fill=tk.X, padx=10, pady=5)
        
        # 終了ボタン
        quit_button = tk.Button(
            self.root,
            text="❌ デモ終了",
            font=("Yu Gothic UI", 10),
            command=self.root.quit,
            bg="#ffe0e0",
            relief=tk.FLAT,
            pady=3
        )
        quit_button.pack(pady=10)
    
    def _get_current_settings_info(self):
        """現在の設定情報を取得"""
        info = f"""言語: {self.config.get('app.language', 'ja')}
テーマ: {self.config.get('app.theme', 'wabi_sabi_light')}
フォントサイズ: {self.config.get('ui.font.size', 10)}
フォントファミリー: {self.config.get('ui.font.family', 'Meiryo')}
背景色: {self.config.get('ui.colors.background', '#FEFEFE')}
メールチェック間隔: {self.config.get('mail.check_interval', 300)}秒
自動チェック: {'有効' if self.config.get('mail.auto_check', True) else '無効'}
通知: {'有効' if self.config.get('mail.notifications.enabled', True) else '無効'}
暗号化: {'有効' if self.config.get('security.encryption_enabled', True) else '無効'}"""
        return info
    
    def _refresh_current_info(self):
        """設定情報表示を更新"""
        self.current_info_label.config(text=self._get_current_settings_info())
        print("🔄 設定情報を更新しました")
    
    def _demo_open_settings(self):
        """設定画面を開くデモ"""
        print("🛠️ 設定画面を開きます...")
        
        def on_settings_changed(changed_settings):
            """設定変更時のコールバック"""
            print(f"⚙️ 設定が変更されました: {list(changed_settings.keys())}")
            messagebox.showinfo(
                "設定変更完了",
                f"以下の設定が変更されました:\n\n" + 
                "\n".join([f"• {key}" for key in changed_settings.keys()]),
                parent=self.root
            )
            # 表示を更新
            self._refresh_current_info()
        
        settings_window = show_settings_window(
            parent=self.root,
            config=self.config,
            on_settings_changed=on_settings_changed
        )
        
        if settings_window:
            print("✨ 設定画面を表示しました")
        else:
            print("❌ 設定画面の表示に失敗しました")
    
    def _demo_apply_sample_settings(self):
        """サンプル設定を適用"""
        print("🎨 サンプル設定を適用します...")
        
        try:
            # サンプル設定を適用
            sample_settings = {
                "app.language": "ja",
                "app.theme": "wabi_sabi_light",
                "ui.font.size": 12,
                "ui.font.family": "Yu Gothic UI",
                "ui.colors.background": "#F5F5F5",
                "ui.colors.text": "#2F2F2F",
                "mail.check_interval": 600,
                "mail.auto_check": True,
                "mail.notifications.enabled": True,
                "mail.notifications.sound": False,
                "security.encryption_enabled": True,
                "security.auto_lock": False
            }
            
            for key, value in sample_settings.items():
                self.config.set(key, value)
            
            self.config.save_config()
            self._refresh_current_info()
            
            messagebox.showinfo(
                "サンプル設定適用完了",
                "サンプル設定が正常に適用されました！\n\n"
                "設定画面を開いて確認してみてください。",
                parent=self.root
            )
            
            print("✅ サンプル設定を適用しました")
            
        except Exception as e:
            print(f"❌ サンプル設定適用エラー: {e}")
            messagebox.showerror("エラー", f"サンプル設定の適用に失敗しました:\n{e}")
    
    def _demo_reset_settings(self):
        """設定をリセット"""
        print("🔄 設定をリセットします...")
        
        result = messagebox.askyesno(
            "設定リセット確認",
            "設定をデフォルト値にリセットしますか？\n\n"
            "この操作は元に戻せません。",
            parent=self.root
        )
        
        if result:
            try:
                self.config.reset_to_default()
                self._refresh_current_info()
                
                messagebox.showinfo(
                    "設定リセット完了",
                    "設定が正常にリセットされました！",
                    parent=self.root
                )
                
                print("✅ 設定をリセットしました")
                
            except Exception as e:
                print(f"❌ 設定リセットエラー: {e}")
                messagebox.showerror("エラー", f"設定のリセットに失敗しました:\n{e}")
        else:
            print("🚫 設定リセットをキャンセルしました")
    
    def run(self):
        """デモアプリケーションを実行"""
        try:
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
        demo = SettingsWindowDemo()
        demo.run()
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()