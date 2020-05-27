from flask import Blueprint, request, make_response
from mongoengine import *
import json

from .auth import login_required
from ..models.user import User
from ..models.body_part import BodyPart

body_parts_bp = Blueprint('body_parts', __name__, url_prefix='/users/<uid>/body_parts')

##########################################################################
# Get body part
###########################################################################
@body_parts_bp.route('/', methods=['GET'])
@login_required
def get_body_parts(uid, user):
    # Check entry id provided exists.
    body_parts = BodyPart.objects(user=user)
    if body_parts is None:
        return make_response('User has no body parts available.', 404)

    s = []
    for bp in body_parts:
        s.append(bp.serialize())
    responseObject = {
        'body_parts': s,
        'status': 'success',
    }
    return make_response(responseObject, 200)

##########################################################################
# Create new body part
###########################################################################
@body_parts_bp.route('/', methods=['POST'])
@login_required
def create_body_part(uid, user):
    print('hello')
    # Check all required fields are provided.
    if 'name' not in request.json:
        return make_response('No name provided!', 400)
    if 'type' not in request.json:
        return make_response('No type provided!', 400)
    if uid is None:
        return make_response('No user ID Provided', 400)

    # Create the body_part.
    new_part = BodyPart(
    name = request.json['name'],
    type = request.json['type'],
    user = user
    )
    new_part.save()
    user.update(push__body_parts=new_part)

    return make_response('Success', 201)

##########################################################################
# Get body part
###########################################################################
@body_parts_bp.route('/<bpid>/', methods=['GET'])
@login_required
def get_body_part(uid, bpid, user):
    # Check entry id provided exists.
    body_part = BodyPart.objects(pk=bpid).first()
    if body_part is None:
        return make_response('This body part does not exist', 404)

    return make_response(repr(body_part), 200)