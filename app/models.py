# Add any model classes for Flask-SQLAlchemy here
from datetime import datetime, timezone

import bcrypt
from app import db, login_manager
from flask_login import UserMixin

#MemberProfile <-> Likes

member_likes = db.Table(
    "member_likes",
    db.Column(
        "member_id",
        db.Integer,
        db.ForeignKey("member_profiles.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    db.Column(
        "like_id",
        db.Integer,
        db.ForeignKey("likes.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)

#Account

class Account(UserMixin, db.Model):
    __tablename__ = "accounts"

    id            = db.Column(db.Integer, primary_key=True)
    handle        = db.Column(db.String(64),  unique=True, nullable=False, index=True)
    email_address = db.Column(db.String(128), unique=True, nullable=False, index=True)
    pw_hash       = db.Column(db.String(256), nullable=False)
    registered_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    member_profile = db.relationship(
        "MemberProfile",
        back_populates="account",
        uselist=False,
        cascade="all, delete-orphan",
    )

    # ----------------------------------------------------------
    def store_password(self, raw: str) -> None:
        self.pw_hash = bcrypt.hashpw(
            raw.encode(), bcrypt.gensalt()
        ).decode()

    def verify_password(self, raw: str) -> bool:
        return bcrypt.checkpw(raw.encode(), self.pw_hash.encode())

    def serialise(self) -> dict:
        return {
            "id":            self.id,
            "handle":        self.handle,
            "email_address": self.email_address,
            "registered_at": self.registered_at.isoformat() if self.registered_at else None,
        }

@login_manager.user_loader
def fetch_account(account_id: str):
    return db.session.get(Account, int(account_id))

class MemberProfile(db.Model):
    __tablename__ = "member_profiles"

    id      = db.Column(db.Integer, primary_key=True)
    acct_id = db.Column(
        db.Integer,
        db.ForeignKey("accounts.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    # --- Personal details ---
    first_name  = db.Column(db.String(64), nullable=False)
    surname = db.Column(db.String(64), nullable=False)
    birthdate   = db.Column(db.Date,       nullable=False)
    gender      = db.Column(db.String(32), nullable=False)
    seeking     = db.Column(db.String(32), default="any")

    # --- Bio & location ---
    about_me  = db.Column(db.Text)
    parish    = db.Column(db.String(64))
    city      = db.Column(db.String(64))
    country    = db.Column(db.String(64), default="Jamaica")
    lat       = db.Column(db.Float)
    lng       = db.Column(db.Float)

    # --- Matching preferences ---
    min_age       = db.Column(db.Integer, default=18)
    max_age       = db.Column(db.Integer, default=99)
    search_radius = db.Column(db.Integer, default=50)   # kilometres

    # --- Extra fields ---
    job_title   = db.Column(db.String(128))
    schooling   = db.Column(db.String(64))              # e.g. Bachelor's, Master's

    # --- Display ---
    avatar_file = db.Column(db.String(256))
    visible     = db.Column(db.Boolean, default=True)

    created_at  = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    modified_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # --- Relationships ---
    account = db.relationship("Account", back_populates="member_profile")
    likes    = db.relationship(
        "Likes",
        secondary=member_likes,
        back_populates="members",
        lazy="select",
    )

    __table_args__ = (
        db.Index("ix_mp_parish_country", "parish", "country"),
        db.Index("ix_mp_gender",          "gender"),
    )

    # ----------------------------------------------------------
    @property
    def current_age(self) -> int | None:
        """Calculate age from birthdate; returns None when birthdate is absent."""
        if not self.birthdate:
            return None
        today = datetime.now(timezone.utc).date()
        bd    = self.birthdate
        return today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))

    @property
    def display_name(self) -> str:
        return f"{self.first_name} {self.surname}"

    def _avatar_url(self) -> str | None:
        if not self.avatar_file:
            return None
        if self.avatar_file.startswith("http"):
            return self.avatar_file
        return f"/api/v1/uploads/{self.avatar_file}"

    def serialise(self, private: bool = False) -> dict:
        payload = {
            "id":           self.id,
            "acct_id":      self.acct_id,
            "handle":       self.account.handle if self.account else None,
            "first_name":   self.first_name,
            "surname":      self.surname,
            "display_name": self.display_name,
            "age":          self.current_age,
            "gender":       self.gender,
            "seeking":      self.seeking,
            "about_me":     self.about_me,
            "parish":       self.parish,
            "city":         self.city,
            "country":      self.country,
            "job_title":    self.job_title,
            "schooling":    self.schooling,
            "avatar_url":   self._avatar_url(),
            "visible":      self.visible,
            "likes":         [t.name for t in self.likes],
            "min_age":      self.min_age,
            "max_age":      self.max_age,
            "search_radius": self.search_radius,
            "created_at":   self.created_at.isoformat() if self.created_at else None,
        }
        if private:
            payload.update({
                "email_address": self.account.email_address if self.account else None,
                "lat":           self.lat,
                "lng":           self.lng,
            })
        return payload

class Likes(db.Model):
    __tablename__ = "likes"

    id    = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False, index=True)

    members = db.relationship(
        "MemberProfile",
        secondary=member_likes,
        back_populates="likes",
        lazy="select",
    )

    def serialise(self) -> dict:
        return {"id": self.id, "name": self.name}

class Swipe(db.Model):
    __tablename__ = "swipes"

    id         = db.Column(db.Integer, primary_key=True)
    actor_id   = db.Column(
        db.Integer, db.ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False
    )
    subject_id = db.Column(
        db.Integer, db.ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False
    )
    verdict    = db.Column(db.String(16), nullable=False)   # 'yes' | 'no'
    swiped_at  = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        db.UniqueConstraint("actor_id", "subject_id", name="uq_swipe_pair"),
        db.Index("ix_swipes_actor",   "actor_id"),
        db.Index("ix_swipes_subject", "subject_id"),
    )

    actor   = db.relationship("Account", foreign_keys=[actor_id])
    subject = db.relationship("Account", foreign_keys=[subject_id])

class Connection(db.Model):
    __tablename__ = "connections"

    id           = db.Column(db.Integer, primary_key=True)
    initiator_id = db.Column(
        db.Integer, db.ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False
    )
    receiver_id  = db.Column(
        db.Integer, db.ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False
    )
    formed_at    = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        db.UniqueConstraint("initiator_id", "receiver_id", name="uq_connection_pair"),
        db.Index("ix_connections_initiator", "initiator_id"),
        db.Index("ix_connections_receiver",  "receiver_id"),
    )

    initiator = db.relationship("Account", foreign_keys=[initiator_id])
    receiver  = db.relationship("Account", foreign_keys=[receiver_id])
    thread    = db.relationship(
        "ChatMessage",
        back_populates="connection",
        cascade="all, delete-orphan",
        order_by="ChatMessage.sent_at",
    )

    def partner(self, viewer_id: int):
        """Return the other Account involved in this Connection."""
        return self.receiver if self.initiator_id == viewer_id else self.initiator

    def serialise(self, viewer_id: int | None = None) -> dict:
        other = self.partner(viewer_id) if viewer_id else None
        return {
            "id":            self.id,
            "initiator_id":  self.initiator_id,
            "receiver_id":   self.receiver_id,
            "formed_at":     self.formed_at.isoformat() if self.formed_at else None,
            "other_profile": (
                other.member_profile.serialise()
                if other and other.member_profile
                else None
            ),
        }

class ChatMessage(db.Model):
    __tablename__ = "chat_messages"

    id            = db.Column(db.Integer, primary_key=True)
    connection_id = db.Column(
        db.Integer,
        db.ForeignKey("connections.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    author_id     = db.Column(
        db.Integer, db.ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False
    )
    content       = db.Column(db.Text, nullable=False)
    sent_at       = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    connection = db.relationship("Connection", back_populates="thread")
    author     = db.relationship("Account", foreign_keys=[author_id])

    def serialise(self) -> dict:
        return {
            "id":            self.id,
            "connection_id": self.connection_id,
            "author_id":     self.author_id,
            "author_handle": self.author.handle if self.author else None,
            "content":       self.content,
            "sent_at":       self.sent_at.isoformat() if self.sent_at else None,
        }

class Saved(db.Model):
    __tablename__ = "saved_profiles"

    id         = db.Column(db.Integer, primary_key=True)
    owner_id   = db.Column(
        db.Integer, db.ForeignKey("accounts.id",       ondelete="CASCADE"), nullable=False
    )
    target_id  = db.Column(
        db.Integer, db.ForeignKey("member_profiles.id", ondelete="CASCADE"), nullable=False
    )
    saved_at   = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        db.UniqueConstraint("owner_id", "target_id", name="uq_saved_entry"),
    )

    owner  = db.relationship("Account",       foreign_keys=[owner_id])
    target = db.relationship("MemberProfile", foreign_keys=[target_id])

class Report(db.Model):
    __tablename__ = "reports"

    id          = db.Column(db.Integer, primary_key=True)
    filed_by    = db.Column(
        db.Integer, db.ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False
    )
    filed_about = db.Column(
        db.Integer, db.ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False
    )
    category    = db.Column(db.String(64), nullable=False)   # spam/harassment/fake/other
    description = db.Column(db.Text)
    resolution  = db.Column(db.String(16), default="open")   # open/closed/dismissed
    filed_at    = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        db.UniqueConstraint("filed_by", "filed_about", name="uq_report_pair"),
        db.Index("ix_reports_resolution", "resolution"),
    )

    complainant = db.relationship("Account", foreign_keys=[filed_by])
    respondent  = db.relationship("Account", foreign_keys=[filed_about])

    def serialise(self) -> dict:
        return {
            "id":               self.id,
            "filed_by":         self.filed_by,
            "filed_about":      self.filed_about,
            "respondent_handle": (
                self.respondent.handle if self.respondent else None
            ),
            "category":    self.category,
            "description": self.description,
            "resolution":  self.resolution,
            "filed_at":    self.filed_at.isoformat() if self.filed_at else None,
        }

class Block(db.Model):
    __tablename__ = "blocks"

    id          = db.Column(db.Integer, primary_key=True)
    enforcer_id = db.Column(
        db.Integer, db.ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False
    )
    blocked_id  = db.Column(
        db.Integer, db.ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False
    )
    imposed_at  = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        db.UniqueConstraint("enforcer_id", "blocked_id", name="uq_block_pair"),
        db.Index("ix_blocks_enforcer", "enforcer_id"),
    )

    enforcer = db.relationship("Account", foreign_keys=[enforcer_id])
    blocked  = db.relationship("Account", foreign_keys=[blocked_id])

