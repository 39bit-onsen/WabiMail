# -*- coding: utf-8 -*-
"""
メールストレージモジュール

WabiMailのメールデータ専用ストレージシステムです。
受信メールのローカルキャッシュ、検索、オフライン閲覧機能を提供します。

Author: WabiMail Development Team
Created: 2025-07-01
"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
import uuid
import json

from src.mail.mail_message import MailMessage, MessageFlag, MailAttachment
from src.storage.secure_storage import SecureStorage
from src.utils.logger import get_logger

# ロガーを取得
logger = get_logger(__name__)


class MailStorage:
    """
    メールストレージクラス
    
    WabiMailのメールデータをローカルにキャッシュ・管理します。
    オフライン閲覧、高速検索、メール同期機能を提供します。
    
    Attributes:
        _storage (SecureStorage): 基盤ストレージシステム
        _max_cache_days (int): キャッシュ保持期間（日数）
    """
    
    def __init__(self, storage_dir: Optional[str] = None, max_cache_days: int = 30):
        """
        メールストレージを初期化
        
        Args:
            storage_dir: カスタムストレージディレクトリ（テスト用）
            max_cache_days: キャッシュ保持期間（日数）
        """
        self._storage = SecureStorage(storage_dir)
        self._max_cache_days = max_cache_days
        logger.info(f"メールストレージを初期化しました（キャッシュ保持期間: {max_cache_days}日）")
    
    def cache_message(self, account_id: str, folder: str, message: MailMessage) -> bool:
        """
        メッセージをローカルキャッシュに保存
        
        Args:
            account_id: アカウントID
            folder: フォルダ名
            message: MailMessageオブジェクト
            
        Returns:
            bool: キャッシュ成功可否
        """
        try:
            # メッセージデータを辞書に変換
            message_data = self._message_to_dict(message)
            
            # 暗号化してデータベースに保存
            cursor = self._storage._conn.cursor()
            
            # UIDが存在するかチェック
            message_uid = getattr(message, 'uid', None)
            if not message_uid:
                message_uid = str(uuid.uuid4())
            
            cursor.execute("""
                INSERT OR REPLACE INTO mail_cache 
                (id, account_id, folder, uid, encrypted_message, flags, date_received, cached_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                f"{account_id}_{folder}_{message_uid}",
                account_id,
                folder,
                message_uid,
                self._storage.encrypt_data(message_data),
                json.dumps([flag.value for flag in message.flags]),
                message.date_received,
                datetime.now()
            ))
            
            self._storage._conn.commit()
            logger.debug(f"メッセージをキャッシュしました: {message.subject}")
            return True
            
        except Exception as e:
            logger.error(f"メッセージキャッシュエラー: {e}")
            return False
    
    def load_cached_message(self, account_id: str, folder: str, uid: str) -> Optional[MailMessage]:
        """
        キャッシュからメッセージを読み込み
        
        Args:
            account_id: アカウントID
            folder: フォルダ名
            uid: メッセージUID
            
        Returns:
            Optional[MailMessage]: メッセージオブジェクト
        """
        try:
            cursor = self._storage._conn.cursor()
            cursor.execute("""
                SELECT encrypted_message, flags FROM mail_cache 
                WHERE account_id = ? AND folder = ? AND uid = ?
            """, (account_id, folder, uid))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            # 暗号化データを復号
            message_data = self._storage.decrypt_data(row['encrypted_message'])
            
            # MailMessage オブジェクトに変換
            message = self._dict_to_message(message_data)
            
            # フラグを復元
            if row['flags']:
                flags_data = json.loads(row['flags'])
                message.flags = [MessageFlag(flag) for flag in flags_data]
            
            return message
            
        except Exception as e:
            logger.error(f"キャッシュメッセージ読み込みエラー: {e}")
            return None
    
    def list_cached_messages(self, account_id: str, folder: str, 
                           limit: Optional[int] = None, 
                           offset: int = 0) -> List[Dict[str, Any]]:
        """
        フォルダ内のキャッシュメッセージ一覧を取得
        
        Args:
            account_id: アカウントID
            folder: フォルダ名
            limit: 取得件数制限
            offset: オフセット
            
        Returns:
            List[Dict]: メッセージ情報リスト
        """
        try:
            cursor = self._storage._conn.cursor()
            
            sql = """
                SELECT uid, flags, date_received, cached_at
                FROM mail_cache 
                WHERE account_id = ? AND folder = ?
                ORDER BY date_received DESC
            """
            
            params = [account_id, folder]
            
            if limit:
                sql += " LIMIT ? OFFSET ?"
                params.extend([limit, offset])
            
            cursor.execute(sql, params)
            
            messages = []
            for row in cursor.fetchall():
                messages.append({
                    'uid': row['uid'],
                    'flags': json.loads(row['flags']) if row['flags'] else [],
                    'date_received': row['date_received'],
                    'cached_at': row['cached_at']
                })
            
            return messages
            
        except Exception as e:
            logger.error(f"キャッシュメッセージ一覧取得エラー: {e}")
            return []
    
    def search_cached_messages(self, account_id: str, 
                             query: str, 
                             folder: Optional[str] = None,
                             limit: int = 100) -> List[MailMessage]:
        """
        キャッシュ内でメッセージを検索
        
        Args:
            account_id: アカウントID
            query: 検索クエリ
            folder: 検索対象フォルダ（Noneで全フォルダ）
            limit: 取得件数制限
            
        Returns:
            List[MailMessage]: 検索結果メッセージリスト
        """
        try:
            cursor = self._storage._conn.cursor()
            
            # 基本的なSQL（実際のアプリケーションではFTSを使用することを推奨）
            sql = """
                SELECT account_id, folder, uid, encrypted_message, flags 
                FROM mail_cache 
                WHERE account_id = ?
            """
            params = [account_id]
            
            if folder:
                sql += " AND folder = ?"
                params.append(folder)
            
            sql += " ORDER BY date_received DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(sql, params)
            
            messages = []
            for row in cursor.fetchall():
                try:
                    # メッセージを復号
                    message_data = self._storage.decrypt_data(row['encrypted_message'])
                    
                    # 検索クエリにマッチするかチェック
                    if self._message_matches_query(message_data, query):
                        message = self._dict_to_message(message_data)
                        
                        # フラグを復元
                        if row['flags']:
                            flags_data = json.loads(row['flags'])
                            message.flags = [MessageFlag(flag) for flag in flags_data]
                        
                        messages.append(message)
                        
                except Exception as e:
                    logger.warning(f"メッセージ処理スキップ: {e}")
                    continue
            
            logger.info(f"検索結果: {len(messages)}件のメッセージが見つかりました")
            return messages
            
        except Exception as e:
            logger.error(f"メッセージ検索エラー: {e}")
            return []
    
    def delete_cached_message(self, account_id: str, folder: str, uid: str) -> bool:
        """
        キャッシュからメッセージを削除
        
        Args:
            account_id: アカウントID
            folder: フォルダ名
            uid: メッセージUID
            
        Returns:
            bool: 削除成功可否
        """
        try:
            cursor = self._storage._conn.cursor()
            cursor.execute("""
                DELETE FROM mail_cache 
                WHERE account_id = ? AND folder = ? AND uid = ?
            """, (account_id, folder, uid))
            
            self._storage._conn.commit()
            
            if cursor.rowcount > 0:
                logger.debug(f"キャッシュメッセージを削除しました: {uid}")
                return True
            else:
                logger.warning(f"削除対象のメッセージが見つかりません: {uid}")
                return False
                
        except Exception as e:
            logger.error(f"メッセージ削除エラー: {e}")
            return False
    
    def delete_folder_cache(self, account_id: str, folder: str) -> bool:
        """
        フォルダのキャッシュを全削除
        
        Args:
            account_id: アカウントID
            folder: フォルダ名
            
        Returns:
            bool: 削除成功可否
        """
        try:
            cursor = self._storage._conn.cursor()
            cursor.execute("""
                DELETE FROM mail_cache 
                WHERE account_id = ? AND folder = ?
            """, (account_id, folder))
            
            self._storage._conn.commit()
            
            deleted_count = cursor.rowcount
            logger.info(f"フォルダキャッシュを削除しました: {folder} ({deleted_count}件)")
            return True
            
        except Exception as e:
            logger.error(f"フォルダキャッシュ削除エラー: {e}")
            return False
    
    def delete_account_cache(self, account_id: str) -> bool:
        """
        アカウントのキャッシュを全削除
        
        Args:
            account_id: アカウントID
            
        Returns:
            bool: 削除成功可否
        """
        try:
            cursor = self._storage._conn.cursor()
            cursor.execute("""
                DELETE FROM mail_cache WHERE account_id = ?
            """, (account_id,))
            
            self._storage._conn.commit()
            
            deleted_count = cursor.rowcount
            logger.info(f"アカウントキャッシュを削除しました: {account_id} ({deleted_count}件)")
            return True
            
        except Exception as e:
            logger.error(f"アカウントキャッシュ削除エラー: {e}")
            return False
    
    def cleanup_old_cache(self) -> int:
        """
        古いキャッシュを削除
        
        Returns:
            int: 削除したメッセージ数
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=self._max_cache_days)
            
            cursor = self._storage._conn.cursor()
            cursor.execute("""
                DELETE FROM mail_cache 
                WHERE cached_at < ?
            """, (cutoff_date,))
            
            self._storage._conn.commit()
            
            deleted_count = cursor.rowcount
            if deleted_count > 0:
                logger.info(f"古いキャッシュを削除しました: {deleted_count}件")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"キャッシュクリーンアップエラー: {e}")
            return 0
    
    def get_cache_stats(self, account_id: Optional[str] = None) -> Dict[str, Any]:
        """
        キャッシュ統計情報を取得
        
        Args:
            account_id: 特定のアカウントID（Noneで全体統計）
            
        Returns:
            Dict[str, Any]: 統計情報
        """
        try:
            cursor = self._storage._conn.cursor()
            
            if account_id:
                # 特定アカウントの統計
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_messages,
                        COUNT(DISTINCT folder) as folder_count,
                        MIN(cached_at) as oldest_cache,
                        MAX(cached_at) as newest_cache
                    FROM mail_cache 
                    WHERE account_id = ?
                """, (account_id,))
                
                row = cursor.fetchone()
                stats = {
                    'account_id': account_id,
                    'total_messages': row['total_messages'],
                    'folder_count': row['folder_count'],
                    'oldest_cache': row['oldest_cache'],
                    'newest_cache': row['newest_cache']
                }
                
                # フォルダ別統計
                cursor.execute("""
                    SELECT folder, COUNT(*) as message_count
                    FROM mail_cache 
                    WHERE account_id = ?
                    GROUP BY folder
                    ORDER BY message_count DESC
                """, (account_id,))
                
                stats['folders'] = [
                    {'folder': row['folder'], 'message_count': row['message_count']}
                    for row in cursor.fetchall()
                ]
                
            else:
                # 全体統計
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_messages,
                        COUNT(DISTINCT account_id) as account_count,
                        COUNT(DISTINCT account_id || folder) as total_folders,
                        MIN(cached_at) as oldest_cache,
                        MAX(cached_at) as newest_cache
                    FROM mail_cache
                """)
                
                row = cursor.fetchone()
                stats = {
                    'total_messages': row['total_messages'],
                    'account_count': row['account_count'],
                    'total_folders': row['total_folders'],
                    'oldest_cache': row['oldest_cache'],
                    'newest_cache': row['newest_cache']
                }
                
                # アカウント別統計
                cursor.execute("""
                    SELECT account_id, COUNT(*) as message_count
                    FROM mail_cache 
                    GROUP BY account_id
                    ORDER BY message_count DESC
                """)
                
                stats['accounts'] = [
                    {'account_id': row['account_id'], 'message_count': row['message_count']}
                    for row in cursor.fetchall()
                ]
            
            return stats
            
        except Exception as e:
            logger.error(f"キャッシュ統計取得エラー: {e}")
            return {}
    
    def _message_to_dict(self, message: MailMessage) -> Dict[str, Any]:
        """
        MailMessage オブジェクトを辞書に変換
        
        Args:
            message: MailMessageオブジェクト
            
        Returns:
            Dict[str, Any]: メッセージデータ辞書
        """
        # 添付ファイルを辞書に変換
        attachments = []
        for attachment in message.attachments:
            attachments.append({
                'filename': attachment.filename,
                'content_type': attachment.content_type,
                'size': attachment.size,
                'data': attachment.data.hex() if attachment.data else None  # バイナリを16進文字列に
            })
        
        return {
            'subject': message.subject,
            'sender': message.sender,
            'recipients': message.recipients,
            'cc': getattr(message, 'cc', []),
            'bcc': getattr(message, 'bcc', []),
            'body_text': message.body_text,
            'body_html': getattr(message, 'body_html', ''),
            'date_received': message.date_received.isoformat() if message.date_received else None,
            'message_id': getattr(message, 'message_id', ''),
            'in_reply_to': getattr(message, 'in_reply_to', ''),
            'references': getattr(message, 'references', []),
            'attachments': attachments,
            'size': getattr(message, 'size', 0),
            'uid': getattr(message, 'uid', '')
        }
    
    def _dict_to_message(self, message_data: Dict[str, Any]) -> MailMessage:
        """
        辞書から MailMessage オブジェクトに変換
        
        Args:
            message_data: メッセージデータ辞書
            
        Returns:
            MailMessage: MailMessageオブジェクト
        """
        # 添付ファイルを復元
        attachments = []
        for attachment_data in message_data.get('attachments', []):
            attachment = MailAttachment(
                filename=attachment_data['filename'],
                content_type=attachment_data['content_type'],
                size=attachment_data['size']
            )
            # バイナリデータを復元
            if attachment_data['data']:
                attachment.data = bytes.fromhex(attachment_data['data'])
            attachments.append(attachment)
        
        # 日付を復元
        date_received = None
        if message_data.get('date_received'):
            date_received = datetime.fromisoformat(message_data['date_received'])
        
        # MailMessage オブジェクトを作成
        message = MailMessage(
            subject=message_data.get('subject', ''),
            sender=message_data.get('sender', ''),
            recipients=message_data.get('recipients', []),
            body_text=message_data.get('body_text', ''),
            date_received=date_received,
            attachments=attachments
        )
        
        # 追加属性を設定
        message.cc = message_data.get('cc', [])
        message.bcc = message_data.get('bcc', [])
        message.body_html = message_data.get('body_html', '')
        message.message_id = message_data.get('message_id', '')
        message.in_reply_to = message_data.get('in_reply_to', '')
        message.references = message_data.get('references', [])
        message.size = message_data.get('size', 0)
        message.uid = message_data.get('uid', '')
        
        return message
    
    def _message_matches_query(self, message_data: Dict[str, Any], query: str) -> bool:
        """
        メッセージが検索クエリにマッチするかチェック
        
        Args:
            message_data: メッセージデータ辞書
            query: 検索クエリ
            
        Returns:
            bool: マッチ結果
        """
        query_lower = query.lower()
        
        # 件名、送信者、本文で検索
        searchable_fields = [
            message_data.get('subject', ''),
            message_data.get('sender', ''),
            message_data.get('body_text', ''),
            message_data.get('body_html', '')
        ]
        
        # 受信者も検索対象に追加
        for recipient in message_data.get('recipients', []):
            searchable_fields.append(recipient)
        
        # いずれかのフィールドにクエリが含まれているかチェック
        for field in searchable_fields:
            if query_lower in field.lower():
                return True
        
        return False
    
    def close(self):
        """
        ストレージ接続を閉じる
        """
        if self._storage:
            self._storage.close()
    
    def __enter__(self):
        """コンテキストマネージャー開始"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """コンテキストマネージャー終了"""
        self.close()