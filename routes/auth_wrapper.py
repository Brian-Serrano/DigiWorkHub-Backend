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
            user_obj = User.query.filter_by(id=data["user_id"]).first()
            user = {
                "id": user_obj.id,
                "name": user_obj.name,
                "email": user_obj.email
            }
        except Exception as e:
            return jsonify({"error": f"Invalid token! {e}"}), 401

        return f(user, *args, **kwargs)
    
    return decorator

