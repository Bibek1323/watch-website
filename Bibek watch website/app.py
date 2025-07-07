from flask import Flask
from extensions import db, login_manager
from flask_mail import Mail

app = Flask(__name__)
app.secret_key = "244224567"


app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://shreemishra:shreesql@shreemishra.mysql.pythonanywhere-services.com/shreemishra$default"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


# Mail config
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'swayamshree220@gmail.com'
app.config['MAIL_PASSWORD'] = '1234'

db.init_app(app)
login_manager.init_app(app)
mail = Mail(app)

with app.app_context():
    db.create_all()

# Import routes AFTER app and extensions are set up
import routes

if __name__ == "__main__":
    app.run(debug=True)
