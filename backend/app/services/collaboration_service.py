from app import db
from app.models.collaboration import ThreadedComment, Notification
from datetime import datetime
import hashlib

class CollaborationService:
    @staticmethod
    def add_comment(user_id, document_id, content, parent_comment_id=None):
        comment = ThreadedComment(
            user_id=user_id,
            document_id=document_id,
            content=content,
            parent_comment_id=parent_comment_id,
            created_at=datetime.utcnow(),
            content_hash=hashlib.sha256(content.encode()).hexdigest()
        )
        db.session.add(comment)
        db.session.commit()
        return comment

    @staticmethod
    def resolve_comment(comment_id, resolved_by_id):
        comment = ThreadedComment.query.get(comment_id)
        if not comment:
            raise ValueError(f"Comment {comment_id} not found")
        comment.is_resolved = True
        comment.resolved_by_id = resolved_by_id
        comment.resolved_at = datetime.utcnow()
        db.session.commit()
        return comment

    @staticmethod
    def get_comment_thread(document_id, parent_id=None):
        if parent_id:
            return ThreadedComment.query.filter_by(
                document_id=document_id,
                parent_comment_id=parent_id
            ).order_by(ThreadedComment.created_at).all()
        return ThreadedComment.query.filter_by(
            document_id=document_id,
            parent_comment_id=None
        ).order_by(ThreadedComment.created_at).all()

    @staticmethod
    def send_notification(user_id, notification_type, source_id, message):
        notif = Notification(
            user_id=user_id,
            notification_type=notification_type,
            source_id=source_id,
            message=message,
            created_at=datetime.utcnow(),
            is_read=False
        )
        db.session.add(notif)
        db.session.commit()
        return notif

    @staticmethod
    def mark_notification_read(notification_id):
        notif = Notification.query.get(notification_id)
        if notif:
            notif.is_read = True
            notif.read_at = datetime.utcnow()
            db.session.commit()
        return notif

    @staticmethod
    def get_unread_notifications(user_id):
        return Notification.query.filter_by(
            user_id=user_id,
            is_read=False
        ).order_by(Notification.created_at.desc()).all()

    @staticmethod
    def delete_comment(comment_id):
        comment = ThreadedComment.query.get(comment_id)
        if comment:
            db.session.delete(comment)
            db.session.commit()
        return comment
