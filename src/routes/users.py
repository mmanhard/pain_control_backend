from flask import Blueprint, request, redirect, session, jsonify, render_template, make_response

from .auth import login_required

bp = Blueprint('users', __name__, url_prefix='/users')

###########################################################################
# Read all users - NOT SUPPORTED
###########################################################################
@bp.route("/", methods=['GET'])
def index():
    return "No"

###########################################################################
# Create new user
###########################################################################
@bp.route("/", methods=['POST'])
def create_user():
    return "User could not be created"

###########################################################################
# Read info about a specific user
###########################################################################
@bp.route("/<uid>", methods=['GET'])
@login_required
def get_user(uid):
    return "User could not be found"

###########################################################################
# Update user info
###########################################################################
@bp.route("/<uid>", methods=['PATCH'])
@login_required
def modify_user(uid):
    return "User could not be found"

###########################################################################
# Delete user
###########################################################################
@bp.route("/<uid>", methods=['DELETE'])
@login_required
def delete_user(uid):
    return "User could not be found"
