from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager
from dotenv import load_dotenv
from routes import routes
from models import db
import os

# Load environment variables before reading them
load_dotenv()

app = Flask(__name__)

database_uri = os.environ.get("DATABASE_URI")
secret_key = os.environ.get("JWT_SECRET")
frontend_url = os.environ.get("FRONTEND_URL")  # https://your-app.vercel.app

# Flask configuration
app.config["SQLALCHEMY_DATABASE_URI"] = database_uri
app.config["SECRET_KEY"] = secret_key

# Session cookie configuration
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SECURE"] = True          # HTTPS only
app.config["SESSION_COOKIE_SAMESITE"] = "None"      # Required for cross-site cookies

# If you use remember=True with Flask-Login
app.config["REMEMBER_COOKIE_SECURE"] = True
app.config["REMEMBER_COOKIE_SAMESITE"] = "None"

# Initialize extensions
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

# Allow only your frontend
CORS(
    app,
    supports_credentials=True,
    origins=[frontend_url]
)

app.register_blueprint(routes)


@login_manager.user_loader
def load_user(user_id):
    from models.user import Users
    return Users.query.get(int(user_id))


@app.get("/")
def index():
    return "The server is running."


if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)