from flask import Flask

app = Flask(__name__)
app.config.from_object('config')

from ImageManipulator import views
app.run()
