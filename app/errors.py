from flask import render_template, jsonify
from app import app, db

from flask_mail import Message
from flask_exceptions import APIException


@app.errorhandler(404)
def not_found_error(error):
    app.logger.error(error)
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    app.logger.error(error)
    
    return render_template('500.html'), 500

