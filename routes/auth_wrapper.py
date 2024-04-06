from functools import wraps

import jwt
from flask import request, jsonify

from config import api
from db import User


def auth_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = request.headers["Authorization"]

        if not token:
            return jsonify({"error": "A valid token is missing!"}), 401
        
        try:
            data = jwt.decode(token, api.config['SECRET_KEY'], algorithms=['HS256'])
            user = User.query.filter_by(id=data["user_id"]).first()

            if not user:
                return jsonify({"error": "User not found"}), 401

            current_user = {
                "id": user.id,
                "name": user.name,
                "email": user.email
            }
        except Exception as e:
            return jsonify({"error": f"Invalid token! {e}"}), 401

        return f(current_user, *args, **kwargs)
    
    return decorator

