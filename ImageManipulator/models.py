from . import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_filename = db.Column(db.Text, index=True)
    save_path = db.Column(db.Text, index=True, unique=True)
    results = db.Column(db.Text, index=True, unique=True)

    def __init__(self, original_filename, save_path, results):
        self.original_filename = original_filename
        self.save_path = save_path
        self.results = results

    def __repr__(self):
        return '<Image %r>' % self.save_path
