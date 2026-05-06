from app.routes.common import *


@api_bp.route("/api/notifications", methods=["GET"])
@login_required
def get_notifications():
    account = current_account()

    notifications = Notification.query.filter_by(account_id=account.id).order_by(
        Notification.created_at.desc()
    ).all()

    unread_count = Notification.query.filter_by(account_id=account.id, is_read=False).count()

    return jsonify(
        notifications=[notification.to_dict() for notification in notifications],
        unread_count=unread_count,
    ), 200


@api_bp.route("/api/notifications/unread-count", methods=["GET"])
@login_required
def get_unread_notification_count():
    account = current_account()

    unread_count = Notification.query.filter_by(account_id=account.id, is_read=False).count()

    return jsonify(unread_count=unread_count), 200


@api_bp.route("/api/notifications/<int:notification_id>/read", methods=["PUT"])
@login_required
def mark_notification_read(notification_id):
    account = current_account()

    notification = db.session.get(Notification, notification_id)
    if not notification:
        return jsonify(error="Notification not found."), 404

    if notification.account_id != account.id:
        return jsonify(error="You cannot update this notification."), 403

    notification.is_read = True
    db.session.commit()

    return jsonify(message="Notification marked as read.", notification=notification.to_dict()), 200


@api_bp.route("/api/notifications/read-all", methods=["PUT"])
@login_required
def mark_all_notifications_read():
    account = current_account()

    notifications = Notification.query.filter_by(account_id=account.id, is_read=False).all()

    for notification in notifications:
        notification.is_read = True

    db.session.commit()

    return jsonify(message="All notifications marked as read."), 200
