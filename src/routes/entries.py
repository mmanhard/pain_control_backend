from flask import Blueprint, request, redirect, session, jsonify, render_template, make_response
from werkzeug.security import generate_password_hash
from mongoengine import *
import json

from ..models.entry import Entry
from ..models.user import User

bp = Blueprint('entries', __name__, url_prefix='/users/<uid>/entries')

###########################################################################
# Get all entries for a given user
###########################################################################
@bp.route('/', methods=['GET'])
def index(uid):
    all_entries = Entry.objects()
    s = []
    for e in all_entries:
        s.append(e.serialize())
    return make_response(json.dumps(s, sort_keys=True, indent=4),200)

##########################################################################
# Create new entry
###########################################################################
@bp.route('/', methods=['POST'])
def create_entry(uid):

    # Check all required fields are provided.
    if 'notes' not in request.form:
        return make_response('No notes provided!', 400)
    if uid is None:
        return make_response("No user ID Provided", 400)

    # Check user id provided exists.
    user = User.objects(pk=uid).first()
    if user is None:
        return make_response("This user does not exist", 404)

    # Create the entry and save a reference to it in the user db.
    newentry = Entry(
    user = user,
    notes = request.form['notes'],
    )
    newentry.save()
    user.update(push__entries=newentry)

    return make_response("Success", 201)

##########################################################################
# Get entry details
###########################################################################
@bp.route('/<eid>', methods=['GET'])
# @login_required
def get_user(uid, eid):
    # Check entry id provided exists.
    entry = Entry.objects(pk=eid).first()
    if entry is None:
        return make_response("This entry does not exist", 404)

    # Check user id provided exists.
    user = User.objects(pk=uid).first()
    if user is None:
        return make_response("This user does not exist", 404)

    return make_response(repr(entry), 200)

##########################################################################
# Delete entry
###########################################################################
@bp.route('/<eid>', methods=['DELETE'])
def delete_entry(uid,eid):
    # Check entry id provided exists.
    entry = Entry.objects(pk=eid).first()
    if entry is None:
        return make_response("This entry does not exist", 404)

    # Check user id provided exists.
    user = User.objects(pk=uid).first()
    if user is None:
        return make_response("This user does not exist", 404)

    entry.delete()

    return make_response("Entry successfully deleted", 200)