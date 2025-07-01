# -*- coding: utf-8 -*-
"""
メールメッセージデータモデル

WabiMailで扱うメールメッセージの情報を管理します。
送受信したメールの構造化データとして使用されます。

Author: WabiMail Development Team
Created: 2025-07-01
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import email
import email.policy
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import uuid

from src.utils.logger import get_logger

# ロガーを取得
logger = get_logger(__name__)


class MessageFlag(Enum):
    """
    メールメッセージのフラグ列挙型
    
    IMAP標準のフラグとWabiMail独自フラグを定義します。
    """
    SEEN = "\\Seen"           # 既読
    ANSWERED = "\\Answered"   # 返信済み
    FLAGGED = "\\Flagged"     # 重要マーク
    DELETED = "\\Deleted"     # 削除マーク
    DRAFT = "\\Draft"         # 下書き
    RECENT = "\\Recent"       # 最近受信
    
    # WabiMail独自フラグ
    STARRED = "\\Starred"     # スター付き
    ARCHIVED = "\\Archived"   # アーカイブ済み


@dataclass
class MailAttachment:
    """
    メール添付ファイル情報クラス
    
    メールに添付されたファイルの情報を管理します。
    
    Attributes:
        filename (str): ファイル名
        content_type (str): MIMEタイプ
        size (int): ファイルサイズ（バイト）
        content_id (Optional[str]): インライン画像用のContent-ID
        data (Optional[bytes]): ファイルデータ（必要時のみ読み込み）
        is_inline (bool): インライン添付かどうか
    """
    filename: str = ""
    content_type: str = ""
    size: int = 0
    content_id: Optional[str] = None
    data: Optional[bytes] = None
    is_inline: bool = False
    
    def __str__(self) -> str:
        """
        添付ファイルの文字列表現
        
        Returns:
            str: ファイル情報の文字列
        """
        size_str = f"{self.size:,}バイト" if self.size > 0 else "サイズ不明"
        inline_str = " (インライン)" if self.is_inline else ""
        return f"{self.filename} ({self.content_type}, {size_str}){inline_str}"


@dataclass
class MailMessage:
    """
    メールメッセージクラス
    
    WabiMailで扱うメールメッセージの完全な情報を管理します。
    受信メール、送信メール、下書きすべてに対応します。
    
    Attributes:
        message_id (str): メッセージの一意識別子
        uid (Optional[str]): IMAPサーバー上のUID
        subject (str): 件名
        sender (str): 送信者（From）
        recipients (List[str]): 受信者リスト（To）
        cc_recipients (List[str]): CC受信者リスト
        bcc_recipients (List[str]): BCC受信者リスト
        reply_to (Optional[str]): 返信先アドレス
        date_sent (Optional[datetime]): 送信日時
        date_received (Optional[datetime]): 受信日時
        body_text (str): テキスト本文
        body_html (str): HTML本文
        attachments (List[MailAttachment]): 添付ファイルリスト
        flags (List[MessageFlag]): メッセージフラグ
        folder (str): 所属フォルダ
        account_id (str): 関連するアカウントID
        in_reply_to (Optional[str]): 返信元メッセージID
        references (List[str]): 参照メッセージIDリスト
        priority (str): 優先度（high/normal/low）
        raw_headers (Dict[str, str]): 生ヘッダー情報
    """
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    uid: Optional[str] = None
    subject: str = ""
    sender: str = ""
    recipients: List[str] = field(default_factory=list)
    cc_recipients: List[str] = field(default_factory=list)
    bcc_recipients: List[str] = field(default_factory=list)
    reply_to: Optional[str] = None
    date_sent: Optional[datetime] = None
    date_received: Optional[datetime] = None
    body_text: str = ""
    body_html: str = ""
    attachments: List[MailAttachment] = field(default_factory=list)
    flags: List[MessageFlag] = field(default_factory=list)
    folder: str = "INBOX"
    account_id: str = ""
    in_reply_to: Optional[str] = None
    references: List[str] = field(default_factory=list)
    priority: str = "normal"  # high, normal, low
    raw_headers: Dict[str, str] = field(default_factory=dict)
    
    def __post_init__(self):
        """
        初期化後の処理
        
        受信日時が設定されていない場合は現在時刻を設定します。
        """
        if self.date_received is None:
            self.date_received = datetime.now()
    
    @classmethod
    def from_email_message(cls, email_msg: email.message.EmailMessage, 
                          account_id: str = "", folder: str = "INBOX",
                          uid: Optional[str] = None) -> 'MailMessage':
        """
        email.message.EmailMessageからMailMessageを作成します
        
        Args:
            email_msg: Pythonのemail.messageオブジェクト
            account_id: 関連するアカウントID
            folder: メッセージが所属するフォルダ
            uid: IMAPサーバー上のUID
            
        Returns:
            MailMessage: 変換されたメールメッセージ
        """
        try:
            # 基本情報を抽出
            message = cls(
                uid=uid,
                subject=email_msg.get('Subject', ''),
                sender=email_msg.get('From', ''),
                folder=folder,
                account_id=account_id
            )
            
            # 受信者情報を解析
            to_header = email_msg.get('To', '')
            if to_header:
                message.recipients = [addr.strip() for addr in to_header.split(',')]
            
            cc_header = email_msg.get('Cc', '')
            if cc_header:
                message.cc_recipients = [addr.strip() for addr in cc_header.split(',')]
            
            # 返信先
            message.reply_to = email_msg.get('Reply-To')
            
            # 日時情報
            date_header = email_msg.get('Date')
            if date_header:
                try:
                    message.date_sent = email.utils.parsedate_to_datetime(date_header)
                except Exception as e:
                    logger.warning(f"日付解析エラー: {date_header}, {e}")
            
            # メッセージID関連
            message_id_header = email_msg.get('Message-ID')
            if message_id_header:
                message.message_id = message_id_header
            
            message.in_reply_to = email_msg.get('In-Reply-To')
            
            references_header = email_msg.get('References', '')
            if references_header:
                message.references = [ref.strip() for ref in references_header.split()]
            
            # 優先度
            priority_header = email_msg.get('X-Priority', '').lower()
            if priority_header in ['1', '2']:
                message.priority = 'high'
            elif priority_header in ['4', '5']:
                message.priority = 'low'
            else:
                message.priority = 'normal'
            
            # 本文を抽出
            message._extract_body_content(email_msg)
            
            # 添付ファイルを抽出
            message._extract_attachments(email_msg)
            
            # 生ヘッダーを保存
            for key, value in email_msg.items():
                message.raw_headers[key] = value
            
            logger.debug(f"メールメッセージを解析しました: {message.subject}")
            return message
            
        except Exception as e:
            logger.error(f"メール解析エラー: {e}")
            # エラーが発生しても基本的なメッセージオブジェクトは返す
            return cls(
                subject="[解析エラー]",
                sender="unknown",
                account_id=account_id,
                folder=folder,
                uid=uid
            )
    
    def _extract_body_content(self, email_msg: email.message.EmailMessage):
        """
        メール本文を抽出します
        
        Args:
            email_msg: Pythonのemail.messageオブジェクト
        """
        try:
            # テキスト本文を取得
            if email_msg.is_multipart():
                for part in email_msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = part.get('Content-Disposition', '')
                    
                    # 添付ファイルではない本文パートを処理
                    if 'attachment' not in content_disposition:
                        if content_type == 'text/plain' and not self.body_text:
                            self.body_text = part.get_content()
                        elif content_type == 'text/html' and not self.body_html:
                            self.body_html = part.get_content()
            else:
                # シンプルなメッセージの場合
                content_type = email_msg.get_content_type()
                if content_type == 'text/plain':
                    self.body_text = email_msg.get_content()
                elif content_type == 'text/html':
                    self.body_html = email_msg.get_content()
                    
        except Exception as e:
            logger.warning(f"本文抽出エラー: {e}")
            self.body_text = "[本文を読み込めませんでした]"
    
    def _extract_attachments(self, email_msg: email.message.EmailMessage):
        """
        添付ファイル情報を抽出します
        
        Args:
            email_msg: Pythonのemail.messageオブジェクト
        """
        try:
            if not email_msg.is_multipart():
                return
            
            for part in email_msg.walk():
                content_disposition = part.get('Content-Disposition', '')
                content_type = part.get_content_type()
                
                # 添付ファイルかインライン画像の場合
                if 'attachment' in content_disposition or 'inline' in content_disposition:
                    filename = part.get_filename()
                    if filename:
                        attachment = MailAttachment(
                            filename=filename,
                            content_type=content_type,
                            content_id=part.get('Content-ID'),
                            is_inline='inline' in content_disposition
                        )
                        
                        # ファイルサイズを推定（データが利用可能な場合）
                        try:
                            content = part.get_content()
                            if isinstance(content, bytes):
                                attachment.size = len(content)
                            elif isinstance(content, str):
                                attachment.size = len(content.encode('utf-8'))
                        except Exception:
                            attachment.size = 0
                        
                        self.attachments.append(attachment)
                        
        except Exception as e:
            logger.warning(f"添付ファイル抽出エラー: {e}")
    
    def has_flag(self, flag: MessageFlag) -> bool:
        """
        指定されたフラグが設定されているかチェックします
        
        Args:
            flag: チェックするフラグ
            
        Returns:
            bool: フラグが設定されている場合True
        """
        return flag in self.flags
    
    def add_flag(self, flag: MessageFlag):
        """
        フラグを追加します
        
        Args:
            flag: 追加するフラグ
        """
        if flag not in self.flags:
            self.flags.append(flag)
    
    def remove_flag(self, flag: MessageFlag):
        """
        フラグを削除します
        
        Args:
            flag: 削除するフラグ
        """
        if flag in self.flags:
            self.flags.remove(flag)
    
    def is_read(self) -> bool:
        """
        既読かどうかをチェックします
        
        Returns:
            bool: 既読の場合True
        """
        return self.has_flag(MessageFlag.SEEN)
    
    def mark_as_read(self):
        """
        既読マークを設定します
        """
        self.add_flag(MessageFlag.SEEN)
    
    def mark_as_unread(self):
        """
        未読マークを設定します
        """
        self.remove_flag(MessageFlag.SEEN)
    
    def is_flagged(self) -> bool:
        """
        重要マークが付いているかチェックします
        
        Returns:
            bool: 重要マークがある場合True
        """
        return self.has_flag(MessageFlag.FLAGGED)
    
    def get_display_date(self) -> datetime:
        """
        表示用の日時を取得します
        
        Returns:
            datetime: 送信日時、なければ受信日時
        """
        return self.date_sent or self.date_received or datetime.now()
    
    def get_body_preview(self, max_length: int = 100) -> str:
        """
        本文のプレビューテキストを取得します
        
        Args:
            max_length: 最大文字数
            
        Returns:
            str: プレビューテキスト
        """
        # テキスト本文を優先、なければHTMLから抽出
        body = self.body_text or self._extract_text_from_html(self.body_html)
        
        if not body:
            return "[本文なし]"
        
        # 改行を空白に置換し、連続空白を整理
        body = ' '.join(body.split())
        
        # 指定文字数で切り取り
        if len(body) > max_length:
            return body[:max_length] + "..."
        
        return body
    
    def _extract_text_from_html(self, html: str) -> str:
        """
        HTMLからテキストを抽出します（簡易版）
        
        Args:
            html: HTML文字列
            
        Returns:
            str: 抽出されたテキスト
        """
        if not html:
            return ""
        
        # 簡易的なHTMLタグ除去（本格的にはBeautifulSoupを使用）
        import re
        text = re.sub(r'<[^>]+>', '', html)
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&amp;', '&')
        
        return text.strip()
    
    def has_attachments(self) -> bool:
        """
        添付ファイルがあるかチェックします
        
        Returns:
            bool: 添付ファイルがある場合True
        """
        return len(self.attachments) > 0
    
    def get_attachment_count(self) -> int:
        """
        添付ファイル数を取得します
        
        Returns:
            int: 添付ファイル数
        """
        return len(self.attachments)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        メッセージ情報をディクショナリ形式に変換します
        
        Returns:
            Dict[str, Any]: メッセージ情報ディクショナリ
        """
        return {
            "message_id": self.message_id,
            "uid": self.uid,
            "subject": self.subject,
            "sender": self.sender,
            "recipients": self.recipients,
            "cc_recipients": self.cc_recipients,
            "date_sent": self.date_sent.isoformat() if self.date_sent else None,
            "date_received": self.date_received.isoformat() if self.date_received else None,
            "body_text": self.body_text,
            "body_html": self.body_html,
            "attachments": [
                {
                    "filename": att.filename,
                    "content_type": att.content_type,
                    "size": att.size,
                    "is_inline": att.is_inline
                }
                for att in self.attachments
            ],
            "flags": [flag.value for flag in self.flags],
            "folder": self.folder,
            "account_id": self.account_id,
            "priority": self.priority,
            "has_attachments": self.has_attachments()
        }
    
    def __str__(self) -> str:
        """
        メッセージの文字列表現
        
        Returns:
            str: メッセージ情報の文字列
        """
        date_str = self.get_display_date().strftime("%Y/%m/%d %H:%M")
        flags_str = "".join([
            "📖" if self.is_read() else "📩",
            "⭐" if self.is_flagged() else "",
            "📎" if self.has_attachments() else ""
        ])
        
        return f"{flags_str} {date_str} | {self.sender} | {self.subject}"