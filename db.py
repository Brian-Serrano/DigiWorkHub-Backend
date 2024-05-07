from datetime import datetime

from config import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False, default="Test")
    email = db.Column(db.String, nullable=False, default="test@gmail.com")
    password = db.Column(db.String, nullable=False, default="test123")
    image_path = db.Column(db.String, nullable=False, default="images")
    role = db.Column(db.String, nullable=False, default="NA")
    forgot_password_code = db.Column(db.String, nullable=False, default="")
    push_notifications_token = db.Column(db.String, nullable=False, default="")


class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, nullable=False, default="TestTask")
    description = db.Column(db.String, nullable=False, default="TestTaskDesc")
    status = db.Column(db.String, nullable=False, default="OPEN")
    priority = db.Column(db.String, nullable=False, default="LOW")
    due = db.Column(db.DateTime, nullable=False, default=datetime.now())
    date_sent = db.Column(db.DateTime, nullable=False, default=datetime.now())
    assignee = db.Column(db.String, nullable=False, default="")
    creator_id = db.Column(db.Integer, nullable=False, default=0)
    type = db.Column(db.String, nullable=False, default="TASK")


class TaskComment(db.Model):
    comment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    description = db.Column(db.String, nullable=False, default="TestCommentMessage")
    reply_id = db.Column(db.String, nullable=False, default="")
    mentions_id = db.Column(db.String, nullable=False, default="")
    user_id = db.Column(db.Integer, nullable=False, default=0)
    task_id = db.Column(db.Integer, nullable=False, default=0)
    date_sent = db.Column(db.DateTime, nullable=False, default=datetime.now())
    likes_id = db.Column(db.String, nullable=False, default="")


class Subtask(db.Model):
    subtask_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    task_id = db.Column(db.Integer, nullable=False, default=0)
    description = db.Column(db.String, nullable=False, default="TestTaskDesc")
    status = db.Column(db.String, nullable=False, default="OPEN")
    priority = db.Column(db.String, nullable=False, default="LOW")
    due = db.Column(db.DateTime, nullable=False, default=datetime.now())
    date_sent = db.Column(db.DateTime, nullable=False, default=datetime.now())
    assignee = db.Column(db.String, nullable=False, default="")
    creator_id = db.Column(db.Integer, nullable=False, default=0)
    type = db.Column(db.String, nullable=False, default="TASK")


class Checklist(db.Model):
    checklist_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    task_id = db.Column(db.Integer, nullable=False, default=0)
    user_id = db.Column(db.Integer, nullable=False, default=0)
    description = db.Column(db.String, nullable=False, default="TestTaskDesc")
    is_checked = db.Column(db.Boolean, nullable=False, default=False)
    assignee = db.Column(db.String, nullable=False, default="")
    date_sent = db.Column(db.DateTime, nullable=False, default=datetime.now())


class Attachment(db.Model):
    attachment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    task_id = db.Column(db.Integer, nullable=False, default=0)
    user_id = db.Column(db.Integer, nullable=False, default=0)
    attachment_path = db.Column(db.String, nullable=False, default="attachments")
    file_name = db.Column(db.String, nullable=False, default="file.docx")
    date_sent = db.Column(db.DateTime, nullable=False, default=datetime.now())


class Message(db.Model):
    message_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date_sent = db.Column(db.DateTime, nullable=False, default=datetime.now())
    title = db.Column(db.String, nullable=False, default="TestMessage")
    description = db.Column(db.String, nullable=False, default="TestMessageDesc")
    sender_id = db.Column(db.Integer, nullable=False, default=0)
    receiver_id = db.Column(db.Integer, nullable=False, default=0)
    attachment_paths = db.Column(db.String, nullable=False, default="")
    file_names = db.Column(db.String, nullable=False, default="")
    deleted_from_sender = db.Column(db.Boolean, nullable=False, default=False)
    deleted_from_receiver = db.Column(db.Boolean, nullable=False, default=False)


class MessageReply(db.Model):
    message_reply_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    message_id = db.Column(db.Integer, nullable=False, default=0)
    date_sent = db.Column(db.DateTime, nullable=False, default=datetime.now())
    description = db.Column(db.String, nullable=False, default="TestMessageDesc")
    from_id = db.Column(db.Integer, nullable=False, default=0)
    attachment_paths = db.Column(db.String, nullable=False, default="")
    file_names = db.Column(db.String, nullable=False, default="")
