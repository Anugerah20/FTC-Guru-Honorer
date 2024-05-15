# app.py
from flask import Flask
from config import Config
from extensions import mysql, cors
from blueprints.auth import auth
from blueprints.main import main

import pandas as pd
from flask import Flask, request, render_template

app = Flask(__name__)
app.config.from_object(Config)

mysql.init_app(app)
cors.init_app(app)

app.register_blueprint(auth)
app.register_blueprint(main)

if __name__ == '__main__':
     app.run(debug=True)
