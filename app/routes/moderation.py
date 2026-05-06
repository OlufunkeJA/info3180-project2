from app.routes.common import *


@api_bp.route("/api/accounts/<int:target_id>/report", methods=["POST"])
@login_required
def report_account(target_id):
    me = current_account()
    if me.id == target_id:
        return jsonify({"error": "Cannot report yourself."}), 400

    target = db.session.get(Account, target_id)
    if not target:
        return jsonify({"error": "Account not found."}), 404

    data = request.get_json(silent=True) or request.form
    reason = (data.get("reason") or "").strip()
    details = (data.get("details") or "").strip()

    if reason not in ("spam", "harassment", "fake", "inappropriate", "other"):
        return jsonify({"error": "reason must be one of: spam, harassment, fake, inappropriate, other"}), 400

    existing = Report.query.filter_by(filed_by=me.id, filed_about=target_id).first()
    if existing:
        return jsonify({"message": "Already reported."}), 200

    report = Report(filed_by=me.id, filed_about=target_id, category=reason, description=details)
    db.session.add(report)
    db.session.commit()
    return jsonify({"message": "Report submitted. Our team will review it."}), 201


@api_bp.route("/api/accounts/<int:target_id>/block", methods=["POST"])
@login_required
def block_account(target_id):
    me = current_account()
    if me.id == target_id:
        return jsonify({"error": "Cannot self-block."}), 400

    existing = Block.query.filter_by(enforcer_id=me.id, blocked_id=target_id).first()
    if existing:
        return jsonify({"message": "Already blocked this account."}), 200

    block = Block(enforcer_id=me.id, blocked_id=target_id)
    db.session.add(block)
    db.session.commit()
    return jsonify({"message": "Account blocked."}), 201


@api_bp.route("/api/accounts/<int:target_id>/unblock", methods=["DELETE"])
@login_required
def unblock_account(target_id):
    me = current_account()
    block = Block.query.filter_by(enforcer_id=me.id, blocked_id=target_id).first()
    if not block:
        return jsonify({"error": "Account was not blocked."}), 404
    db.session.delete(block)
    db.session.commit()
    return jsonify({"message": "Account unblocked."}), 200


@api_bp.route("/api/blocks", methods=["GET"])
@login_required
def get_blocks():
    me = current_account()
    blocks = Block.query.filter_by(enforcer_id=me.id).all()
    return jsonify(
        {
            "blocked": [
                {
                    "account_id": b.blocked_id,
                    "username": b.blocked.handle if b.blocked else None,
                    "blocked_at": b.imposed_at.isoformat() if b.imposed_at else None,
                }
                for b in blocks
            ]
        }
    ), 200
