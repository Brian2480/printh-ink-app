from flask_login import login_user 
from werkzeug.security import generate_password_hash , check_password_hash
from sqlalchemy import select

from src.app.models import User


def service_login( db_session , username , password ):
    stmt = select(User).filter_by(username = username)
    user = db_session.execute(stmt).scalar_one_or_none()

    if user and check_password_hash(user.password_hash , password ):
        login_user(user)
        return user


def service_register(db_session , username , password ):
    new_user = User(
        username = username,                               #type: ignore
        password_hash = generate_password_hash(password),  #type: ignore
        is_admin = False                                   #type: ignore
    )
    db_session.add(new_user)
    return
