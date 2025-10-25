from flask import Blueprint

user_bp = Blueprint('user', __name__, template_folder='views/templates', static_folder='views/static')

@user_bp.route('/')
def root():
    return "User Blueprint Root"

@user_bp.route('/settings')
def settings():
    return "User Settings Page"