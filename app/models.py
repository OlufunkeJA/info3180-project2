# Add any model classes for Flask-SQLAlchemy here

from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash

from app import db


class User(db.Model):
    # -------------------------------------------------------------------
    # User model for authentication and user management
    # -------------------------------------------------------------------

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)

    # Dark mode / theme preference
    theme = db.Column(db.String(20), default="light")

    # Timestamp for when account was created
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    # Relationship to profile
    profile = db.relationship(
        "Profile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )
    

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"

    # Converts the object to a dictionary for JSON serialization
    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "theme": self.theme,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }



profile_interests = db.Table(
    "profile_interests",
    db.Column(
        "profile_id",
        db.Integer,
        db.ForeignKey("profiles.id", ondelete="CASCADE"),
        primary_key=True
    ),
    db.Column(
        "interest_id",
        db.Integer,
        db.ForeignKey("interests.id", ondelete="CASCADE"),
        primary_key=True
    )
)

class Profile(db.Model):

    # -------------------------------------------------------------------
    # Profile model for user details and preferences
    # -------------------------------------------------------------------

    __tablename__ = "profiles"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )

    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)

    date_of_birth = db.Column(db.Date, nullable=False)

    bio = db.Column(db.Text)

    gender = db.Column(db.String(30), nullable=False)
    looking_for = db.Column(db.String(30), default="any")

    parish = db.Column(db.String(80))
    city = db.Column(db.String(80))
    country = db.Column(db.String(80), default="Jamaica")
    occupation = db.Column(db.String(120))
    education_level = db.Column(db.String(120))
    preferred_age_min = db.Column(db.Integer, default=18)
    preferred_age_max = db.Column(db.Integer, default=99)
    profile_picture = db.Column(db.String(255))
    is_public = db.Column(db.Boolean, default=True)

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    user = db.relationship(
        "User",
        back_populates="profile"
    )
    interests = db.relationship(
        "Interest",
        secondary=profile_interests,
        back_populates="profiles"
    )

    @property
    def age(self):
        today = datetime.now(timezone.utc).date()

        return (
            today.year
            - self.date_of_birth.year
            - (
                (today.month, today.day)
                <
                (self.date_of_birth.month, self.date_of_birth.day)
            )
        )

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        return f"<Profile {self.full_name}>"

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "username": self.user.username if self.user else None,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "age": self.age,
            "bio": self.bio,
            "gender": self.gender,
            "looking_for": self.looking_for,
            "parish": self.parish,
            "city": self.city,
            "country": self.country,
            "occupation": self.occupation,
            "education_level": self.education_level,
            "preferred_age_min": self.preferred_age_min,
            "preferred_age_max": self.preferred_age_max,
            "profile_picture": self.profile_picture,
            "is_public": self.is_public,
            "interests": [interest.name for interest in self.interests],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class Interest(db.Model):
    # -------------------------------------------------------------------
    # Interest model for hobbies/interests
    # -------------------------------------------------------------------

    __tablename__ = "interests"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(
        db.String(80),
        unique=True,
        nullable=False,
        index=True
    )

    profiles = db.relationship(
        "Profile",
        secondary=profile_interests,
        back_populates="interests"
    )

    def __repr__(self):
        return f"<Interest {self.name}>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name
        }    