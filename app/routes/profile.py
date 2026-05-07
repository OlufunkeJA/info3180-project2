import math

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


def haversine_distance(lat1, lon1, lat2, lon2):
    if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
        return None

    radius = 6371.0
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return radius * c


def build_match_score(current_profile, candidate):
    score = 0
    distance = None

    if current_profile and current_profile.lat is not None and current_profile.lng is not None and candidate.lat is not None and candidate.lng is not None:
        distance = haversine_distance(current_profile.lat, current_profile.lng, candidate.lat, candidate.lng)
        search_radius = current_profile.search_radius or 50
        if distance <= search_radius:
            score += int((1 - distance / search_radius) * 30)

    candidate_age = candidate.current_age
    current_age = current_profile.current_age if current_profile else None

    if current_profile:
        if candidate_age is not None and current_profile.min_age <= candidate_age <= current_profile.max_age:
            score += 15
        if current_age is not None and candidate.min_age <= current_age <= candidate.max_age:
            score += 15

    if current_profile and current_profile.likes and candidate.likes:
        current_interests = {interest.name for interest in current_profile.likes}
        candidate_interests = {interest.name for interest in candidate.likes}
        common_interests = current_interests.intersection(candidate_interests)
        score += min(len(common_interests) * 5, 20)

    if current_profile and current_profile.job_title and candidate.job_title and current_profile.job_title.strip().lower() == candidate.job_title.strip().lower():
        score += 10

    if current_profile and current_profile.schooling and candidate.schooling and current_profile.schooling.strip().lower() == candidate.schooling.strip().lower():
        score += 10

    return score, distance


@api_bp.route("/api/profiles", methods=["GET"])
def get_profiles():
    account = current_account()
    current_profile = MemberProfile.query.filter_by(acct_id=account.id).first()

    location = request.args.get("location", "").strip()
    min_age = request.args.get("min_age", type=int)
    max_age = request.args.get("max_age", type=int)
    interests_raw = request.args.get("interests", "").strip()
    gender = request.args.get("gender", "").strip()
    job_title = request.args.get("job_title", "").strip()
    schooling = request.args.get("schooling", "").strip()
    sort = request.args.get("sort", "newest").strip().lower()

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

    if location:
        pattern = f"%{location}%"
        query = query.filter(
            db.or_(
                MemberProfile.city.ilike(pattern),
                MemberProfile.parish.ilike(pattern),
                MemberProfile.country.ilike(pattern),
            )
        )

    if gender:
        query = query.filter(MemberProfile.gender.ilike(f"%{gender}%"))

    if job_title:
        query = query.filter(MemberProfile.job_title.ilike(f"%{job_title}%"))

    if schooling:
        query = query.filter(MemberProfile.schooling.ilike(f"%{schooling}%"))

    if min_age is not None or max_age is not None:
        today = datetime.now(timezone.utc).date()

        if min_age is not None:
            max_birthdate = today - timedelta(days=int(min_age * 365.25))
            query = query.filter(MemberProfile.birthdate <= max_birthdate)

        if max_age is not None:
            min_birthdate = today - timedelta(days=int(max_age * 365.25))
            query = query.filter(MemberProfile.birthdate >= min_birthdate)

    if interests_raw:
        interest_names = [interest.strip().lower() for interest in interests_raw.split(",") if interest.strip()]
        if interest_names:
            query = query.join(MemberProfile.likes).filter(Likes.name.in_(interest_names)).distinct()

    profiles = query.all()
    profile_results = []

    for profile in profiles:
        score, distance = build_match_score(current_profile, profile)
        profile_data = profile.serialise()
        profile_data["match_score"] = score
        if distance is not None:
            profile_data["distance_km"] = round(distance, 1)
        profile_results.append(profile_data)

    if sort == "newest":
        profile_results.sort(key=lambda item: item["created_at"], reverse=True)
    else:
        profile_results.sort(key=lambda item: (item["match_score"], item["created_at"]), reverse=True)

    return jsonify(profiles=profile_results), 200


@api_bp.route("/api/profiles/<int:profile_id>", methods=["GET"])
def get_profile(profile_id):
    profile = db.session.get(MemberProfile, profile_id)

    if not profile:
        return jsonify(error="Profile not found."), 404

    if not profile.visible and profile.acct_id != current_account().id:
        return jsonify(error="This profile is private."), 403

    return jsonify(profile=profile.serialise(private=(profile.acct_id == current_account().id))), 200
