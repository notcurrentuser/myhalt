import os

from dotenv import load_dotenv

from halt_app import route
from users_db import user_model

load_dotenv()


if __name__ == '__main__':
    if os.getenv("IS_FIRST_START") == '1':
        user_model.reset_db()

    route.run()
