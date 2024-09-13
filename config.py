class Config:
     MYSQL_HOST = 'localhost'
     MYSQL_USER = 'root'
     MYSQL_PASSWORD = ''
     MYSQL_DB = 'guru_honorer'
     DEBUG = True
     UPLOAD_FOLDER = 'uploads'
     SECRET_KEY = 'teacher_honorer'
     SQLALCHEMY_DATABASE_URI = 'mysql://root:@localhost/guru_honorer'
     SQLALCHEMY_TRACK_MODIFICATIONS = False