from functools import wraps
from typing import Dict, Any, Tuple, Optional

import jwt
from flask import request, jsonify, Response

from config import api
from db import User


def auth_required(f):
    """Wrapper function for routes that need authorization"""
    @wraps(f)
    def decorator(*args: Any, **kwargs: Any) -> Tuple[Response, int]:
        # get the authorization token
        token: str = request.headers["Authorization"]

        # check if token not exist
        if not token:
            return jsonify({"error": "A valid token is missing!"}), 401
        
        try:
            # get the data from the token (decode it)
            data: Dict[str, Any] = jwt.decode(token, api.config['SECRET_KEY'], algorithms=['HS256'])
            # get the user using the data of decoded token
            user: Optional[User] = User.query.filter_by(id=data["user_id"]).first()

            # check if user not exist
            if not user:
                return jsonify({"error": "User not found"}), 401

            # the user information that can be used for the routes that have authorization
            current_user: Dict[str, Any] = {
                "id": user.id,
                "name": user.name,
                "email": user.email
            }
        except Exception as e:
            return jsonify({"error": f"Invalid token! {e}"}), 401

        return f(current_user, *args, **kwargs)
    
    return decorator

