#!/usr/bin/python3
"""Define DB models for user management, reviews, availability, and appointments."""
from .extensions import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Column, String, Integer, ForeignKey, Text, DateTime, Boolean, Time
from sqlalchemy.orm import relationship


class User(db.Model, UserMixin):
    """User model to store user-related information."""
    __tablename__ = 'users'

    MAX_USERNAME_LENGTH = 80
    MAX_EMAIL_LENGTH = 120
    MAX_PASSWORD_HASH_LENGTH = 128
    MAX_ROLE_LENGTH = 50

    id = Column(Integer, primary_key=True)
    username = Column(String(MAX_USERNAME_LENGTH), unique=True, nullable=False, index=True)
    email = Column(String(MAX_EMAIL_LENGTH), unique=True, nullable=False, index=True)
    password_hash = Column(String(MAX_PASSWORD_HASH_LENGTH), nullable=False)
    email_confirmed = Column(Boolean, default=True)
    bio = Column(Text, nullable=True)
    profile_picture = Column(String(1024), nullable=True)
    role = Column(String(MAX_ROLE_LENGTH), nullable=False)
    time_zone = Column(String(50), nullable=True)
    country = Column(String(100), nullable=True)
    level = Column(String(50), nullable=True)
    subject = Column(String(200), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    availabilities = relationship('Availability', back_populates='teacher', cascade="all, delete-orphan", lazy=True)
    appointments_sent = relationship('Appointment', back_populates='student', foreign_keys='Appointment.student_id', lazy=True, cascade="all, delete-orphan")
    appointments_received = relationship('Appointment', back_populates='teacher', foreign_keys='Appointment.teacher_id', lazy=True, cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="teacher", cascade="all, delete-orphan", foreign_keys="[Review.teacher_id]")

    notifications = relationship('Notification', back_populates='user', cascade="all, delete-orphan", lazy=True)

    def to_dict(self):
        """Return a dictionary representation of the user."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'email_confirmed': self.email_confirmed,
            'bio': self.bio,
            'profile_picture': self.profile_picture,
            'role': self.role,
            'country': self.country,
            'time_zone': self.time_zone,
            'level': self.level,
            'subject': self.subject,
            'reviews': self.reviews,
            'reviews_co': len(self.reviews)
        }

    def __init__(self, username, email, password, role):
        super().__init__()
        self.username = username
        self.email = email
        self.set_password(password)
        self.role = role

    def set_password(self, password):
        """Hash the password and store it in the password_hash field."""
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def verify_password(self, password):
        """Verify the provided password against the stored password hash."""
        return check_password_hash(self.password_hash, password)


class Availability(db.Model):
    """Model to store teacher availability."""
    __tablename__ = 'availabilities'

    id = Column(Integer, primary_key=True)
    teacher_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    day_of_week = Column(String(10), nullable=False)  # e.g., 'Monday'
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)

    teacher = relationship('User', back_populates='availabilities')


class Appointment(db.Model):
    """Model to handle appointment scheduling between students and teachers."""
    __tablename__ = 'appointments'

    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    DECLINED = 'declined'
    CANCELED = 'canceled'

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    teacher_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    slot_time = Column(DateTime, nullable=False, index=True)  # Adding index for performance
    status = Column(String(20), default=PENDING)
    cancel_reason = Column(Text, nullable=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    material_url = Column(String(200), nullable=True)
    google_meet_link = Column(String(200), nullable=True)

    student = relationship('User', foreign_keys=[student_id], back_populates='appointments_sent')
    teacher = relationship('User', foreign_keys=[teacher_id], back_populates='appointments_received')


class Review(db.Model):
    """Model to store student reviews for teachers."""
    __tablename__ = 'reviews'

    id = Column(Integer, primary_key=True)
    comment = Column(Text, nullable=False)
    rating = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    student_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    teacher_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    teacher = relationship("User", back_populates="reviews", foreign_keys=[teacher_id])
    student = relationship("User", foreign_keys=[student_id])


class Notification(db.Model):
    """Model to handle notifications."""
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    read = db.Column(db.Boolean, default=False)

    user = db.relationship('User', back_populates='notifications')
