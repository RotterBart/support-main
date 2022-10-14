from app import app, db
from app import socketio
from app.models import User, Post
import logging
from logging.handlers import RotatingFileHandler
import os

# if not app.debug:
#     if not os.path.exists('logs'):
#         os.mkdir('logs')

#     file_handler = RotatingFileHandler('logs/project.log',
#                                        maxBytes=10240,
#                                        backupCount=10)
#     file_handler.setFormatter(
#         logging.Formatter(
#             '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
#         ))
#     file_handler.setLevel(logging.INFO)
    # app.logger.addHandler(file_handler)
    # app.logger.setLevel(logging.INFO)


# для flask shell
# @app.shell_context_processor
# def make_shell_context():
#     return {'db': db, 'User': User, 'Post': Post}


if __name__ == '__main__':
    #app.logger.info('Initialising..')
    app.run(debug=True, port=5000, host='0.0.0.0')
    # socketio.run(app, debug=True, host='0.0.0.0', port=5000)
