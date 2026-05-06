"""
Flask Documentation:     https://flask.palletsprojects.com/
Jinja2 Documentation:    https://jinja.palletsprojects.com/
Werkzeug Documentation:  https://werkzeug.palletsprojects.com/
This file creates your application.
"""
from datetime import datetime, timezone

from app import app
from flask import render_template, request, jsonify, send_file, current_app, g
import os
from app import db, app
from app.models import User

###
# Routing for your application.
###

@app.route('/')
def index():
    return jsonify(message="This is the beginning of our API")


# ============================================================
# Like / Dislike / Pass / Matching
# ============================================================

@app.route('/api/profiles/<int:target_user_id>/like', methods=['POST'])
@token_required
def like_or_dislike_or_pass(target_user_id):
    """Like or dislike or pass on a profile. Creates a Match if mutual."""
    me = g.current_user

    if me.id == target_user_id:
        return jsonify({'error': 'You cannot like your own profile.'}), 400

    target = db.session.get(User, target_user_id)
    if not target:
        return jsonify({'error': 'User not found.'}), 404

    data = request.get_json(silent=True) or request.form
    action = (data.get('action') or 'like').lower()
    if action not in ('like', 'dislike', 'pass'):
        return jsonify({'error': "action must be 'like', 'dislike', or 'pass'."}), 400

    # Upsert like record
    existing = Like.query.filter_by(liker_id=me.id, liked_id=target_user_id).first()
    if existing:
        existing.action = action
        existing.created_at = datetime.now(timezone.utc)
    else:
        existing = Like(liker_id=me.id, liked_id=target_user_id, action=action)
        db.session.add(existing)

    match_created = False
    match_obj = None

    # Mutual match Check
    if action == 'like':
        reverse = Like.query.filter_by(
            liker_id=target_user_id, liked_id=me.id, action='like'
        ).first()
        if reverse:
            # Ensure canonical order (smaller id first) to avoid duplicates
            u1, u2 = (me.id, target_user_id) if me.id < target_user_id \
                     else (target_user_id, me.id)
            match_obj = Match.query.filter_by(user1_id=u1, user2_id=u2).first()
            if not match_obj:
                match_obj = Match(user1_id=u1, user2_id=u2)
                db.session.add(match_obj)
                match_created = True

    db.session.commit()

    response = {
        'message': f"Action '{action}' recorded.",
        'action': action,
        'match': match_obj.to_dict(me.id) if match_obj else None,
        'is_new_match': match_created,
    }
    return jsonify(response), 200


@app.route('/api/matches', methods=['GET'])
@token_required
def get_matches():
    """Return all mutual matches for the current user."""
    me = g.current_user
    matches = Match.query.filter(
        db.or_(Match.user1_id == me.id, Match.user2_id == me.id)
    ).order_by(Match.created_at.desc()).all()

    return jsonify({
        'matches': [m.to_dict(me.id) for m in matches],
        'total': len(matches),
    }), 200


# ============================================================
# Bookmarking
# ============================================================
@app.route('/api/bookmarks', methods=['GET'])
@token_required
def get_bookmarks():
    """List bookmarked profiles."""
    me = g.current_user
    bookmarks = Bookmark.query.filter_by(user_id=me.id) \
                         .order_by(Bookmark.created_at.desc()).all()
    return jsonify({
        'bookmarks': [bookmark.profile.to_dict() for bookmark in bookmarks],
        'total': len(favs),
    }), 200


@app.route('/api/bookmarks/<int:profile_id>', methods=['POST'])
@token_required
def add_bookmark(profile_id):
    """Bookmark a profile."""
    me = g.current_user
    profile = db.session.get(Profile, profile_id)
    if not profile:
        return jsonify({'error': 'Profile not found.'}), 404

    existing = Bookmark.query.filter_by(user_id=me.id, profile_id=profile_id).first()
    if existing:
        return jsonify({'message': 'Already bookmarked.'}), 200

    fav = Bookmark(user_id=me.id, profile_id=profile_id)
    db.session.add(fav)
    db.session.commit()
    return jsonify({'message': 'Added to bookmarks.'}), 201


@app.route('/api/bookmarks/<int:profile_id>', methods=['DELETE'])
@token_required
def remove_bookmark(profile_id):
    """Remove a bookmarked profile."""
    me = g.current_user
    bookmark = Bookmark.query.filter_by(user_id=me.id, profile_id=profile_id).first()
    if not bookmark:
        return jsonify({'error': 'Not in bookmarks.'}), 404

    db.session.delete(bookmark)
    db.session.commit()
    return jsonify({'message': 'Removed from bookmarks.'}), 200


# ============================================================
# Interests
# ============================================================
@app.route('/api/interests', methods=['GET'])
def get_interests():
    """Return all available interests."""
    interests = Interest.query.order_by(Interest.name).all()
    return jsonify({'interests': [i.to_dict() for i in interests]}), 200

# ============================================================
# Report & Block  (Optional Feature #1)
# ============================================================

@app.route('/api/users/<int:target_id>/report', methods=['POST'])
@token_required
def report_user(target_id):
    """Report another user for moderation review."""
    me = g.current_user
    if me.id == target_id:
        return jsonify({'error': 'Cannot report yourself.'}), 400

    target = db.session.get(User, target_id)
    if not target:
        return jsonify({'error': 'User not found.'}), 404

    data   = request.get_json(silent=True) or request.form
    reason  = (data.get('reason') or '').strip()
    details = (data.get('details') or '').strip()

    if reason not in ('spam', 'harassment', 'fake', 'inappropriate', 'other'):
        return jsonify({'error': "reason must be one of: spam, harassment, fake, inappropriate, other"}), 400

    existing = Report.query.filter_by(reporter_id=me.id, reported_id=target_id).first()
    if existing:
        return jsonify({'message': 'Already reported.'}), 200

    report = Report(reporter_id=me.id, reported_id=target_id,
                    reason=reason, details=details)
    db.session.add(report)
    db.session.commit()
    return jsonify({'message': 'Report submitted. Our team will review it.'}), 201


@app.route('/api/users/<int:target_id>/block', methods=['POST'])
@token_required
def block_user(target_id):
    """Block a user"""
    me = g.current_user
    if me.id == target_id:
        return jsonify({'error': 'Cannot self-block.'}), 400

    existing = Block.query.filter_by(blocker_id=me.id, blocked_id=target_id).first()
    if existing:
        return jsonify({'message': 'Already blocked this user.'}), 200

    block = Block(blocker_id=me.id, blocked_id=target_id)
    db.session.add(block)
    db.session.commit()
    return jsonify({'message': 'User blocked.'}), 201


@app.route('/api/users/<int:target_id>/unblock', methods=['DELETE'])
@token_required
def unblock_user(target_id):
    """Unblock a previously blocked user."""
    me = g.current_user
    block = Block.query.filter_by(blocker_id=me.id, blocked_id=target_id).first()
    if not block:
        return jsonify({'error': 'User was not blocked.'}), 404
    db.session.delete(block)
    db.session.commit()
    return jsonify({'message': 'User unblocked.'}), 200


@app.route('/api/blocks', methods=['GET'])
@token_required
def get_blocks():
    """List all users you have blocked."""
    me     = g.current_user
    blocks = Block.query.filter_by(blocker_id=me.id).all()
    return jsonify({
        'blocked': [
            {'user_id': b.blocked_id,
             'username': b.blocked.username if b.blocked else None,
             'blocked_at': b.created_at.isoformat() if b.created_at else None}
            for b in blocks
        ]
    }), 200


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


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also tell the browser not to cache the rendered page. If we wanted
    to we could change max-age to 600 seconds which would be 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404