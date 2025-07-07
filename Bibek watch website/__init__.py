from flask import Flask
from .extensions import db, login_manager, mail
from .routes import main
from flask_login import current_user

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = '22421'

    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://shreemishra:yourpassword@shreemishra.mysql.pythonanywhere-services.com/shreemishra$watchstore"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Email config
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'swayamshree220@gmail.com'
    app.config['MAIL_PASSWORD'] = 'cbhj rqiw gkbp ynks'

    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'

    app.register_blueprint(main)

    @app.context_processor
    def inject_user():
        return dict(logged_in=current_user.is_authenticated if current_user else False)

    @app.template_filter('zip')
    def zip_filter(a, b):
        return zip(a, b)

    return app
