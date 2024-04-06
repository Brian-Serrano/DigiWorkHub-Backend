import os
from datetime import datetime, timedelta
import random

import bcrypt
import jwt
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename

from config import db, api, SALT
from db import User
from utils import validate_signup, validate_login, get_response_image

auth_bp = Blueprint("auth_routes", __name__)


@auth_bp.route("/sign_up", methods=["POST"])
def sign_up():
    try:
        data = request.get_json()
        validation = validate_signup(data["name"], data["email"], data["password"], data["confirmPassword"])

        if validation["isValid"]:
            font = ImageFont.truetype("fonts/RobotoSlab-Black.ttf", 150)
            img = Image.new("RGBA", (200, 200), (int(random.random() * 100) + 100, int(random.random() * 100) + 100, int(random.random() * 100) + 100))
            draw = ImageDraw.Draw(img)
            draw.text((100, 100), data["name"][0].upper(), fill=(0, 0, 0), font=font, anchor="mm")
            filename = secure_filename(datetime.now().strftime('%d_%m_%Y_%H_%M_%S') + ".png")
            img.save(os.path.join("images", filename))

            user = User(
                name=data["name"],
                email=data["email"],
                password=bcrypt.hashpw(data["password"].encode(), SALT).decode(),
                image_path="images/" + filename
            )
            db.session.add(user)
            token = jwt.encode({"user_id": user.id, "exp": datetime.now() + timedelta(days=7)}, api.config['SECRET_KEY'], algorithm='HS256')

            db.session.commit()
            response = {
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
def login():
    try:
        data = request.get_json()
        user = User.query.filter_by(email=data["email"]).first()
        validation = validate_login(user, data["email"], data["password"])
        if validation["isValid"]:
            token = jwt.encode({"user_id": user.id, "exp": datetime.now() + timedelta(days=7)}, api.config['SECRET_KEY'], algorithm='HS256')
            response = {
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
        return jsonify({"error": f"Unhandled exception: {e}"}), 500
