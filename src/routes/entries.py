from flask import Blueprint, request, make_response
from mongoengine import *
import json

from .auth import login_required
from ..models.user import User
from ..models.subentry import SubEntry, PainSubEntry
from ..models.entry import Entry
from ..models.body_part import BodyPart

entries_bp = Blueprint('entries', __name__, url_prefix='/users/<uid>/entries')

###########################################################################
# Get all entries for a given user
###########################################################################
@entries_bp.route('/', methods=['GET'])
@login_required
def get_entries(uid, user):
    all_entries = Entry.objects()

    all_entries_serialized = []
    for entry in all_entries:
        all_entries_serialized.append(entry.serialize())
    responseObject = {
        'entries': all_entries_serialized
    }
    return make_response(responseObject, 200)

##########################################################################
# Create new entry
###########################################################################
@entries_bp.route('/', methods=['POST'])
@login_required
def create_entry(uid, user):

    # Check all required fields are provided.
    if uid is None:
        return make_response({'message': 'No user ID Provided'}, 400)

    # Create the entry and save a reference to it in the user db.
    new_entry = Entry(
    user = user
    )
    new_entry.save()
    user.update(push__entries=new_entry)

    # Create the pain subentries and update the corresponding body parts.
    pain_subentries = []
    if 'pain_subentries' in request.json:
        for pain_data in request.json['pain_subentries']:
            pain_level = int(pain_data['pain_level'])
            bp = BodyPart.objects(pk=pain_data['id']).first()
            new_subentry = PainSubEntry(
                body_part = bp,
                pain_level = pain_level
            )
            pain_subentries.append(new_subentry)

            bp.modifyBodyPartStats(pain_level)
            bp.update(push__entries=new_entry)
    new_entry.pain_subentries = pain_subentries

    # Add optional notes.
    if 'notes' in request.json:
        new_entry.notes = request.json['notes']

    new_entry.save()

    responseObject = {
        'message': 'Entry successfully created.',
        'entry_info': str(new_entry.id)
    }
    return make_response(responseObject, 201)

##########################################################################
# Get entry details
###########################################################################
@entries_bp.route('/<eid>/', methods=['GET'])
@login_required
def get_entry(uid, eid, user):
    # Check entry id provided exists.
    entry = Entry.objects(pk=eid).first()
    if entry is None:
        return make_response({'message': 'This entry does not exist'}, 404)

    responseObject = {
        'entry_info': entry.serialize()
    }
    return make_response(responseObject, 200)

##########################################################################
# Delete entry
###########################################################################
@entries_bp.route('/<eid>/', methods=['DELETE'])
@login_required
def delete_entry(uid, eid, user):
    # Check entry id provided exists.
    entry = Entry.objects(pk=eid).first()
    if entry is None:
        return make_response({'message': 'This entry does not exist'}, 404)

    entry.delete()

    return make_response({'message': 'Entry successfully deleted'}, 200)