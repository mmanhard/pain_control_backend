from flask import Blueprint, request, make_response
from werkzeug.security import check_password_hash, generate_password_hash
import functools
import jwt

from ..models.user import User
from ..models.blacklist_token import BlacklistToken

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register/', methods=['POST'])
def register():
    # Verify all required fields are provided.
    if 'email' not in request.json:
        return make_response({'message': 'No email provided!'}, 400)
    if 'first_name' not in request.json:
        return make_response({'message': 'No first name provided!'}, 400)
    if 'last_name' not in request.json:
        return make_response({'message': 'No last name provided!'}, 400)
    if 'password' not in request.json:
        return make_response({'message': 'No password provided!'}, 400)

    # Verify email is unique and valid.
    email = request.json['email']
    if User.objects(email=email).count() != 0:
        return make_response({'message': 'Email already registered!'}, 400)
    elif not valid_email(email):
        return make_response({'message': 'Email is invalid!'}, 400)

    # Verify phone number (if provided) is unique and valid.
    if 'phone' in request.json:
        phone = request.json['phone']
        if User.objects(phone=phone).count() != 0:
            return make_response({'message': 'Phone number already registered!'}, 400)
        elif not valid_phone(phone):
            return make_response({'message': 'Phone number is invalid!'}, 400)

    # Verify provided password is valid and hash it.
    password = request.json['password']
    if not valid_password(password):
        return make_response({'message': 'Password is invalid!'}, 400)
    hash = generate_password_hash(password)

    # Create the user
    newuser = User(
    email = email,
    first_name = request.json['first_name'],
    last_name = request.json['last_name'],
    hash = hash
    )

    # Add optional parameters
    optional_params = User.getOptionalUserParams()
    for param in optional_params:
        if param in request.json:
            newuser[param] = request.json[param]
    newuser.save()

    # Generate auth token
    try:
        auth_token = newuser.encodeAuthToken()
        responseObject = {
            'message': 'Successfully registered.',
            'user_info': {
                'id': str(newuser.id)
            },
            'auth_token': auth_token.decode()
        }
        return make_response(responseObject, 201)
    except Exception as e:
        return make_response({'message': 'Could not create token.'}, 401)

@auth_bp.route('/login/', methods=['POST'])
def login():
    # Verify all required fields are provided.
    if 'email' not in request.json:
        return make_response({'message': 'No email provided!'}, 400)
    if 'password' not in request.json:
        return make_response({'message': 'No password provided!'}, 400)

    # Verify user exists.
    email = request.json['email']
    user = User.objects(email=email).first()
    if user == None:
        return make_response({'message': 'User does not exist.'}, 404)

    # Verify the password then create a token
    password = request.json['password']
    if check_password_hash(user.hash, password):
        # Generate auth token
        try:
            auth_token = user.encodeAuthToken()
            responseObject = {
                'message': 'Successfully logged in.',
                'user_info': {
                    'id': str(user.id)
                },
                'auth_token': auth_token.decode()
            }
            response = make_response(responseObject, 200)
            response.set_cookie('test', 'wow this worked!',domain="mypaincontroller.com")
            return response
        except Exception as e:
            return make_response({'message': 'Could not create token.'}, 401)
    else:
        return make_response({'message': 'Could not verify!'}, 401)

@auth_bp.route('/logout/', methods=['POST'])
def logout():
    auth = request.headers.get('Authorization')
    if auth:
        auth_token = auth.split(' ')[1]
    else:
        return make_response({'message': 'No auth token provided!'}, 401)

    success, err = User.decode_auth_token(auth_token)
    if success:
        try:
            # Add the token to the blacklist.
            blacklist_token = BlacklistToken(token=auth_token)
            blacklist_token.save()
            return make_response({'message': 'User logged out succesfully.'}, 200)
        except Exception as e:
            return make_response({'message': e}, 200)
    else:
        return make_response({'message': err}, 401)

def login_required(f):
    @functools.wraps(f)
    def verify_login_wrapper(*args, **kwargs):
        auth = request.headers.get('Authorization')
        if auth:
            auth_token = auth.split(' ')[1]
        else:
            return make_response({'message': 'No auth token provided!'}, 401)

        success, message = User.decode_auth_token(auth_token)
        if success:
            if 'uid' not in kwargs or kwargs['uid'] != message:
                return make_response({'message': 'Access forbidden'}, 403)

            user, err = verify_user(message)
            if err is not None:
                return make_response({'message': err['message']}, err['status_code'])
            else:
                return f(*args, user=user, **kwargs)
        else:
            return make_response({'message': message}, 401)

    return verify_login_wrapper

####################################
# TODO - TODO -TODO Auxiliary functions
####################################
def verify_user(uid):
    if uid is None:
        err = {'message': 'No user ID Provided', 'status_code': 400}
        return None, err

    user = User.objects(pk=uid).first()
    if user is None:
        err = {'message': 'This user does not exist', 'status_code': 404}
        return None, err

    return user, None

def valid_email(email):
    return True

def valid_phone(phone):
    return True

def valid_password(password):
    return True