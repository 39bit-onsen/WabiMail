# -*- coding: utf-8 -*-
"""
PyInstaller ランタイムフック
実行時の環境設定を行います
"""

import os
import sys

# SSL証明書の設定（requests用）
if hasattr(sys, '_MEIPASS'):
    import certifi
    os.environ['SSL_CERT_FILE'] = certifi.where()
    os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()

# Tkinterの設定
if sys.platform == "darwin":
    # macOSでのTkinter設定
    os.environ['TK_SILENCE_DEPRECATION'] = '1'
