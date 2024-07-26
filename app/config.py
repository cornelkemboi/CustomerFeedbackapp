import os


class Config:
    MYSQL_DB = os.getenv('MYSQL_DB')
    MYSQL_HOST = os.getenv('MYSQL_HOST')
    MYSQL_USER = os.getenv('MYSQL_USER')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
    SECRET_KEY = os.getenv('SECRET_KEY')
