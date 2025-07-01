# -*- coding: utf-8 -*-
"""
ログ設定モジュール

WabiMail全体で使用するログ設定を管理します。
開発環境とプロダクション環境で適切なログレベルを設定します。

Author: WabiMail Development Team
Created: 2025-07-01
"""

import logging
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler
import colorama
from colorama import Fore, Style

# Coloramaを初期化（Windows対応）
colorama.init()


class ColoredFormatter(logging.Formatter):
    """
    カラー付きログフォーマッター
    
    ログレベルに応じて色付きでログを出力します。
    開発時の視認性向上のために使用します。
    """
    
    # ログレベル別の色設定
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.MAGENTA + Style.BRIGHT
    }
    
    def format(self, record):
        """
        ログレコードをカラー付きでフォーマットします
        
        Args:
            record: ログレコード
            
        Returns:
            str: フォーマット済みログメッセージ
        """
        # 元のフォーマッターでメッセージを作成
        log_message = super().format(record)
        
        # ログレベルに応じた色を適用
        color = self.COLORS.get(record.levelname, '')
        if color:
            log_message = f"{color}{log_message}{Style.RESET_ALL}"
            
        return log_message


def setup_logger(name="WabiMail", level=logging.INFO):
    """
    WabiMail用のログ設定を行います
    
    Args:
        name (str): ロガー名（デフォルト: "WabiMail"）
        level: ログレベル（デフォルト: INFO）
        
    Returns:
        logging.Logger: 設定済みロガーインスタンス
        
    Note:
        - コンソール出力: カラー付きフォーマット
        - ファイル出力: ローテーション付きログファイル
        - 開発時はDEBUGレベル、本番はINFOレベルを推奨
    """
    
    # ロガーを作成
    logger = logging.getLogger(name)
    
    # 既に設定済みの場合はそのまま返す
    if logger.handlers:
        return logger
        
    # ログレベルを設定
    logger.setLevel(level)
    
    # ログフォーマットを定義
    console_format = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    file_format = "%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s"
    
    # コンソールハンドラー（カラー付き）
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_formatter = ColoredFormatter(console_format, datefmt="%H:%M:%S")
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # ファイルハンドラー（ローテーション付き）
    # ログディレクトリを作成
    log_dir = Path.cwd() / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # ログファイルパス
    log_file = log_dir / "wabimail.log"
    
    # ローテーションファイルハンドラー
    # 最大5MB、最大5ファイルまでローテーション
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=5*1024*1024,  # 5MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)  # ファイルには詳細ログを記録
    file_formatter = logging.Formatter(file_format, datefmt="%Y-%m-%d %H:%M:%S")
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # 初期化完了ログ
    logger.debug(f"ログシステムを初期化しました (レベル: {logging.getLevelName(level)})")
    logger.debug(f"ログファイル: {log_file}")
    
    return logger


def get_logger(name=None):
    """
    既存のロガーを取得します
    
    Args:
        name (str): ロガー名（None の場合は "WabiMail"）
        
    Returns:
        logging.Logger: ロガーインスタンス
        
    Note:
        setup_logger() を事前に呼び出している必要があります
    """
    if name is None:
        name = "WabiMail"
    return logging.getLogger(name)