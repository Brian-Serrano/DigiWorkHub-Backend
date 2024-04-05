import os
import re

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

PASSWORD_REGEX = re.compile(os.getenv("PASSWORD_REGEX"))
EMAIL_REGEX = re.compile(os.getenv("EMAIL_REGEX"))
NAME_REGEX = re.compile(os.getenv("NAME_REGEX"))
SALT = os.getenv("SALT").encode("utf-8")
ALLOWED_FILE_EXTENSIONS = {"7z", "aac", "accdb", "accft", "adx", "ai", "aiff", "aifc", "amr", "amv", "avi", "avif",
                           "bmp", "blend", "cdf", "cdr", "cgm", "csv", "doc", "docx", "docm", "dot", "dotx", "dpx",
                           "drc", "dtd", "dwf", "dwg", "dxf", "email", "emf", "eml", "emz", "eot", "esd", "exp", "f4v",
                           "fbx", "flac", "flv", "fni", "fnx", "fodg", "fodp", "fods", "fodt", "gif", "gz", "hdi",
                           "icl", "ico", "img", "info", "iso", "j2c", "jp2", "jpe", "jpeg", "jpg", "json", "jxl", "ldb",
                           "lz", "m3u", "m3u8", "m4a", "m4p", "m4r", "m4v", "md", "mdf", "mdi", "mov", "mp2", "mp3",
                           "mp4", "mpa", "mpc", "mpeg", "mpg", "mso", "mxf", "odb", "odf", "odg", "odp", "ods", "odt",
                           "oga", "ogg", "ogv", "ogx", "ost", "otf", "otg", "otp", "ots", "ott", "pdf", "pgn", "png", "pptx",
                           "ppsx", "ppt", "psd", "psdc", "pub", "rar", "rtf", "svg", "swf", "stc", "std", "sti", "stw",
                           "sxc", "sxd", "sxg", "sxi", "sxm", "sxw", "tak", "tar", "taz", "tb2", "tbz", "tbz2", "tif",
                           "tiff", "torrent", "ttc", "ttf", "url", "uxf", "wav", "webm", "wma", "wmdb", "wmf", "wmv",
                           "wtx", "xls", "xlsb", "xlsm", "xlsx", "xmf", "xml", "xps", "zip"}
ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "bmp", "webp"}

api = Flask(__name__, template_folder="templates")
api.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///digiwork_hub.db"
api.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
api.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024
db = SQLAlchemy(api)
