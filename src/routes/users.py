from flask import current_app, Blueprint, request, redirect, session, jsonify, render_template, make_response
from werkzeug.security import generate_password_hash
from mongoengine import *
import json

from ..models.user import User, getOptionalUserParams
# from .auth import login_required

users_bp = Blueprint('users', __name__, url_prefix='/users')

###########################################################################
# Read all users - NOT SUPPORTED IN PRODUCTION
###########################################################################
@users_bp.route('/', methods=['GET'])
def index():
    detail_level = 'high'
    if 'detail_level' in request.args:
        detail_level = request.args['detail_level']
    all_users = User.objects()
    s = []
    for u in all_users:
        s.append(u.serialize(detail_level=detail_level))
    return make_response(json.dumps(s, indent=4), 200, {'Content-Type': 'application/json'})

##########################################################################
# Create new user - POST
# /users/
#
# Required body keys:
# email, first_name, last_name, password
#
# Optional body keys:
# phone, birthday, hometown, medical_history
#
###########################################################################
@users_bp.route('/', methods=['POST'])
def create_user():

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
    print(optional_params)
    for param in optional_params:
        print(param)
        if param in request.json:
            newuser[param] = request.json[param]

    newuser.save()
    return make_response("Success", 201, {'Content-Type': 'application/json'})

###########################################################################
# Read info about a specific user - GET
# /users/<user_id>
#
# Optional query parameters:
# detail_level = low, medium, high (default)
#
###########################################################################
@users_bp.route('/<uid>/', methods=['GET'])
# @login_required
def get_user(uid):
    user, err = verify_user(uid)
    if err is not None:
        return make_response(err['message'], err['status_code'], {'Content-Type': 'application/json'})

    detail_level = 'high'
    if 'detail_level' in request.args:
        detail_level = request.args['detail_level']

    return make_response(user.serialize(detail_level=detail_level), 200, {'Content-Type': 'application/json'})

##########################################################################
# Update user info
###########################################################################
@users_bp.route('/<uid>', methods=['PATCH'])
# @login_required
def modify_user(uid):
    user, err = verify_user(uid)
    if err is not None:
        return make_response(err['message'], err['status_code'], {'Content-Type': 'application/json'})

    # Check to see if request contains changes to unsupport fields.
    if 'email' in request.json:
        return make_response('Changes to email not supported', 400, {'Content-Type': 'application/json'})
    if 'phone' in request.json:
        return make_response('Changes to phone number not supported', 400, {'Content-Type': 'application/json'})
    if 'hash' in request.json:
        return make_response('Changes to hash not supported', 400, {'Content-Type': 'application/json'})
    if 'entries' in request.json:
        return make_response('Changes to entries directly is not supported', 400, {'Content-Type': 'application/json'})
    if 'body_parts' in request.json:
        return make_response('Changes to body parts directly is not supported', 400, {'Content-Type': 'application/json'})

    for (key, value) in request.json.items():
        if key in user and user[key] != value:
            user[key] = value
        elif key == 'password':
            if not valid_password(value):
                return make_response('Password is invalid!', 400, {'Content-Type': 'application/json'})
            user['hash'] = generate_password_hash(value)

    user.save()
    return make_response("User edited succesfully", 200, {'Content-Type': 'application/json'})

# ###########################################################################
# # Delete user
# ###########################################################################
@users_bp.route('/<uid>', methods=['DELETE'])
# @login_required
def delete_user(uid):
    user, err = verify_user(uid)
    if err is not None:
        return make_response(err['message'], err['status_code'], {'Content-Type': 'application/json'})

    user.delete()

    return make_response("User successfully deleted", 200, {'Content-Type': 'application/json'})


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