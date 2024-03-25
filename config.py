import os
import re

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

PASSWORD_REGEX = re.compile(os.getenv("PASSWORD_REGEX"))
EMAIL_REGEX = re.compile(os.getenv("EMAIL_REGEX"))
NAME_REGEX = re.compile(os.getenv("NAME_REGEX"))
SALT = os.getenv("SALT").encode("utf-8")
ALLOWED_FILE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "drawio", "docx", "pptx", "xlsx", "pdf", "mp3", "mp4", "wav", "ogg"}
ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg"}

api = Flask(__name__, template_folder="templates")
api.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///digiwork_hub.db"
api.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
db = SQLAlchemy(api)
