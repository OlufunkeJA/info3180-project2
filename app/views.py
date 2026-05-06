"""
Flask Documentation:     https://flask.palletsprojects.com/
Jinja2 Documentation:    https://jinja.palletsprojects.com/
Werkzeug Documentation:  https://werkzeug.palletsprojects.com/
This file creates your application.
"""

from functools import wraps

from app import app, db
from app.models import User, Profile, Interest, profile_interests, Match, Message
from app.forms import RegistrationForm, LoginForm, ProfileForm

from flask import render_template, request, jsonify, send_file, session
import os
import cloudinary
import cloudinary.uploader
import uuid

###
# Routing for your application.
###

@app.route('/')
def index():
    return jsonify(message="This is the beginning of our API")


###
# Authentication helper functions.
###

def current_user():
    """Returns the currently logged-in user using session."""
    user_id = session.get('user_id')

    if not user_id:
        return None

    return db.session.get(User, user_id)


def login_required(route_function):
    """Decorator to protect routes that require a logged-in user."""

    @wraps(route_function)
    def wrapper(*args, **kwargs):
        user = current_user()

        if not user:
            return jsonify(error="Authentication required."), 401

        return route_function(*args, **kwargs)

    return wrapper
def allowed_file(filename):
    """Check if uploaded profile picture has an allowed extension."""
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in app.config["ALLOWED_EXTENSIONS"]
    )


def upload_profile_picture(file, user_id):
    """Upload profile picture to Cloudinary if configured, otherwise save locally."""

    if not file or not file.filename:
        return None

    if not allowed_file(file.filename):
        return None

    if app.config.get("CLOUDINARY_CLOUD_NAME"):
        upload_result = cloudinary.uploader.upload(
            file,
            folder="driftdater/profile_pictures",
            public_id=f"user_{user_id}",
            overwrite=True,
            resource_type="image"
        )

        return upload_result.get("secure_url")

    extension = file.filename.rsplit(".", 1)[1].lower()
    filename = f"user_{user_id}_{uuid.uuid4().hex}.{extension}"

    upload_folder = app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_folder, exist_ok=True)

    file.save(os.path.join(upload_folder, filename))

    return filename


def get_or_create_interests(interests_raw):
    """Convert comma-separated interests into Interest objects."""

    if not interests_raw:
        return []

    if isinstance(interests_raw, list):
        interest_names = interests_raw
    else:
        interest_names = interests_raw.split(",")

    interests = []

    for name in interest_names:
        clean_name = name.strip().lower()

        if clean_name:
            interest = Interest.query.filter_by(name=clean_name).first()

            if not interest:
                interest = Interest(name=clean_name)
                db.session.add(interest)

            interests.append(interest)

    return interests


def form_boolean(value):
    """Convert form/select value into a Python boolean."""
    return str(value).lower() in ["true", "1", "yes", "on"]

###
# Authentication routes.
###

@app.route('/api/register', methods=['POST'])
def register():
    """Register a new user."""
    data = request.get_json() or {}

    form = RegistrationForm(data=data)

    if not form.validate():
        return jsonify(errors=form_errors(form)), 400

    user = User(
        username=form.username.data.strip(),
        email=form.email.data.lower().strip()
    )

    user.set_password(form.password.data)
    try: 
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify(error="Registration failed."), 500
    

    session['user_id'] = user.id
    session.permanent = True

    return jsonify(
        message="User registered successfully.",
        user=user.to_dict()
    ), 201


@app.route('/api/login', methods=['POST'])
def login():
    """Login an existing user."""
    data = request.get_json() or {}

    form = LoginForm(data=data)

    if not form.validate():
        return jsonify(errors=form_errors(form)), 400

    email = form.email.data.lower().strip()
    password = form.password.data

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify(error="Invalid email or password."), 401

    session['user_id'] = user.id
    session.permanent = True

    return jsonify(
        message="Login successful.",
        user=user.to_dict()
    ), 200

@app.route('/api/profile', methods=['POST'])
@login_required
def create_profile():
    """Create a profile for the logged-in user."""
    user = current_user()

    existing_profile = Profile.query.filter_by(user_id=user.id).first()

    if existing_profile:
        return jsonify(error="Profile already exists."), 409

    data = request.form if request.form else request.get_json() or {}

    form = ProfileForm(data=data)

    if not form.validate():
        return jsonify(errors=form_errors(form)), 400

    interests_raw = data.get("interests")

    interests = get_or_create_interests(interests_raw)

    if len(interests) < 3:
        return jsonify(error="Please provide at least 3 interests."), 400

    profile_picture = None

    if "profile_picture" in request.files:
        profile_picture = upload_profile_picture(
            request.files["profile_picture"],
            user.id
        )

    profile = Profile(
        user_id=user.id,
        first_name=form.first_name.data.strip(),
        last_name=form.last_name.data.strip(),
        date_of_birth=form.date_of_birth.data,
        bio=form.bio.data,
        gender=form.gender.data,
        looking_for=form.looking_for.data,
        parish=form.parish.data,
        city=form.city.data,
        country=form.country.data or "Jamaica",
        occupation=form.occupation.data,
        education=form.education.data,
        minimum_age=form.minimum_age.data or 18,
        maximum_age=form.maximum_age.data or 99,
        pfp_accepted=profile_picture,
        is_pub=form_boolean(form.is_pub.data)
    )

    profile.interests = interests

    try:
        db.session.add(profile)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify(error="Profile creation failed."), 500

    return jsonify(
        message="Profile created successfully.",
        profile=profile.to_dict()
    ), 201

@app.route('/api/interests', methods=['GET'])
def get_interests():
    """Get all available interests."""
    interests = Interest.query.order_by(Interest.name).all()

    return jsonify(
        interests=[interest.to_dict() for interest in interests]
    ), 200

@app.route('/api/logout', methods=['POST'])
@login_required
def logout():
    """Logout the current user."""
    session.clear()

    return jsonify(message="Logout successful."), 200


@app.route('/api/session', methods=['GET'])
def check_session():
    """Check if a user is currently logged in."""
    user = current_user()

    if not user:
        return jsonify(
            authenticated=False,
            user=None
        ), 200

    return jsonify(
        authenticated=True,
        user=user.to_dict()
    ), 200


@app.route('/api/settings/theme', methods=['PUT'])
@login_required
def update_theme():
    """Update the user's theme preference."""
    user = current_user()
    data = request.get_json() or {}

    theme = data.get('theme')

    if theme not in ['light', 'dark', 'system']:
        return jsonify(error="Theme must be light, dark, or system."), 400

    user.theme = theme
    db.session.commit()

    return jsonify(
        message="Theme updated successfully.",
        user=user.to_dict()
    ), 200


###
# The functions below should be applicable to all Flask apps.
###

# Here we define a function to collect form errors from Flask-WTF
# which we can later use
def form_errors(form):
    error_messages = []
    """Collects form errors"""
    for field, errors in form.errors.items():
        for error in errors:
            message = u"Error in the %s field - %s" % (
                    getattr(form, field).label.text,
                    error
                )
            error_messages.append(message)

    return error_messages


@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)

###
# Profile management routes.
###

#@app.route('/api/profile', methods=['POST'])
#@login_required
#def create_profile():
#    """Create a profile for the logged-in user."""
#    user = current_user()
#
#    existing_profile = Profile.query.filter_by(user_id=user.id).first()
#
#    if existing_profile:
#        return jsonify(error="Profile already exists."), 409
#
#    data = request.form if request.form else request.get_json() or {}
#
#    form = ProfileForm(data=data)
#
#    if not form.validate():
#        return jsonify(errors=form_errors(form)), 400
#
#    profile = Profile(
#        user_id=user.id,
#        first_name=form.first_name.data.strip(),
#        last_name=form.last_name.data.strip(),
#        date_of_birth=form.date_of_birth.data,
#        bio=form.bio.data,
#        gender=form.gender.data,
#        looking_for=form.looking_for.data,
#        parish=form.parish.data,
#        city=form.city.data,
#        country=form.country.data or "Jamaica",
#        occupation=form.occupation.data,
#        education=form.education.data,
#        minimum_age=form.minimum_age.data or 18,
#        maximum_age=form.maximum_age.data or 99,
#        is_pub=form.is_pub.data
#    )
#
#    db.session.add(profile)
#    db.session.commit()
#
#    return jsonify(
#        message="Profile created successfully.",
#        profile=profile.to_dict()
#    ), 201


@app.route('/api/profile', methods=['GET'])
@login_required
def get_my_profile():
    """Get the logged-in user's profile."""
    user = current_user()

    profile = Profile.query.filter_by(user_id=user.id).first()

    if not profile:
        return jsonify(error="Profile not found."), 404

    return jsonify(profile=profile.to_dict()), 200


@app.route('/api/profile', methods=['PUT'])
@login_required
def update_my_profile():
    """Update the logged-in user's profile."""
    user = current_user()

    profile = Profile.query.filter_by(user_id=user.id).first()

    if not profile:
        return jsonify(error="Profile not found."), 404

    data = request.form if request.form else request.get_json() or {}

    form = ProfileForm(data=data)

    if not form.validate():
        return jsonify(errors=form_errors(form)), 400

    interests_raw = data.get("interests")

    if interests_raw is not None:
        interests = get_or_create_interests(interests_raw)

        if len(interests) < 3:
            return jsonify(error="Please provide at least 3 interests."), 400

        profile.interests = interests

    if "profile_picture" in request.files:
        uploaded_picture = upload_profile_picture(
            request.files["profile_picture"],
            user.id
        )

        if uploaded_picture:
            profile.pfp_accepted = uploaded_picture

    profile.first_name = form.first_name.data.strip()
    profile.last_name = form.last_name.data.strip()
    profile.date_of_birth = form.date_of_birth.data
    profile.bio = form.bio.data
    profile.gender = form.gender.data
    profile.looking_for = form.looking_for.data
    profile.parish = form.parish.data
    profile.city = form.city.data
    profile.country = form.country.data or "Jamaica"
    profile.occupation = form.occupation.data
    profile.education = form.education.data
    profile.minimum_age = form.minimum_age.data or 18
    profile.maximum_age = form.maximum_age.data or 99
    profile.is_pub = form_boolean(form.is_pub.data)

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify(error="Profile update failed."), 500

    return jsonify(
        message="Profile updated successfully.",
        profile=profile.to_dict()
    ), 200


@app.route('/api/profiles', methods=['GET'])
@login_required
def get_profiles():
    """Get all public profiles except the logged-in user's profile."""
    user = current_user()

    profiles = Profile.query.filter(
        Profile.user_id != user.id,
        Profile.is_pub == True
    ).all()

    return jsonify(
        profiles=[profile.to_dict() for profile in profiles]
    ), 200


@app.route('/api/profiles/<int:profile_id>', methods=['GET'])
@login_required
def get_profile(profile_id):
    """Get a single public profile."""
    profile = db.session.get(Profile, profile_id)

    if not profile:
        return jsonify(error="Profile not found."), 404

    if not profile.is_pub and profile.user_id != current_user().id:
        return jsonify(error="This profile is private."), 403

    return jsonify(profile=profile.to_dict()), 200

###
# Message routes.
###

@app.route('/api/conversations', methods=['GET'])
@login_required
def get_conversations():
    """Get all conversations for the logged-in user."""
    user = current_user()

    matches = Match.query.filter(
        db.or_(
            Match.user1_id == user.id,
            Match.user2_id == user.id
        )
    ).order_by(Match.created_at.desc()).all()

    conversations = []

    for match in matches:
        latest_message = Message.query.filter_by(
            match_id=match.id
        ).order_by(
            Message.created_at.desc()
        ).first()

        other_user = match.other_user(user.id)

        conversations.append({
            "match": match.to_dict(user.id),
            "other_user": other_user.to_dict() if other_user else None,
            "other_profile": other_user.profile.to_dict() if other_user and other_user.profile else None,
            "latest_message": latest_message.to_dict() if latest_message else None
        })

    return jsonify(conversations=conversations), 200


@app.route('/api/matches/<int:match_id>/messages', methods=['GET'])
@login_required
def get_messages(match_id):
    """Get message history for a match."""
    user = current_user()

    match = db.session.get(Match, match_id)

    if not match:
        return jsonify(error="Match not found."), 404

    if user.id not in [match.user1_id, match.user2_id]:
        return jsonify(error="You are not part of this match."), 403

    messages = Message.query.filter_by(
        match_id=match.id
    ).order_by(
        Message.created_at.asc()
    ).all()

    for message in messages:
        if message.sender_id != user.id:
            message.is_read = True

    db.session.commit()

    return jsonify(
        match=match.to_dict(user.id),
        messages=[message.to_dict() for message in messages]
    ), 200


@app.route('/api/matches/<int:match_id>/messages', methods=['POST'])
@login_required
def send_message(match_id):
    """Send a message to a matched user."""
    user = current_user()

    match = db.session.get(Match, match_id)

    if not match:
        return jsonify(error="Match not found."), 404

    if user.id not in [match.user1_id, match.user2_id]:
        return jsonify(error="You are not part of this match."), 403

    data = request.get_json() or {}

    form = MessageForm(data=data)

    if not form.validate():
        return jsonify(errors=form_errors(form)), 400

    message = Message(
        match_id=match.id,
        sender_id=user.id,
        body=form.body.data.strip()
    )

    try:
        db.session.add(message)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify(error="Message could not be sent."), 500

    return jsonify(
        message="Message sent successfully.",
        data=message.to_dict()
    ), 201


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also tell the browser not to cache the rendered page. If we wanted
    to we could change max-age to 600 seconds which would be 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'

    if request.method == 'GET':
        response.headers['Cache-Control'] = 'public, max-age=0'
    else:
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate'

    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return jsonify(error="Resource not found."), 404