from app.routes.common import *


@api_bp.route("/api/conversations", methods=["GET"])
@login_required
def get_conversations():
    account = current_account()

    connections = Connection.query.filter(
        db.or_(Connection.initiator_id == account.id, Connection.receiver_id == account.id)
    ).order_by(Connection.formed_at.desc()).all()

    conversations = []

    for connection in connections:
        latest_message = ChatMessage.query.filter_by(connection_id=connection.id).order_by(
            ChatMessage.sent_at.desc()
        ).first()

        other_account = connection.partner(account.id)

        conversations.append(
            {
                "connection": connection.serialise(account.id),
                "other_account": other_account.serialise() if other_account else None,
                "other_profile": other_account.member_profile.serialise() if other_account and other_account.member_profile else None,
                "latest_message": latest_message.serialise() if latest_message else None,
            }
        )

    return jsonify(conversations=conversations), 200


@api_bp.route("/api/connections/<int:connection_id>/messages", methods=["GET"])
@login_required
def get_messages(connection_id):
    account = current_account()

    connection = db.session.get(Connection, connection_id)
    if not connection:
        return jsonify(error="Connection not found."), 404

    if account.id not in [connection.initiator_id, connection.receiver_id]:
        return jsonify(error="You are not part of this connection."), 403

    messages = ChatMessage.query.filter_by(connection_id=connection.id).order_by(
        ChatMessage.sent_at.asc()
    ).all()

    return jsonify(
        connection=connection.serialise(account.id),
        messages=[message.serialise() for message in messages],
    ), 200


@api_bp.route("/api/connections/<int:connection_id>/messages", methods=["POST"])
@login_required
def send_message(connection_id):
    account = current_account()

    connection = db.session.get(Connection, connection_id)
    if not connection:
        return jsonify(error="Connection not found."), 404

    if account.id not in [connection.initiator_id, connection.receiver_id]:
        return jsonify(error="You are not part of this connection."), 403

    data = request.get_json() or {}

    form = MessageForm(data=data)
    if not form.validate():
        return jsonify(errors=form_errors(form)), 400

    message = ChatMessage(
        connection_id=connection.id,
        author_id=account.id,
        content=form.content.data.strip(),
    )

    other_account = connection.partner(account.id)
    create_notification(
        account_id=other_account.id,
        title="New message",
        message=f"{account.handle} sent you a message.",
        notification_type="message",
    )

    try:
        db.session.add(message)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify(error="Message could not be sent."), 500

    return jsonify(message="Message sent successfully.", data=message.serialise()), 201


@api_bp.route("/api/profiles/<int:target_account_id>/like", methods=["POST"])
@login_required
def like_or_dislike_or_pass(target_account_id):
    me = current_account()

    if me.id == target_account_id:
        return jsonify({"error": "You cannot like your own profile."}), 400

    target = db.session.get(Account, target_account_id)
    if not target:
        return jsonify({"error": "Account not found."}), 404

    data = request.get_json(silent=True) or request.form
    action = (data.get("action") or "like").lower()
    verdict_map = {"like": "yes", "dislike": "no", "pass": "pass"}
    if action not in verdict_map:
        return jsonify({"error": "action must be 'like', 'dislike', or 'pass'."}), 400

    verdict = verdict_map[action]

    existing = Swipe.query.filter_by(actor_id=me.id, subject_id=target_account_id).first()
    if existing:
        existing.verdict = verdict
        existing.swiped_at = datetime.now(timezone.utc)
    else:
        existing = Swipe(actor_id=me.id, subject_id=target_account_id, verdict=verdict)
        db.session.add(existing)

    connection_created = False
    connection_obj = None

    if verdict == "yes":
        reverse = Swipe.query.filter_by(
            actor_id=target_account_id, subject_id=me.id, verdict="yes"
        ).first()
        if reverse:
            u1, u2 = (me.id, target_account_id) if me.id < target_account_id else (target_account_id, me.id)
            connection_obj = Connection.query.filter_by(initiator_id=u1, receiver_id=u2).first()
            if not connection_obj:
                connection_obj = Connection(initiator_id=u1, receiver_id=u2)
                db.session.add(connection_obj)
                connection_created = True

                create_notification(
                    account_id=target_account_id,
                    title="New connection",
                    message=f"You are now connected with {me.handle}.",
                    notification_type="connection",
                )
                create_notification(
                    account_id=me.id,
                    title="New connection",
                    message=f"You are now connected with {target.handle}.",
                    notification_type="connection",
                )

    db.session.commit()

    response = {
        "message": f"Action '{action}' recorded.",
        "action": action,
        "connection": connection_obj.serialise(me.id) if connection_obj else None,
        "is_new_connection": connection_created,
    }
    return jsonify(response), 200


@api_bp.route("/api/connections", methods=["GET"])
@login_required
def get_connections():
    me = current_account()
    connections = Connection.query.filter(
        db.or_(Connection.initiator_id == me.id, Connection.receiver_id == me.id)
    ).order_by(Connection.formed_at.desc()).all()

    return jsonify({"connections": [m.serialise(me.id) for m in connections], "total": len(connections)}), 200


@api_bp.route("/api/bookmarks", methods=["GET"])
@login_required
def get_bookmarks():
    me = current_account()
    bookmarks = Bookmark.query.filter_by(owner_id=me.id).order_by(Bookmark.saved_at.desc()).all()
    return jsonify({"bookmarks": [bookmark.target.serialise() for bookmark in bookmarks], "total": len(bookmarks)}), 200


@api_bp.route("/api/bookmarks/<int:profile_id>", methods=["POST"])
@login_required
def add_bookmark(profile_id):
    me = current_account()
    profile = db.session.get(MemberProfile, profile_id)
    if not profile:
        return jsonify({"error": "Profile not found."}), 404

    existing = Bookmark.query.filter_by(owner_id=me.id, target_id=profile_id).first()
    if existing:
        return jsonify({"message": "Already bookmarked."}), 200

    fav = Bookmark(owner_id=me.id, target_id=profile_id)
    db.session.add(fav)
    db.session.commit()
    return jsonify({"message": "Added to bookmarks."}), 201


@api_bp.route("/api/bookmarks/<int:profile_id>", methods=["DELETE"])
@login_required
def remove_bookmark(profile_id):
    me = current_account()
    bookmark = Bookmark.query.filter_by(owner_id=me.id, target_id=profile_id).first()
    if not bookmark:
        return jsonify({"error": "Not in bookmarks."}), 404

    db.session.delete(bookmark)
    db.session.commit()
    return jsonify({"message": "Removed from bookmarks."}), 200
