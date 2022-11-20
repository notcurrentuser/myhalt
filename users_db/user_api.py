from users_db.user_model import User


def get_user_info_by_id(user_id):
    return User.query.filter_by(id=user_id).first()


def get_user_info_by_login(login):
    return User.query.filter_by(login=login).first()
