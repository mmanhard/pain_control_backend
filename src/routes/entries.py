from flask import Blueprint, request, make_response
from mongoengine import *
import json
import datetime
from dateutil.parser import isoparse


from .auth import login_required
from ..models.user import User
from ..models.subentry import SubEntry, PainSubEntry
from ..models.entry import Entry
from ..models.body_part import BodyPart

from ..controllers.entry import EntryController

entries_bp = Blueprint('entries', __name__, url_prefix='/users/<uid>/entries')

###########################################################################
# Get all entries for a given user
###########################################################################
@entries_bp.route('/', methods=['GET'])
@login_required
def get_entries(uid, user):

    start_date = None
    end_date = None
    time_of_day = None
    pain_point = None
    sort_by = None

    if 'start_date' in request.args:
        start_date = request.args['start_date']
        start_date = datetime.datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%S.%f%z")

    if 'end_date' in request.args:
        end_date = request.args['end_date']
        end_date = datetime.datetime.strptime(end_date, "%Y-%m-%dT%H:%M:%S.%f%z")

    if 'time_of_day' in request.args:
        time_of_day = request.args['time_of_day']

    if 'pain_point' in request.args:
        pain_point = request.args['pain_point']

    if 'sort_by' in request.args:
        sort_by = request.args['sort_by']

    entries = EntryController.getEntries(user, start_date, end_date, time_of_day, pain_point, sort_by)

    responseObject = {
        'entries': EntryController.serializeEntries(entries)
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
    pain_total = 0
    pain_min = 10
    pain_max = 0
    if 'pain_subentries' in request.json:
        for pain_data in request.json['pain_subentries']:
            pain_level = int(pain_data['pain_level'])
            bp = BodyPart.objects(pk=pain_data['id']).first()
            new_subentry = PainSubEntry(
                body_part = bp,
                pain_level = pain_level
            )

            pain_total += pain_level
            if pain_level < pain_min:
                pain_min = pain_level
            if pain_level > pain_max:
                pain_max = pain_level

            pain_subentries.append(new_subentry)

            bp.update(push__entries=new_entry)

    new_entry.pain_subentries = pain_subentries
    new_entry.create_stats(pain_max, pain_min, pain_total, len(pain_subentries))

    # Add date if included.
    if 'date' in request.json:
        date = request.json['date']
        date = datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%f%z")
        new_entry.date = date

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
    (entry, comparisons) = EntryController.getEntryByID(user, eid)
    if entry is None:
        return make_response({'message': 'This entry does not exist'}, 404)

    responseObject = {
        'entry_info': entry.serialize(comparisons)
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