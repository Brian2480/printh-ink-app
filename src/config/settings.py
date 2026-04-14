import os
from dotenv import load_dotenv

load_dotenv()


class DevelopmentConfig():
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SECRET_KEY = os.getenv('SECRET_KEY')
    AUTO_CREATE_TABLES = True
    SQL_ECHO = True
    DEBUG = True

    CLOUDINARY_NAME = os.getenv('CLOUDINARY_NAME')
    CLOUDINARY_API_KEY = os.getenv('CLOUDINARY_API_KEY')
    CLOUDINARY_API_SECRET = os.getenv('CLOUDINARY_API_SECRET')

class ProductionConfig():
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    SECRET_KEY = os.environ['DATABASE_URL']
    AUTO_CREATE_TABLES = False
    SQL_ECHO = False
    DEBUG = False

    CLOUDINARY_NAME = os.environ['CLOUDINARY_NAME']
    CLOUDINARY_API_KEY = os.environ['CLOUDINARY_API_KEY']
    CLOUDINARY_API_SECRET = os.environ['CLOUDINARY_API_SECRET']


APP_ENV = os.getenv('APP_ENV')


config_map = {
    'development': DevelopmentConfig(),
    'production': ProductionConfig()
}

ConfigClass = config_map.get(APP_ENV) #type: ignore

if not ConfigClass:
    raise RuntimeError(f'INVALID APP_ENV: {APP_ENV}')


