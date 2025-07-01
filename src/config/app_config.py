# -*- coding: utf-8 -*-
"""
アプリケーション設定管理モジュール

WabiMailの基本設定を管理します。
設定ファイルの読み書き、デフォルト値の管理等を行います。

Author: WabiMail Development Team
Created: 2025-07-01
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
import yaml
from src.utils.logger import get_logger

# ロガーを取得
logger = get_logger(__name__)


class AppConfig:
    """
    アプリケーション設定管理クラス
    
    WabiMailの基本設定を管理します。
    設定ファイルの自動生成、読み込み、保存機能を提供します。
    
    Attributes:
        config_dir (Path): 設定ディレクトリパス
        config_file (Path): 設定ファイルパス
        _config (Dict): 設定データ
    """
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        AppConfigを初期化します
        
        Args:
            config_dir (str, optional): 設定ディレクトリパス
                                      Noneの場合はデフォルト位置を使用
        """
        # 設定ディレクトリを決定
        if config_dir:
            self.config_dir = Path(config_dir)
        else:
            # ユーザーのホームディレクトリにWabiMail設定フォルダを作成
            self.config_dir = Path.home() / ".wabimail"
            
        # 設定ディレクトリを作成（存在しない場合）
        self.config_dir.mkdir(exist_ok=True)
        
        # 設定ファイルパス
        self.config_file = self.config_dir / "config.yaml"
        
        # 設定データを初期化
        self._config = {}
        
        # 設定を読み込み
        self.load_config()
        
        logger.info(f"アプリケーション設定を初期化しました: {self.config_file}")
    
    def get_default_config(self) -> Dict[str, Any]:
        """
        デフォルト設定を返します
        
        Returns:
            Dict[str, Any]: デフォルト設定辞書
        """
        return {
            # アプリケーション基本設定
            "app": {
                "version": "0.1.0",
                "first_run": True,
                "language": "ja",  # 日本語がデフォルト
                "theme": "wabi_sabi_light",
                "window": {
                    "width": 1200,
                    "height": 800,
                    "maximized": False,
                    "x": 100,
                    "y": 100
                }
            },
            
            # UI設定
            "ui": {
                "font": {
                    "family": "Meiryo",  # 日本語フォント
                    "size": 10
                },
                "colors": {
                    "background": "#FEFEFE",  # 侘び寂びの白
                    "text": "#333333",
                    "accent": "#E6E6E6"
                },
                "layout": {
                    "left_pane_width": 250,
                    "center_pane_width": 400,
                    "show_preview": True
                }
            },
            
            # メール設定
            "mail": {
                "check_interval": 300,  # 5分間隔
                "auto_check": True,
                "notifications": {
                    "enabled": True,
                    "sound": False  # 静かな体験
                }
            },
            
            # セキュリティ設定
            "security": {
                "auto_lock": False,
                "remember_passwords": True,
                "encryption_enabled": True
            },
            
            # ログ設定
            "logging": {
                "level": "INFO",
                "file_enabled": True,
                "console_enabled": True
            }
        }
    
    def load_config(self):
        """
        設定ファイルから設定を読み込みます
        
        ファイルが存在しない場合はデフォルト設定を使用して新規作成します。
        """
        try:
            if self.config_file.exists():
                # 既存の設定ファイルを読み込み
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self._config = yaml.safe_load(f) or {}
                logger.debug(f"設定ファイルを読み込みました: {self.config_file}")
            else:
                # 設定ファイルが存在しない場合はデフォルト設定を使用
                logger.info("設定ファイルが見つかりません。デフォルト設定を作成します。")
                self._config = self.get_default_config()
                self.save_config()
                
        except Exception as e:
            logger.error(f"設定ファイル読み込みエラー: {e}")
            logger.info("デフォルト設定を使用します")
            self._config = self.get_default_config()
    
    def save_config(self):
        """
        現在の設定をファイルに保存します
        
        Raises:
            Exception: ファイル保存に失敗した場合
        """
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(
                    self._config, 
                    f, 
                    default_flow_style=False,
                    allow_unicode=True,
                    indent=2
                )
            logger.debug(f"設定ファイルを保存しました: {self.config_file}")
            
        except Exception as e:
            logger.error(f"設定ファイル保存エラー: {e}")
            raise
    
    def get(self, key_path: str, default=None):
        """
        ドット記法で設定値を取得します
        
        Args:
            key_path (str): 設定キーパス（例: "ui.font.size"）
            default: デフォルト値
            
        Returns:
            設定値またはデフォルト値
            
        Example:
            >>> config.get("ui.font.size", 12)
            10
        """
        keys = key_path.split('.')
        value = self._config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            logger.debug(f"設定キー '{key_path}' が見つかりません。デフォルト値を返します: {default}")
            return default
    
    def set(self, key_path: str, value):
        """
        ドット記法で設定値を変更します
        
        Args:
            key_path (str): 設定キーパス（例: "ui.font.size"）
            value: 設定する値
            
        Example:
            >>> config.set("ui.font.size", 12)
        """
        keys = key_path.split('.')
        current = self._config
        
        # 最後のキー以外は辞書を作成
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # 値を設定
        current[keys[-1]] = value
        logger.debug(f"設定を更新しました: {key_path} = {value}")
    
    def get_all(self) -> Dict[str, Any]:
        """
        全設定を取得します
        
        Returns:
            Dict[str, Any]: 全設定データ
        """
        return self._config.copy()
    
    def reset_to_default(self):
        """
        設定をデフォルト値にリセットします
        """
        logger.info("設定をデフォルト値にリセットします")
        self._config = self.get_default_config()
        self.save_config()
    
    def is_first_run(self) -> bool:
        """
        初回起動かどうかを確認します
        
        Returns:
            bool: 初回起動の場合True
        """
        return self.get("app.first_run", True)
    
    def mark_setup_complete(self):
        """
        初回セットアップ完了をマークします
        """
        self.set("app.first_run", False)
        self.save_config()
        logger.info("初回セットアップ完了をマークしました")