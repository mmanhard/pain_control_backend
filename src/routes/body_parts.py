from flask import Blueprint, request, redirect, session, jsonify, render_template, make_response
from werkzeug.security import generate_password_hash
from mongoengine import *
import json

from .users import verify_user
from ..models.user import User
from ..models.body_part import BodyPart

body_parts_bp = Blueprint('body_parts', __name__, url_prefix='/users/<uid>/body_parts')

##########################################################################
# Create new body part
###########################################################################
@body_parts_bp.route('/', methods=['POST'])
def create_entry(uid):
    # Check all required fields are provided.
    if 'name' not in request.form:
        return make_response('No name provided!', 400, {'Content-Type': 'application/json'})
    if 'type' not in request.form:
        return make_response('No type provided!', 400, {'Content-Type': 'application/json'})
    if uid is None:
        return make_response("No user ID Provided", 400, {'Content-Type': 'application/json'})

    # Check user id provided exists.
    user, err = verify_user(uid)
    if err is not None:
        return make_response(err['message'], err['status_code'], {'Content-Type': 'application/json'})

    # Create the body_part.
    new_part = BodyPart(
    name = request.form['name'],
    type = request.form['type'],
    user = user,
    notes = request.form['notes']
    )
    new_part.save()
    user.update(push__body_parts=new_part)

    return make_response("Success", 201, {'Content-Type': 'application/json'})

##########################################################################
# Get body parts
###########################################################################
@body_parts_bp.route('/<bpid>/', methods=['GET'])
# @login_required
def get_user(uid, bpid):
    # Check entry id provided exists.
    body_part = BodyPart.objects(pk=bpid).first()
    if body_part is None:
        return make_response("This body part does not exist", 404, {'Content-Type': 'application/json'})

    # Check user id provided exists.
    user, err = verify_user(uid)
    if err is not None:
        return make_response(err['message'], err['status_code'], {'Content-Type': 'application/json'})

    return make_response(repr(body_part), 200, {'Content-Type': 'application/json'})