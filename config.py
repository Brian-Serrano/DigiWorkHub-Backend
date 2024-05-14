import os
import re
from typing import Optional, Set

import firebase_admin
from firebase_admin.credentials import Certificate

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from firebase_admin import credentials

# create certificate and initialize firebase admin
cred: Certificate = credentials.Certificate("service_account_key.json")
firebase_admin.initialize_app(cred)

# pattern for matching password
PASSWORD_REGEX = re.compile(os.getenv("PASSWORD_REGEX"))
# pattern for matching email
EMAIL_REGEX = re.compile(os.getenv("EMAIL_REGEX"))
# pattern for matching name
NAME_REGEX = re.compile(os.getenv("NAME_REGEX"))
# salt used for hashing passwords
SALT: bytes = os.getenv("SALT").encode("utf-8")
# google password for sending mails to user
PASSWORD: Optional[str] = os.getenv("PASSWORD")

ALLOWED_FILE_EXTENSIONS: Set[str] = {"7z", "aac", "accdb", "accft", "adx", "ai", "aiff", "aifc", "amr", "amv", "avi", "avif", "bmp", "blend", "cdf", "cdr", "cgm", "csv", "doc", "docx", "docm", "dot", "dotx", "dpx", "drc", "dtd", "dwf", "dwg", "dxf", "email", "emf", "eml", "emz", "eot", "esd", "exp", "f4v", "fbx", "flac", "flv", "fni", "fnx", "fodg", "fodp", "fods", "fodt", "gif", "gz", "hdi", "icl", "ico", "img", "info", "iso", "j2c", "jp2", "jpe", "jpeg", "jpg", "json", "jxl", "ldb", "lz", "m3u", "m3u8", "m4a", "m4p", "m4r", "m4v", "md", "mdf", "mdi", "mov", "mp2", "mp3", "mp4", "mpa", "mpc", "mpeg", "mpg", "mso", "mxf", "odb", "odf", "odg", "odp", "ods", "odt", "oga", "ogg", "ogv", "ogx", "ost", "otf", "otg", "otp", "ots", "ott", "pdf", "pgn", "png", "pptx", "ppsx", "ppt", "psd", "psdc", "pub", "rar", "rtf", "svg", "swf", "stc", "std", "sti", "stw", "sxc", "sxd", "sxg", "sxi", "sxm", "sxw", "tak", "tar", "taz", "tb2", "tbz", "tbz2", "tif", "tiff", "torrent", "ttc", "ttf", "url", "uxf", "wav", "webm", "wma", "wmdb", "wmf", "wmv", "wtx", "xls", "xlsb", "xlsm", "xlsx", "xmf", "xml", "xps", "zip"}
ALLOWED_IMAGE_EXTENSIONS: Set[str] = {"png", "jpg", "jpeg", "gif", "bmp", "webp"}

# initialize flask application
api: Flask = Flask(__name__, template_folder="templates")
# directory of database
api.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DIGIWORKHUB_DB_URI")
# secret key for decoding/encoding authorization tokens
api.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
# maximum file size for attachments (50mb)
api.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
# integrate SQLAlchemy on flask
db: SQLAlchemy = SQLAlchemy(api)
