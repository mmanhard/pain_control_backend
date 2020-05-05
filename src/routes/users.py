from flask import Blueprint, request, redirect, session, jsonify, render_template, make_response
from werkzeug.security import generate_password_hash
from mongoengine import *
import json

from ..models.user import User, getOptionalUserParams
# from .auth import login_required

bp = Blueprint('users', __name__, url_prefix='/users')

###########################################################################
# Read all users - NOT SUPPORTED
###########################################################################
@bp.route('/', methods=['GET'])
def index():
    all_users = User.objects()
    s = []
    for u in all_users:
        s.append(u.serialize())
    return make_response(json.dumps(s, sort_keys=True, indent=4),200)

##########################################################################
# Create new user
###########################################################################
@bp.route('/', methods=['POST'])
def create_user():

    # Check all required fields are provided.
    if 'email' not in request.form:
        return make_response('No email provided!', 400)
    if 'first_name' not in request.form:
        return make_response('No first name provided!', 400)
    if 'last_name' not in request.form:
        return make_response('No last name provided!', 400)
    if 'password' not in request.form:
        return make_response('No password provided!', 400)

    # Check email and phone number (if provided) are unique.
    if User.objects(email=request.form['email']).count() != 0:
        return make_response('Email already registered!', 400)
    if 'phone' in request.form and User.objects(phone=request.form['phone']).count() != 0:
        return make_response('Phone number already registered!', 400)

    # Verify provided fields are valid.
    # if not valid_phone_number(cell):
    #     return make_response('Phone number is invalid!', 400)
    #
    # if not valid_username(username):
    #     return make_response('Username is invalid!', 400)


    # Create the user
    newuser = User(
    email = request.form['email'],
    first_name = request.form['first_name'],
    last_name = request.form['last_name'],
    hash = generate_password_hash(request.form['password'])
    )

    # Add optional parameters
    optional_params = getOptionalUserParams()
    print(optional_params)
    for param in optional_params:
        print(param)
        if param in request.form:
            newuser[param] = request.form[param]

    newuser.save()
    return make_response("Success", 201)

###########################################################################
# Read info about a specific user
###########################################################################
@bp.route('/<uid>', methods=['GET'])
# @login_required
def get_user(uid):
    if uid is None:
        return make_response("No user ID Provided", 400)

    user = User.objects(pk=uid).first()

    if user is None:
        return make_response("This user does not exist", 404)

    return make_response(repr(user), 200)

###########################################################################
# # Update user info
# ###########################################################################
# @bp.route('/<uid>', methods=['PATCH'])
# @login_required
# def modify_user(uid):
#     return 'User could not be found'
#
# ###########################################################################
# # Delete user
# ###########################################################################
# @bp.route('/<uid>', methods=['DELETE'])
# @login_required
# def delete_user(uid):
#     return 'User could not be found'
