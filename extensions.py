from flask_mysqldb import MySQL
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

mysql = MySQL()
cors = CORS()
db = SQLAlchemy()