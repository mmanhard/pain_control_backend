from flask import current_app, Blueprint, request, make_response
from werkzeug.security import check_password_hash, generate_password_hash
from mongoengine import *
import json

from ..models.user import User
from .auth import login_required, valid_password

users_bp = Blueprint('users', __name__, url_prefix='/users')


###########################################################################
# Read info about a specific user
###########################################################################
@users_bp.route('/<uid>/', methods=['GET'])
@login_required
def get_user(uid, user):
    detail_level = 'high'
    if 'detail_level' in request.args:
        detail_level = request.args['detail_level']

    responseObject = {
        'user_info': user.serialize(detail_level=detail_level)
    }
    return make_response(responseObject, 200)

##########################################################################
# Update user info
###########################################################################
@users_bp.route('/<uid>/', methods=['PATCH'])
@login_required
def modify_user(uid, user):
    # Check to see if request contains changes to unsupport fields.
    if 'email' in request.json:
        return make_response({'message': 'Changes to email not supported'}, 400)
    if 'hash' in request.json:
        return make_response({'message': 'Changes to hash not supported'}, 400)
    if 'password' in request.json:
        return make_response({'message': 'Changes to password not currently supported'}, 400)
    if 'entries' in request.json:
        return make_response({'message': 'Changes to entries directly is not supported'}, 400)
    if 'body_parts' in request.json:
        return make_response({'message': 'Changes to body parts directly is not supported'}, 400)

    for (key, value) in request.json.items():
        try:
            old_value = getattr(user, key)
            if old_value != value:
                setattr(user, key, value)
        except AttributeError:
            pass

    user.save()
    return make_response({'message': 'User edited succesfully'}, 200)

##########################################################################
# Update user password
###########################################################################
@users_bp.route('/<uid>/change_password/', methods=['PATCH'])
@login_required
def change_user_password(uid, user):
    # Verify all required fields are provided.
    if 'old_password' not in request.json:
        return make_response({'message': 'No old password provided!'}, 400)
    if 'new_password' not in request.json:
        return make_response({'message': 'No new password provided!'}, 400)

    # Verify the old password first then edit it.
    old_password = request.json['old_password']
    if check_password_hash(user.hash, old_password):
        # Verify new password is valid and hash it.
        new_password = request.json['new_password']
        if not valid_password(new_password):
            return make_response({'message': 'New password is invalid!'}, 400)
        hash = generate_password_hash(new_password)

        # Save the new password hash.
        user.hash = hash
        user.save()

        # Generate auth token and send response.
        try:
            auth_token = user.encodeAuthToken()
            responseObject = {
                'message': 'Successfully changed password.',
                'auth_token': auth_token.decode()
            }
            return make_response(responseObject, 200)
        except Exception as e:
            return make_response({'message': 'Could not create token.'}, 401)
    else:
        return make_response({'message': 'Could not verify old password!'}, 401)

###########################################################################
# Delete user
###########################################################################
@users_bp.route('/<uid>', methods=['DELETE'])
@login_required
def delete_user(uid, user):
    user.delete()

    return make_response({'message': 'User successfully deleted'}, 200)