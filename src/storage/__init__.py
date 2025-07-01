# -*- coding: utf-8 -*-
"""
データストレージモジュール

WabiMailのデータ永続化機能を提供します。
暗号化による安全なデータ保存と統合的なストレージ管理を実現します。

Author: WabiMail Development Team
Created: 2025-07-01
"""

from .secure_storage import SecureStorage
from .account_storage import AccountStorage
from .mail_storage import MailStorage

__all__ = [
    'SecureStorage',
    'AccountStorage', 
    'MailStorage'
]