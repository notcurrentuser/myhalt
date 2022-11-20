from flask_login import UserMixin
from sqlalchemy_utils import database_exists, create_database, drop_database


from halt_app import db, manager, app, DB_URL, POSTGRES_DB


class User (db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(128), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)


@manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


def reset_db():
    with app.app_context():
        if database_exists(DB_URL) and \
                input(f"Database {POSTGRES_DB} already exists, reset? Type 'y' to confirm\n").lower() == 'y':
            drop_database(DB_URL)
        create_database(DB_URL)
        db.create_all()
        print('Successfully created')
