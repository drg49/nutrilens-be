import re
from models.user import Users


# -----------------------------
# EMAIL
# -----------------------------
EMAIL_REGEX = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'


def validate_email(email):
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
    if len(password) < 8 or len(password) > 128:
        return False, 'Password must be between 8 and 128 characters.'

    if ' ' in password:
        return False, 'Password cannot contain spaces.'

    if not re.search(r'[A-Z]', password):
        return False, 'Password must contain at least one uppercase letter.'

    if not re.search(r'[a-z]', password):
        return False, 'Password must contain at least one lowercase letter.'

    if not re.search(r'\d', password):
        return False, 'Password must contain at least one number.'

    return True, ''


# -----------------------------
# USERNAME
# -----------------------------
USERNAME_REGEX = r"^[a-zA-Z0-9_-]{3,25}$"


def validate_username(username):
    if not username:
        return False, 'Username cannot be empty.'

    username = username.strip()

    if len(username) < 3 or len(username) > 25:
        return False, 'Username must be between 3 and 25 characters.'

    if not re.match(USERNAME_REGEX, username):
        return False, 'Username can only contain letters, numbers, underscores, and hyphens.'

    if Users.query.filter_by(username=username).first():
        return False, 'Username already taken.'

    return True, ''