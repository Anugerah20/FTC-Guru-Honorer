from extensions import db

# Migrasi tabel users dari SQLAlchemy
class User(db.Model):
     __tablename__ = 'users'
     id = db.Column(db.Integer, primary_key=True)
     username = db.Column(db.String(100), nullable=False)
     password = db.Column(db.String(50), nullable=False)
     email = db.Column(db.String(100), nullable=False)

# Migrasi tabel guru dari SQLAlchemy
class Guru(db.Model):
     __tablename__ = 'guru'
     id = db.Column(db.Integer, primary_key=True)
     conversation_id_str = db.Column(db.String(255))
     created_at = db.Column(db.DateTime)
     favorite_count = db.Column(db.Integer)
     full_text = db.Column(db.Text)
     id_str = db.Column(db.String(255))
     image_url = db.Column(db.String(255))
     in_reply_to_screen_name = db.Column(db.String(255))
     lang = db.Column(db.String(10))
     location = db.Column(db.String(255))
     quote_count = db.Column(db.Integer)
     reply_count = db.Column(db.Integer)
     retweet_count = db.Column(db.Integer)
     tweet_url = db.Column(db.String(255))
     user_id_str = db.Column(db.String(255))
     username = db.Column(db.String(255))

# Migrate tabel preprocess_guru dari SQLAlchemy
class PreprocessGuru(db.Model):
     __tablename__ = 'preprocess_guru'
     id = db.Column(db.Integer, primary_key=True)
     full_text = db.Column(db.Text)
     username = db.Column(db.String(255))
     created_at = db.Column(db.DateTime)
     tweet_url = db.Column(db.String(255))

# Migrate tabel data_training dari SQLAlchemy
class DataTraining(db.Model):
     __tablename__ = 'data_training'
     id = db.Column(db.Integer, primary_key=True)
     full_text = db.Column(db.Text)
     category = db.Column(db.String(255))

# Migrate tabel data_testing dari SQLAlchemy
class DataTesting(db.Model):
     __tablename__ = 'data_testing'
     id = db.Column(db.Integer, primary_key=True)
     full_text = db.Column(db.Text)
     categories = db.Column(db.String(255))
