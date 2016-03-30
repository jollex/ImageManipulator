from flask import Flask

app = Flask(__name__)
app.config.from_object('config')

if not app.debug:
    from logging import FileHandler
    file_handler = FileHandler('app.log')
    file_handler.setLevel(logging.WARNING)
    app.logger.addHandler(file_handler)

from ImageManipulator import views

if __name__=='__main__'
    app.run()
