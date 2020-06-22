from flask import Blueprint, request, make_response
from mongoengine import *
import json
import datetime

from .auth import login_required
from ..models.user import User
from ..models.body_part_stats import BodyPartStats
from ..models.body_part import BodyPart

from ..controllers.body_parts import BodyPartController

body_parts_bp = Blueprint('body_parts', __name__, url_prefix='/users/<uid>/body_parts')

##########################################################################
# Get body part
###########################################################################
@body_parts_bp.route('/', methods=['GET'])
@login_required
def get_body_parts(uid, user):

    start_date = None
    end_date = None

    if 'start_date' in request.args:
        start_date = request.args['start_date']
        start_date = datetime.datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%S.%f%z")

    if 'end_date' in request.args:
        end_date = request.args['end_date']
        end_date = datetime.datetime.strptime(end_date, "%Y-%m-%dT%H:%M:%S.%f%z")

    body_parts = []
    for body_part in user.body_parts:
        (body_part, pain_stats) = BodyPartController.getBodyPartByID(user, body_part.id, start_date, end_date)
        body_parts.append(body_part.serialize(pain_stats))

    responseObject = {
        'body_parts': body_parts,
    }
    return make_response(responseObject, 200)

##########################################################################
# Create new body part
###########################################################################
@body_parts_bp.route('/', methods=['POST'])
@login_required
def create_body_part(uid, user):
    # Check all required fields are provided.
    if 'name' not in request.json:
        return make_response({'message': 'No name provided!'}, 400)
    if 'type' not in request.json:
        return make_response({'message': 'No type provided!'}, 400)
    if uid is None:
        return make_response({'message': 'No user ID Provided'}, 400)

    # Create the body_part.
    new_part = BodyPart(
    name = request.json['name'],
    type = request.json['type'],
    user = user,
    )
    new_part.save()
    user.update(push__body_parts=new_part)

    # Add optional fields.
    if 'location' in request.json:
        new_part.location = request.json['location']
    if 'notes' in request.json:
        new_part.notes = request.json['notes']
    new_part.save()

    responseObject = {
        'message': 'Body part created successfully.',
        'body_part_info': str(new_part.id)
    }
    return make_response(responseObject, 201)

##########################################################################
# Get body part
###########################################################################
@body_parts_bp.route('/<bpid>/', methods=['GET'])
@login_required
def get_body_part(uid, bpid, user):
    start_date = None
    end_date = None
    time_of_day = None

    if 'start_date' in request.args:
        start_date = request.args['start_date']
        start_date = start_date[:len(start_date)-1]
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%dT%H:%M:%S.%f')

    if 'end_date' in request.args:
        end_date = request.args['end_date']
        end_date = end_date[:len(end_date)-1]
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%dT%H:%M:%S.%f')

    if 'time_of_day' in request.args:
        time_of_day = request.args['time_of_day']

    # Check entry id provided exists.
    (body_part, pain_stats) = BodyPartController.getBodyPartByID(user, bpid, start_date, end_date, time_of_day)
    if body_part is None:
        return make_response({'message': 'This body part does not exist'}, 404)

    responseObject = {
        'body_part_info': body_part.serialize(pain_stats)
    }
    return make_response(responseObject, 200)