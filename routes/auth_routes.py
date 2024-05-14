import os
import smtplib
import ssl
import string
from datetime import datetime, timedelta
import random
from email.mime.text import MIMEText
from typing import Tuple, Dict, Any

import bcrypt
import jwt
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from PIL.ImageFont import FreeTypeFont
from flask import Blueprint, request, jsonify, Response
from werkzeug.utils import secure_filename

from config import db, api, SALT, PASSWORD
from db import User
from utils import validate_signup, validate_login, get_response_image, validate_forgot_password

auth_bp = Blueprint("auth_routes", __name__)


@auth_bp.route("/sign_up", methods=["POST"])
def sign_up() -> Tuple[Response, int]:
    try:
        # get the request body
        data: Dict[str, Any] = request.get_json()
        # validate the data on request body
        validation: Dict[str, Any] = validate_signup(data["name"], data["email"], data["password"], data["confirmPassword"])

        # check if request is valid
        if validation["isValid"]:
            # create font
            font: FreeTypeFont = ImageFont.truetype("fonts/RobotoSlab-Black.ttf", 150)
            # create 200x200 image with random background color
            img: Image = Image.new("RGBA", (200, 200), (int(random.random() * 100) + 100, int(random.random() * 100) + 100, int(random.random() * 100) + 100))
            draw: ImageDraw = ImageDraw.Draw(img)
            # draw text to image at center with the first letter of username in uppercase
            draw.text((100, 100), data["name"][0].upper(), fill=(0, 0, 0), font=font, anchor="mm")
            # create file name
            filename: str = secure_filename(datetime.now().strftime('%d_%m_%Y_%H_%M_%S') + ".png")
            # save image as the default user image
            img.save(os.path.join("images", filename))

            # create user with the path of image and valid request data
            user: User = User(
                name=data["name"],
                email=data["email"],
                password=bcrypt.hashpw(data["password"].encode(), SALT).decode(),
                image_path="images/" + filename,
                push_notifications_token=data["notificationToken"]
            )
            # add the user in database
            db.session.add(user)
            # commit/apply the added user
            db.session.commit()

            # create authorization token that will expire in 7 days
            token: str = jwt.encode({"user_id": user.id, "exp": datetime.now() + timedelta(days=7)}, api.config['SECRET_KEY'], algorithm='HS256')
            # return user, message, authorization token, user image as response
            response: Dict[str, Any] = {
                "message": "Success",
                "token": token,
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "password": data["password"],
                "image": get_response_image(user.image_path)
            }
            return jsonify(response), 201
        else:
            return jsonify({"type": "Validation Error", "message": validation["message"]}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@auth_bp.route("/log_in", methods=["POST"])
def login() -> Tuple[Response, int]:
    try:
        # get the request body
        data: Dict[str, Any] = request.get_json()
        # get the user that wants to log in
        user: User = User.query.filter_by(email=data["email"]).first()
        # validate log in
        validation: Dict[str, Any] = validate_login(user, data["email"], data["password"])
        # check if valid
        if validation["isValid"]:
            # create authorization token that will expire in 7 days
            token: str = jwt.encode({"user_id": user.id, "exp": datetime.now() + timedelta(days=7)}, api.config['SECRET_KEY'], algorithm='HS256')
            # change the push notifications token of user to new token
            user.push_notifications_token = data["notificationToken"]
            # commit apply the changed push notification token
            db.session.commit()

            # return user, message, authorization token, user image as response
            response: Dict[str, Any] = {
                "message": "Success",
                "token": token,
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "password": data["password"],
                "image": get_response_image(user.image_path)
            }
            return jsonify(response), 201
        else:
            return jsonify({"type": "Validation Error", "message": validation["message"]}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@auth_bp.route("/forgot_password", methods=["POST"])
def forgot_password() -> Tuple[Response, int]:
    try:
        # get the request body
        data: Dict[str, Any] = request.get_json()
        # generate random code that will be sent in mail
        code: str = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(8))

        # define the data of mail
        email_sender: str = "Brianserrano503@gmail.com"
        email_receiver: str = data["email"]
        msg: MIMEText = MIMEText(f'<p>Use this code to change your password: </p><h3 style="color:blue;">{code}</h3>', "html")
        msg["Subject"] = "DigiWork Hub Forgot Password"
        msg["From"] = email_sender
        msg["To"] = email_receiver
        context: ssl.SSLContext = ssl.create_default_context()

        # add the code to user's database temporarily that will be used soon to check code matches
        user: User = User.query.filter_by(email=data["email"]).first()
        user.forgot_password_code = code

        # send the mail with code to the user
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
            smtp.login(email_sender, PASSWORD)
            smtp.sendmail(email_sender, email_receiver, msg.as_string())
            # commit/apply the forgot password code added
            db.session.commit()
            # return message
            return jsonify({"message": "Success"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@auth_bp.route("/change_password", methods=["POST"])
def change_password() -> Tuple[Response, int]:
    try:
        # get the request body
        data: Dict[str, Any] = request.get_json()
        # get the user that will change the password
        user: User = User.query.filter_by(email=data["email"]).first()
        # validate the request data
        validation: Dict[str, Any] = validate_forgot_password(user, data["code"], data["password"], data["confirmPassword"])

        # check if request is valid
        if validation["isValid"]:
            user.password = bcrypt.hashpw(data["password"].encode(), SALT).decode()
            user.forgot_password_code = ""
            db.session.commit()
            return jsonify({"message": "Success"}), 201
        else:
            return jsonify({"type": "Validation Error", "message": validation["message"]}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500
