from flask import current_app, Blueprint, request, make_response
from werkzeug.security import generate_password_hash
from mongoengine import *
import json

from ..models.user import User
from .auth import login_required, valid_password

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
    return make_response(json.dumps(s, indent=4), 200)

###########################################################################
# Read info about a specific user - GET
# /users/<user_id>
#
# Optional query parameters:
# detail_level = low, medium, high (default)
#
###########################################################################
@users_bp.route('/<uid>/', methods=['GET'])
@login_required
def get_user(uid, user):
    detail_level = 'high'
    if 'detail_level' in request.args:
        detail_level = request.args['detail_level']

    responseObject = {
        'user_info': user.serialize(detail_level=detail_level),
        'status': 'success',
    }
    return make_response(responseObject, 200)

##########################################################################
# Update user info
###########################################################################
@users_bp.route('/<uid>', methods=['PATCH'])
@login_required
def modify_user(uid, user):
    # Check to see if request contains changes to unsupport fields.
    if 'email' in request.json:
        return make_response('Changes to email not supported', 400)
    if 'phone' in request.json:
        return make_response('Changes to phone number not supported', 400)
    if 'hash' in request.json:
        return make_response('Changes to hash not supported', 400)
    if 'entries' in request.json:
        return make_response('Changes to entries directly is not supported', 400)
    if 'body_parts' in request.json:
        return make_response('Changes to body parts directly is not supported', 400)

    for (key, value) in request.json.items():
        if key in user and user[key] != value:
            user[key] = value
        elif key == 'password':
            if not valid_password(value):
                return make_response('Password is invalid!', 400)
            user['hash'] = generate_password_hash(value)

    user.save()
    return make_response('User edited succesfully', 200)

###########################################################################
# Delete user
###########################################################################
@users_bp.route('/<uid>', methods=['DELETE'])
@login_required
def delete_user(uid, user):
    user.delete()

    return make_response('User successfully deleted', 200)