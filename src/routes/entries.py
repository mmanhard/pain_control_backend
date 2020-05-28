from flask import Blueprint, request, make_response
from mongoengine import *
import json

from .auth import login_required
from ..models.user import User
from ..models.subentry import SubEntry, MoodSubEntry
from ..models.entry import Entry

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
    if 'notes' not in request.form:
        return make_response({'message': 'No notes provided!'}, 400)
    if 'subentry_notes' not in request.form:
        return make_response({'message': 'No subentry notes provided!'}, 400)
    if uid is None:
        return make_response({'message': 'No user ID Provided'}, 400)

    # Create the pain subentry.
    # if 'body_'
    # body_part
    # # subentry = PainSubEntry(
    # notes = request.form['subentry_notes'],
    # mood = 'sad'
    # )

    # Create the entry and save a reference to it in the user db.
    new_entry = Entry(
    user = user,
    notes = request.form['notes']
    )
    new_entry.save()
    user.update(push__entries=new_entry)

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
        'entry_info': repr(entry)
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