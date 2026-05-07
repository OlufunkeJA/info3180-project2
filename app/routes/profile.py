from app.routes.common import *


@api_bp.route("/api/profile", methods=["POST"])
def create_profile():
    account = current_account()

    existing_profile = MemberProfile.query.filter_by(acct_id=account.id).first()
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
        profile_picture = upload_profile_picture(request.files["profile_picture"], account.id)

    profile = MemberProfile(
        acct_id=account.id,
        first_name=form.first_name.data.strip(),
        surname=form.surname.data.strip(),
        birthdate=form.birthdate.data,
        about_me=form.about_me.data,
        gender=form.gender.data,
        seeking=form.seeking.data,
        parish=form.parish.data,
        city=form.city.data,
        country=form.country.data or "Jamaica",
        job_title=form.job_title.data,
        schooling=form.schooling.data,
        min_age=form.min_age.data or 18,
        max_age=form.max_age.data or 99,
        avatar_file=profile_picture,
        visible=form_boolean(form.visible.data),
    )

    profile.likes = interests

    try:
        db.session.add(profile)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify(error="Profile creation failed."), 500

    return jsonify(message="Profile created successfully.", profile=profile.serialise(private=True)), 201


@api_bp.route("/api/interests", methods=["GET"])
def get_interests():
    interests = Likes.query.order_by(Likes.name).all()
    return jsonify(interests=[interest.serialise() for interest in interests]), 200


@api_bp.route("/api/profile", methods=["GET"])
@login_required
def get_my_profile():
    account = current_account()

    profile = MemberProfile.query.filter_by(acct_id=account.id).first()
    if not profile:
        return jsonify(error="Profile not found."), 404

    return jsonify(profile=profile.serialise(private=True)), 200


@api_bp.route("/api/profile", methods=["PUT"])
@login_required
def update_my_profile():
    account = current_account()

    profile = MemberProfile.query.filter_by(acct_id=account.id).first()
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

        profile.likes = interests

    if "profile_picture" in request.files:
        uploaded_picture = upload_profile_picture(request.files["profile_picture"], account.id)
        if uploaded_picture:
            profile.avatar_file = uploaded_picture

    profile.first_name = form.first_name.data.strip()
    profile.surname = form.surname.data.strip()
    profile.birthdate = form.birthdate.data
    profile.about_me = form.about_me.data
    profile.gender = form.gender.data
    profile.seeking = form.seeking.data
    profile.parish = form.parish.data
    profile.city = form.city.data
    profile.country = form.country.data or "Jamaica"
    profile.job_title = form.job_title.data
    profile.schooling = form.schooling.data
    profile.min_age = form.min_age.data or 18
    profile.max_age = form.max_age.data or 99
    profile.visible = form_boolean(form.visible.data)

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify(error="Profile update failed."), 500

    return jsonify(message="Profile updated successfully.", profile=profile.serialise(private=True)), 200


@api_bp.route("/api/profiles", methods=["GET"])
def get_profiles():
    account = current_account()
    current_profile = MemberProfile.query.filter_by(acct_id=account.id).first()

    excluded_subjects = db.session.query(Swipe.subject_id).filter(
        Swipe.actor_id == account.id,
        Swipe.verdict.in_(["yes", "no"]),
    )

    query = MemberProfile.query.filter(
        MemberProfile.acct_id != account.id,
        MemberProfile.visible == True,
        ~MemberProfile.acct_id.in_(excluded_subjects),
    )

    if current_profile and current_profile.seeking and current_profile.seeking != "any":
        query = query.filter(MemberProfile.gender == current_profile.seeking)

    profiles = query.all()

    return jsonify(profiles=[profile.serialise() for profile in profiles]), 200


@api_bp.route("/api/profiles/<int:profile_id>", methods=["GET"])
def get_profile(profile_id):
    profile = db.session.get(MemberProfile, profile_id)

    if not profile:
        return jsonify(error="Profile not found."), 404

    if not profile.visible and profile.acct_id != current_account().id:
        return jsonify(error="This profile is private."), 403

    return jsonify(profile=profile.serialise(private=(profile.acct_id == current_account().id))), 200
