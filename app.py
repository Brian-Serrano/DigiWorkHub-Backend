from config import api, db
from routes import get_bp, post_bp, auth_bp

api.register_blueprint(get_bp, url_prefix="/get_routes")
api.register_blueprint(post_bp, url_prefix="/post_routes")
api.register_blueprint(auth_bp, url_prefix="/auth_routes")

if __name__ == '__main__':

    with api.app_context():
        db.create_all()

    api.run()
