from flask import Blueprint, request, redirect, session, jsonify, render_template, make_response
from werkzeug.security import generate_password_hash
from mongoengine import *
import json

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
        return make_response('No name provided!', 400)
    if 'type' not in request.form:
        return make_response('No type provided!', 400)
    if uid is None:
        return make_response("No user ID Provided", 400)

    # Check user id provided exists.
    user = User.objects(pk=uid).first()
    if user is None:
        return make_response("This user does not exist", 404)

    # Create the body_part.
    new_part = BodyPart(
    name = request.form['name'],
    type = request.form['type'],
    user = user,
    notes = request.form['notes']
    )
    new_part.save()
    user.update(push__body_parts=new_part)

    return make_response("Success", 201)

##########################################################################
# Get body parts
###########################################################################
@body_parts_bp.route('/<bpid>/', methods=['GET'])
# @login_required
def get_user(uid, bpid):
    # Check entry id provided exists.
    body_part = BodyPart.objects(pk=bpid).first()
    if body_part is None:
        return make_response("This body part does not exist", 404)

    # Check user id provided exists.
    user = User.objects(pk=uid).first()
    if user is None:
        return make_response("This user does not exist", 404)

    return make_response(repr(body_part), 200)