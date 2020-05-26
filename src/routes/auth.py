from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify, make_response
)
from werkzeug.security import check_password_hash, generate_password_hash
import functools
import jwt

from ..models.user import User, getOptionalUserParams
from ..models.blacklist_token import BlacklistToken

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register/', methods=['POST'])
def register():
    # Verify all required fields are provided.
    if 'email' not in request.json:
        return make_response('No email provided!', 400, {'Content-Type': 'application/json'})
    if 'first_name' not in request.json:
        return make_response('No first name provided!', 400, {'Content-Type': 'application/json'})
    if 'last_name' not in request.json:
        return make_response('No last name provided!', 400, {'Content-Type': 'application/json'})
    if 'password' not in request.json:
        return make_response('No password provided!', 400, {'Content-Type': 'application/json'})

    # Verify email is unique and valid.
    email = request.json['email']
    if User.objects(email=email).count() != 0:
        return make_response('Email already registered!', 400, {'Content-Type': 'application/json'})
    elif not valid_email(email):
        return make_response('Email is invalid!', 400, {'Content-Type': 'application/json'})

    # Verify phone number (if provided) is unique and valid.
    if 'phone' in request.json:
        phone = request.json['phone']
        if User.objects(phone=phone).count() != 0:
            return make_response('Phone number already registered!', 400, {'Content-Type': 'application/json'})
        elif not valid_phone(phone):
            return make_response('Phone number is invalid!', 400, {'Content-Type': 'application/json'})

    # Verify provided password is valid and hash it.
    password = request.json['password']
    if not valid_password(password):
        return make_response('Password is invalid!', 400, {'Content-Type': 'application/json'})
    hash = generate_password_hash(password)

    # Create the user
    newuser = User(
    email = email,
    first_name = request.json['first_name'],
    last_name = request.json['last_name'],
    hash = hash
    )

    # Add optional parameters
    optional_params = getOptionalUserParams()
    for param in optional_params:
        if param in request.json:
            newuser[param] = request.json[param]
    newuser.save()

    # Generate auth auth token
    try:
        auth_token = newuser.encodeAuthToken()
        responseObject = {
            'status': 'success',
            'message': 'Successfully registered.',
            'auth_token': auth_token.decode()
        }
    except Exception as e:
        return make_response('Could not create token.', 401, {'Content-Type': 'application/json'})


    return make_response(jsonify(responseObject), 201, {'Content-Type': 'application/json'})

@auth_bp.route('/login/', methods=['POST'])
def login():
    # Verify all required fields are provided.
    if 'email' not in request.json:
        return make_response('No email provided!', 400, {'Content-Type': 'application/json'})
    if 'password' not in request.json:
        return make_response('No password provided!', 400, {'Content-Type': 'application/json'})

    # Verify user exists.
    email = request.json['email']
    user = User.objects(email=email).first()
    if user == None:
        return make_response('User does not exist.', 404, {'Content-Type': 'application/json'})

    # Verify the p
    password = request.json['password']
    if check_password_hash(user.hash, password):
        # Generate auth token
        try:
            auth_token = user.encodeAuthToken()
            responseObject = {
                'status': 'success',
                'message': 'Successfully logged in.',
                'auth_token': auth_token.decode()
            }
        except Exception as e:
            return make_response('Could not create token.', 401, {'Content-Type': 'application/json'})

        return make_response(jsonify(responseObject)), 200
    else:
        return make_response('Could not verify!', 401, {'WWW-Authenticate' : 'Basic realm="Login Required"'})


# @auth_bp.before_app_request
# def load_logged_in_user():
#     user_id = session.get('user_id')
#
#     if user_id is None:
#         g.user = None
#     else:
#         g.user = get_db().execute(
#             'SELECT * FROM user WHERE id = ?', (user_id,)
#         ).fetchone()

@auth_bp.route('/verify_login/', methods=['GET'])
def verify_login():
    auth = request.headers.get('Authorization')
    if auth:
        auth_token = auth.split(" ")[1]
    else:
        return make_response('No auth token provided!', 401, {'WWW-Authenticate' : 'Basic realm="Login Required"'})

    success, message = User.decode_auth_token(auth_token)
    if success:
        print(message)
        user, err = verify_user(message)
        if user == None:
            return make_response('User does not exist.', 404, {'Content-Type': 'application/json'})
        responseObject = {
            'status': 'success',
            'data': {
                'user_id': str(user.id),
                'email': user.email
            }
        }
        return make_response(jsonify(responseObject)), 200
    else:
        return make_response(err, 401, {'WWW-Authenticate' : 'Basic realm="Login Required"'})

@auth_bp.route('/logout/', methods=['POST'])
def logout():
    auth = request.headers.get('Authorization')
    if auth:
        auth_token = auth.split(" ")[1]
    else:
        return make_response('No auth token provided!', 401, {'WWW-Authenticate' : 'Basic realm="Login Required"'})

    success, err = User.decode_auth_token(auth_token)
    if success:
        try:
            # Add the token to the blacklist.
            blacklist_token = BlacklistToken(token=auth_token)
            blacklist_token.save()
            return make_response("User logged out succesfully.", 200, {'Content-Type': 'application/json'})
        except Exception as e:
            responseObject = {
                'status': 'fail',
                'message': e
            }
            return make_response(jsonify(responseObject), 200)
    else:
        return make_response(err, 401, {'WWW-Authenticate' : 'Basic realm="Login Required"'})

def login_required(f):
    @functools.wraps(f)
    def verify_login_wrapper(*args, **kwargs):
        auth = request.headers.get('Authorization')
        if auth:
            auth_token = auth.split(" ")[1]
        else:
            return make_response('No auth token provided!', 401, {'WWW-Authenticate' : 'Basic realm="Login Required"'})

        success, message = User.decode_auth_token(auth_token)
        if success:
            user, err = verify_user(message)
            if user == None:
                return make_response(err, 404, {'Content-Type': 'application/json'})
            else:
                return f(*args, **kwargs)
        else:
            return make_response(message, 401, {'WWW-Authenticate' : 'Basic realm="Login Required"'})

    return verify_login_wrapper

####################################
# TODO - TODO -TODO Auxiliary functions
####################################
def verify_user(uid):
    if uid is None:
        err = {'message': 'No user ID Provided', 'status_code': 400}
        return None, err

    user = User.objects(pk=uid).first()
    if user is None:
        err = {'message': 'This user does not exist', 'status_code': 404}
        return None, err

    return user, None

def valid_email(email):
    return True

def valid_phone(phone):
    return True

def valid_password(password):
    return True