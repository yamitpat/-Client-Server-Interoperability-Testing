from flask import Blueprint
auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return "<h1>Login</h1><p>This is the login page!</p>",200

@auth.route('/logout')
def logout():
    return "<h1>Logout</h1><p>This is the logout page!</p>",200

@auth.route('/sign_up')
def sign_up():
    return "<h1>Signup</h1><p>This is the signup page!</p>", 200
