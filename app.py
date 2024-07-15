from flask import Flask
from config import Config
from extensions import mysql, cors, db
from blueprints.auth import auth
from blueprints.main import main
from blueprints.clustering import clustering

import os
from flask_migrate import Migrate
from flask import Flask
from config import Config
from extensions import mysql, cors, db
from blueprints.auth import auth
from blueprints.main import main

app = Flask(__name__)

app.config.from_object(Config)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

mysql.init_app(app)
cors.init_app(app)
db.init_app(app)

# Flask Migrate SQLAlchemy
migrate = Migrate(app, db, compare_type=True)

# daftar blueprint agar lebih mudah dibaca
app.register_blueprint(auth)
app.register_blueprint(main)
app.register_blueprint(clustering)

if __name__ == '__main__':
     # Buat folder 'uploads' jika belum ada
     if not os.path.exists(app.config['UPLOAD_FOLDER']):
          os.makedirs(app.config['UPLOAD_FOLDER'])

     app.run(debug=True)
