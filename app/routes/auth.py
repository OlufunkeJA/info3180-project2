from app.routes.common import *


@api_bp.route("/api/register", methods=["POST"])
def register():
    data = request.get_json() or {}

    form = RegistrationForm(data=data)
    if not form.validate():
        return jsonify(errors=form_errors(form)), 400

    account = Account(
        handle=form.handle.data.strip(),
        email_address=form.email_address.data.lower().strip(),
    )

    account.store_password(form.password.data)
    try:
        db.session.add(account)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify(error="Registration failed."), 500

    session["account_id"] = account.id
    session.permanent = True

    return jsonify(message="Account registered successfully.", account=account.serialise()), 201


@api_bp.route("/api/login", methods=["POST"])
def login():
    data = request.get_json() or {}

    form = LoginForm(data=data)
    if not form.validate():
        return jsonify(errors=form_errors(form)), 400

    email = form.email_address.data.lower().strip()
    password = form.password.data

    account = Account.query.filter_by(email_address=email).first()

    if not account or not account.verify_password(password):
        return jsonify(error="Invalid email or password."), 401

    session["account_id"] = account.id
    session.permanent = True

    return jsonify(message="Login successful.", account=account.serialise()), 200


@api_bp.route("/api/logout", methods=["POST"])
@login_required
def logout():
    session.clear()
    return jsonify(message="Logout successful."), 200


@api_bp.route("/api/session", methods=["GET"])
def check_session():
    account = current_account()

    if not account:
        return jsonify(authenticated=False, account=None), 200

    return jsonify(authenticated=True, account=account.serialise()), 200


@api_bp.route("/api/settings/theme", methods=["PUT"])
@login_required
def update_theme():
    account = current_account()
    data = request.get_json() or {}

    theme = data.get("theme")
    if theme not in ["light", "dark", "system"]:
        return jsonify(error="Theme must be light, dark, or system."), 400

    if not hasattr(account, "theme"):
        return jsonify(error="Theme preference is not supported by the Account model."), 400

    account.theme = theme

    create_notification(
        account_id=account.id,
        title="Theme updated",
        message=f"Your theme was changed to {theme}.",
        notification_type="theme",
    )

    db.session.commit()

    return jsonify(message="Theme updated successfully.", account=account.serialise()), 200
