from . import db

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_filename = db.Column(db.Text, index=True)
    filename = db.Column(db.Text, index=True, unique=True)
    results = db.Column(db.Text, index=True)

    def __init__(self, original_filename, filename, results):
        self.original_filename = original_filename
        self.filename = filename
        self.results = results

    def __repr__(self):
        return '<Image %r>' % self.filename
