import re
from models.user import Users


# -----------------------------
# EMAIL
# -----------------------------
EMAIL_REGEX = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'


def validate_email(email):
    if not email or not isinstance(email, str):
        return False, 'Email is required.'

    email = email.strip().lower()

    if len(email) < 3 or len(email) > 150:
        return False, 'Email must be between 3 and 150 characters.'

    if not re.match(EMAIL_REGEX, email):
        return False, 'Invalid email address.'

    if Users.query.filter_by(email=email).first():
        return False, 'Email already registered.'

    return True, ''


# -----------------------------
# PASSWORD (STRONGER)
# -----------------------------
def validate_password(password):
    if not password or not isinstance(password, str):
        return False, 'Password is required.'

    if len(password) < 5 or len(password) > 128:
        return False, 'Password must be between 5 and 128 characters.'

    return True, ''


# -----------------------------
# USERNAME
# -----------------------------
USERNAME_REGEX = r"^[a-zA-Z0-9_-]{3,25}$"


def validate_username(username):
    if not username or not isinstance(username, str):
        return False, 'Username cannot be empty.'

    username = username.strip()

    if len(username) < 3 or len(username) > 25:
        return False, 'Username must be between 3 and 25 characters.'

    if not re.match(USERNAME_REGEX, username):
        return False, 'Username can only contain letters, numbers, underscores, and hyphens.'

    if Users.query.filter_by(username=username).first():
        return False, 'Username already taken.'

    return True, ''