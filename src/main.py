#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WabiMail - 侘び寂びメールクライアント
メインエントリーポイント

このファイルはWabiMailアプリケーションの起動点です。
アプリケーションの初期化とメインウィンドウの表示を行います。

Author: WabiMail Development Team
Created: 2025-07-01
"""

import sys
import os
import logging
from pathlib import Path

# プロジェクトルートをPythonパスに追加
# これにより、src/ディレクトリ内のモジュールを相対インポートできます
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.logger import setup_logger
from src.config.app_config import AppConfig


def main():
    """
    メインエントリーポイント
    
    WabiMailアプリケーションを起動します。
    以下の順序で初期化を行います：
    1. ログ設定
    2. アプリケーション設定読み込み
    3. メインウィンドウ起動
    """
    try:
        # ログ設定を初期化
        # 開発時はDEBUGレベル、リリース時はINFOレベルに設定
        logger = setup_logger()
        logger.info("WabiMail アプリケーションを開始します")
        
        # アプリケーション設定を読み込み
        # 初回起動時は設定ファイルが作成されます
        config = AppConfig()
        logger.info("設定ファイルを読み込みました")
        
        # メインウィンドウを起動
        logger.info("メインウィンドウを起動中...")
        
        from src.ui.main_window import WabiMailMainWindow
        
        # GUIアプリケーションを起動
        app = WabiMailMainWindow()
        
        logger.info("WabiMail GUI が正常に起動しました")
        
        # メインループを開始
        app.run()
        
    except Exception as e:
        # エラーが発生した場合の処理
        error_msg = f"アプリケーション起動中にエラーが発生しました: {e}"
        if 'logger' in locals():
            logger.error(error_msg)
        else:
            print(f"ERROR: {error_msg}")
        sys.exit(1)


if __name__ == "__main__":
    """
    スクリプトとして直接実行された場合のエントリーポイント
    
    python main.py または python src/main.py で実行されます
    """
    main()