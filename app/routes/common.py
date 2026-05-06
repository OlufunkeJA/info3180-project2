from functools import wraps
from datetime import datetime, timezone
import os
import uuid

from flask import Blueprint, current_app, jsonify, request, session

from app import db
from app.models import *
from app.forms import ChatMessageForm as MessageForm, RegistrationForm, LoginForm, ProfileForm

try:
    import cloudinary
    import cloudinary.uploader
except ImportError:  # pragma: no cover
    cloudinary = None


api_bp = Blueprint("api", __name__)


def current_account():
    """Returns the currently logged-in account using session."""
    account_id = session.get("account_id")

    if not account_id:
        return None

    return db.session.get(Account, account_id)


def login_required(route_function):
    """Decorator to protect routes that require a logged-in account."""

    @wraps(route_function)
    def wrapper(*args, **kwargs):
        account = current_account()

        if not account:
            return jsonify(error="Authentication required."), 401

        return route_function(*args, **kwargs)

    return wrapper


def allowed_file(filename):
    """Check if uploaded profile picture has an allowed extension."""
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in current_app.config["ALLOWED_EXTENSIONS"]
    )


def upload_profile_picture(file, account_id):
    """Upload profile picture to Cloudinary if configured, otherwise save locally."""

    if not file or not file.filename:
        return None

    if not allowed_file(file.filename):
        return None

    if current_app.config.get("CLOUDINARY_CLOUD_NAME") and cloudinary:
        upload_result = cloudinary.uploader.upload(
            file,
            folder="driftdater/profile_pictures",
            public_id=f"account_{account_id}",
            overwrite=True,
            resource_type="image",
        )

        return upload_result.get("secure_url")

    extension = file.filename.rsplit(".", 1)[1].lower()
    filename = f"account_{account_id}_{uuid.uuid4().hex}.{extension}"

    upload_folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_folder, exist_ok=True)

    file.save(os.path.join(upload_folder, filename))

    return filename


def get_or_create_interests(interests_raw):
    """Convert comma-separated interests into Likes objects."""

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
            interest = Likes.query.filter_by(name=clean_name).first()

            if not interest:
                interest = Likes(name=clean_name)
                db.session.add(interest)

            interests.append(interest)

    return interests


def form_boolean(value):
    """Convert form/select value into a Python boolean."""
    return str(value).lower() in ["true", "1", "yes", "on"]


def create_notification(account_id, title, message, notification_type):
    """Create an in-app notification for an account."""

    notification = Notification(
        account_id=account_id,
        title=title,
        message=message,
        notification_type=notification_type,
    )

    db.session.add(notification)

    return notification


def form_errors(form):
    """Collect form errors."""
    error_messages = []
    for field, errors in form.errors.items():
        for error in errors:
            message = "Error in the %s field - %s" % (getattr(form, field).label.text, error)
            error_messages.append(message)

    return error_messages
