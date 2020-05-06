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
# Read info about a specific user
###########################################################################
@users_bp.route('/<uid>/', methods=['GET'])
# @login_required
def get_user(uid):
    if uid is None:
        return make_response("No user ID Provided", 400, {'Content-Type': 'application/json'})

    user = User.objects(pk=uid).first()

    if user is None:
        return make_response("This user does not exist", 404, {'Content-Type': 'application/json'})

    return make_response(repr(user), 200, {'Content-Type': 'application/json'})

###########################################################################
# # Update user info
# ###########################################################################
# @users_bp.route('/<uid>', methods=['PATCH'])
# @login_required
# def modify_user(uid):
#     return 'User could not be found'
#
# ###########################################################################
# # Delete user
# ###########################################################################
@users_bp.route('/<uid>', methods=['DELETE'])
# @login_required
def delete_user(uid):
    # Check user id provided exists.
    user = User.objects(pk=uid).first()
    if user is None:
        return make_response("This user does not exist", 404, {'Content-Type': 'application/json'})

    user.delete()

    return make_response("User successfully deleted", 200, {'Content-Type': 'application/json'})


####################################
# TODO - TODO -TODO Auxiliary functions
####################################
def valid_email(email):
    return True

def valid_phone(phone):
    return True

def valid_password(password):
    return True