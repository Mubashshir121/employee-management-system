from dotenv import load_dotenv
load_dotenv()

from flask import Flask, redirect, url_for

from config import Config
from extensions import db, login_manager
from models import User


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.employee import employee_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(employee_bp)

    @app.route("/")
    def index():
        return redirect(url_for("auth.login"))

    return app


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


app = create_app()

if __name__ == "__main__":
    app.run()
    
