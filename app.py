from config import api, db
from routes import auth_bp, task_bp, user_bp, message_bp, comment_bp, checklist_bp, subtask_bp, attachment_bp

# attach the routes to the flask application
api.register_blueprint(auth_bp, url_prefix="/auth_routes")
api.register_blueprint(task_bp, url_prefix="/task_routes")
api.register_blueprint(user_bp, url_prefix="/user_routes")
api.register_blueprint(message_bp, url_prefix="/message_routes")
api.register_blueprint(comment_bp, url_prefix="/comment_routes")
api.register_blueprint(checklist_bp, url_prefix="/checklist_routes")
api.register_blueprint(subtask_bp, url_prefix="/subtask_routes")
api.register_blueprint(attachment_bp, url_prefix="/attachment_routes")

# entry point of flask application
if __name__ == '__main__':

    # create database
    with api.app_context():
        db.create_all()

    # run application
    api.run()
