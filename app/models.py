"""Database models for the PKSK replacement."""

from __future__ import annotations

from datetime import datetime, timezone

from flask_login import UserMixin
from sqlalchemy import false, true
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db


def utc_now():
    return datetime.now(timezone.utc)


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, index=True, nullable=False)
    username = db.Column(db.String(80), unique=True, index=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="editor", server_default="editor")
    active = db.Column(db.Boolean, nullable=False, default=True, server_default=true())
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utc_now)
    last_seen = db.Column(db.DateTime(timezone=True), nullable=True)

    posts = db.relationship("Post", back_populates="author", lazy="dynamic")
    pages = db.relationship("StaticPage", back_populates="author", lazy="dynamic")

    @property
    def is_admin(self):
        return self.role == "admin"

    @property
    def is_active(self):
        return self.active

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Post(db.Model):
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True, index=True, nullable=False)
    summary = db.Column(db.Text, nullable=True)
    body = db.Column(db.Text, nullable=False, default="")
    body_html = db.Column(db.Text, nullable=False, default="")
    image = db.Column(db.String(255), nullable=True)
    image_alt = db.Column(db.String(255), nullable=True)
    image_caption = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), nullable=False, default="draft", server_default="draft")
    published_at = db.Column(db.DateTime(timezone=True), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    author = db.relationship("User", back_populates="posts")


class StaticPage(db.Model):
    __tablename__ = "static_pages"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True, index=True, nullable=False)
    body = db.Column(db.Text, nullable=False, default="")
    body_html = db.Column(db.Text, nullable=False, default="")
    status = db.Column(db.String(20), nullable=False, default="draft", server_default="draft")
    show_in_nav = db.Column(db.Boolean, nullable=False, default=False, server_default=false())
    nav_order = db.Column(db.Integer, nullable=False, default=0, server_default="0")
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    author = db.relationship("User", back_populates="pages")


class SiteSettings(db.Model):
    __tablename__ = "site_settings"

    id = db.Column(db.Integer, primary_key=True, default=1)
    site_name = db.Column(db.String(255), nullable=False, default="PKSK")
    site_description = db.Column(db.Text, nullable=True)
    tagline = db.Column(db.String(255), nullable=True)
    contact_email = db.Column(db.String(255), nullable=True)
    contact_phone = db.Column(db.String(80), nullable=True)
    address = db.Column(db.Text, nullable=True)
    facebook_url = db.Column(db.String(500), nullable=True)
    instagram_url = db.Column(db.String(500), nullable=True)
    footer_text = db.Column(db.Text, nullable=True)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now)
