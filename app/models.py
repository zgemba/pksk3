import hashlib
import os
import stat
from datetime import datetime, timedelta

import bleach
from PIL import Image
from flask import current_app, request
from flask_login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from markdown import markdown
from sqlalchemy import desc
from werkzeug.security import generate_password_hash, check_password_hash

from . import db, login_manager


class Permission:
    READ = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    MODERATE_ROUTES = 0x10
    ADMINISTER = 0x80


class MailNotification:
    NONE = 0x00
    NEWS = 0x01
    COMMENTS = 0x02
    ANNOUNCEMENTS = 0x04
    DEFAULT = ANNOUNCEMENTS | NEWS


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'Guest': (Permission.READ, True),
            'User': (Permission.READ |
                     Permission.COMMENT |
                     Permission.WRITE_ARTICLES, False),
            'Moderator': (Permission.READ |
                          Permission.COMMENT |
                          Permission.WRITE_ARTICLES |
                          Permission.MODERATE_COMMENTS |
                          Permission.MODERATE_ROUTES, False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name


#
# USERS
#
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    approved = db.Column(db.Boolean, default=False)  # potrjen od admina
    name = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    avatar_hash = db.Column(db.String(32))
    mail_notify = db.Column(db.Integer, default=MailNotification.DEFAULT)
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    events = db.relationship('CalendarEvent', backref='author', lazy='dynamic')
    guidebooks = db.relationship('Guidebook', backref='owner', lazy='dynamic')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email in current_app.config['ADMIN_EMAIL']:  # možnih je več adminov!
                self.role = Role.query.filter_by(permissions=0xff).first()
                self.approved = True
                self.confirmed = True
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(
                self.email.encode('utf-8')).hexdigest()

        if self.email is not None:
            self.username = self.email.split("@")[0]  # nastavim na nek default

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        db.session.commit()  # zaradi debuga rabim takojšen commit
        return True

    def approve(self):  # to ročno uredi admin na zaščiteni routi
        self.approved = True
        self.role = Role.query.filter_by(name="User").first()
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        self.avatar_hash = hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        db.session.add(self)
        return True

    def can(self, permissions):
        return self.role is not None and \
               (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def is_approved(self):
        return self.approved

    def notify(self, notification):
        return bool(self.mail_notify & notification)

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = self.avatar_hash or hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)

    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'],
                       expires_in=expiration)
        return s.dumps({'id': self.id}).decode('ascii')

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

    def __repr__(self):
        return '<User %r>' % self.username

    def delete(self):
        # tu uredimo kaskado ali kaj naj se naredi z posti ipd izbrisanega?
        db.session.delete(self)

    @staticmethod
    def users_to_notify(level):
        users = User.query.filter(User.mail_notify.op('&')(level) > 0).all()
        return [u.email for u in users]


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

    def is_approved(self):
        return False


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


#
#          POSTS
#
class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    comments = db.relationship('Comment', backref='post', lazy='dynamic', cascade="save-update, merge, delete")
    images = db.relationship("PostImage", backref="post", lazy="dynamic", cascade="save-update, merge, delete")

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p', 'img']
        allowed_attributes = ['src', 'alt', 'href']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True, attributes=allowed_attributes))

    @property
    def has_images(self):
        return self.images_count > 0

    @property
    def images_count(self):
        return self.images.count()

    @property
    def has_comments(self):
        return self.comments_count > 0

    @property
    def comments_count(self):
        return self.comments.count()

    @property
    def post_thumbnail(self):
        return self.images[0].thumbnail if self.has_images else None

    @property
    def headline_image(self):
        img = [i.headline for i in self.images if i.is_headline] or None
        return img[0] if img else None


db.event.listen(Post.body, 'set', Post.on_changed_body)


#
# COMMENTS
#
class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    disabled = db.Column(db.Boolean)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'code', 'em', 'i',
                        'strong']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))


db.event.listen(Comment.body, 'set', Comment.on_changed_body)


#
# IMAGES
#
class PostImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime)
    comment = db.Column(db.String(200))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    is_headline = db.Column(db.Boolean, default=False)

    def __init__(self, filename, timestamp, comment, post, is_headline=False):
        self.filename = os.path.split(filename)[1]  # hranim samo ime fajla, ostalo dela getter automagično
        self.timestamp = timestamp
        self.comment = comment
        self.post = post
        self.is_headline = is_headline

        self._correct_orientation_from_exif()

        if self._is_oversize:
            self._resize(current_app.config["MAX_UPLOAD_DIMENSION"], self._file_on_disk)

        self._create_thumbnail()

        if self.is_headline:
            self._create_headline()

    @property
    def _file_on_disk(self):
        return os.path.join(current_app.config["UPLOAD_SAVE_FOLDER"], self.filename)

    @property
    def _thumbnail_on_disk(self):
        (name, ext) = os.path.splitext(self.filename)
        thumb_name = name + "-thumbnail" + ext
        return os.path.join(current_app.config["UPLOAD_SAVE_FOLDER"], thumb_name)

    @property
    def _headline_on_disk(self):
        (name, ext) = os.path.splitext(self.filename)
        thumb_name = name + "-headline" + ext
        return os.path.join(current_app.config["UPLOAD_SAVE_FOLDER"], thumb_name)

    @property
    def file(self):
        return os.path.join(current_app.config["UPLOAD_FOLDER"], self.filename)

    @property
    def thumbnail(self):
        (name, ext) = os.path.splitext(self.filename)
        thumb_name = name + "-thumbnail" + ext
        return os.path.join(current_app.config["UPLOAD_FOLDER"], thumb_name)

    @property
    def headline(self):
        (name, ext) = os.path.splitext(self.filename)
        thumb_name = os.path.join(current_app.config["UPLOAD_FOLDER"], name + "-headline" + ext)
        return thumb_name

    @property
    def _is_oversize(self):
        max_size = current_app.config["MAX_UPLOAD_DIMENSION"]
        im = Image.open(self._file_on_disk)
        return max(im.size) > max_size

    def _correct_orientation_from_exif(self):
        im = Image.open(self._file_on_disk)
        if hasattr(im, "_getexif"):  # samo jpeg, to sicer preveri že upload?
            tags = im._getexif()
            if tags is not None:
                transforms = {3: Image.ROTATE_180, 6: Image.ROTATE_270, 8: Image.ROTATE_90}
                if 274 in tags.keys():  # 274 je orientacija
                    orientation = tags[274]  # pozor, image lahko da ima tage, ni nujno, da ima orientacijo!
                    if orientation in transforms.keys():
                        self._rotate(transforms[orientation])
        im.close()

    def _resize(self, max_dim, new_filename):
        im = Image.open(self._file_on_disk)
        (px, py) = im.size

        if px > py:  # horizontalno skaliram
            scale = max_dim / float(px)
        else:  # vertikalno skaliram
            scale = max_dim / float(py)

        npx = int(px * scale)
        npy = int(py * scale)
        new = im.resize((npx, npy), Image.ANTIALIAS)
        new.save(new_filename)

    def _create_thumbnail(self):
        (name, ext) = os.path.splitext(self.filename)
        (path, file) = os.path.split(self._file_on_disk)
        new_name = os.path.join(path, name + "-thumbnail" + ext)
        thumb_size = current_app.config["THUMBNAIL_SIZE"]
        self._resize(thumb_size, new_name)

    def _create_headline(self):
        (name, ext) = os.path.splitext(self.filename)
        (path, file) = os.path.split(self._file_on_disk)
        new_name = os.path.join(path, name + "-headline" + ext)
        if os.path.exists(new_name):
            return  # če slučajno že obstaja?

        thumb_size = current_app.config["HEADLINE_SIZE"]
        im = Image.open(self._file_on_disk)
        if max(im.size) > thumb_size:  # samo če je slika večja
            self._resize(thumb_size, new_name)
        else:
            # naredi symlink originala, da prihranim disk
            os.symlink(self._file_on_disk, new_name)

    @property
    def _unique_filename(self):
        (name, ext) = os.path.splitext(self.filename)
        name = name.split("-")[0]
        mtime = os.stat(self._file_on_disk)[stat.ST_MTIME]
        return "{0}-{1}{2}".format(name, str(mtime), ext)

    def rotate_cw(self):
        self._rotate(Image.ROTATE_270)
        self._create_thumbnail()
        if self.is_headline:
            self._create_headline()

    def rotate_ccw(self):
        self._rotate(Image.ROTATE_90)
        self._create_thumbnail()
        if self.is_headline:
            self._create_headline()

    def _rotate(self, rotation):
        im = Image.open(self._file_on_disk)
        new = im.transpose(rotation)
        new_name = self._unique_filename
        new_file_on_disk = os.path.join(current_app.config["UPLOAD_SAVE_FOLDER"], new_name)
        new.save(new_file_on_disk)
        self.remove()
        self.filename = new_name

    def remove(self):
        try:
            os.remove(self._file_on_disk)
            os.remove(self._thumbnail_on_disk)
            os.remove(self._headline_on_disk)
        except FileNotFoundError:
            pass  # silent ignore

    @staticmethod
    def on_changed_is_headline(target, value, oldvalue, initiator):  # lazy init headline slike
        if value and not target.is_headline and not os.path.exists(target.headline):
            target._create_headline()


db.event.listen(PostImage.is_headline, 'set', PostImage.on_changed_is_headline)


#
# Koledar
#

class CalendarEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime)  # datum kreiranja
    start = db.Column(db.DateTime)
    end = db.Column(db.DateTime)
    title = db.Column(db.String(64))
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer)  # ker je opcionalno polje ne bom delal ORM
    _tags_string = db.Column(db.Text)  # ^ enako

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p', 'img']
        allowed_attributes = ['src', 'alt', 'href']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True, attributes=allowed_attributes))

    @property
    def expired(self):
        if self.end:
            return self.end < datetime.utcnow()
        else:
            # če smo ravno na tisti dan in dogodek še traja, robni primer
            now = datetime.utcnow()
            cutoff = datetime(year=now.year, month=now.month, day=now.day) + timedelta(days=1)
            return self.start < cutoff

    @property
    def tags(self):
        if self._tags_string:
            return self._tags_string.split(",")
        else:
            return []

    @tags.setter
    def tags(self, value):
        if value not in self.tags:
            self._tags_string = ",".join(value)

    @property
    def is_multiday(self):
        return datetime.date(self.start) != datetime.date(self.end)


db.event.listen(CalendarEvent.body, 'set', CalendarEvent.on_changed_body)


#
# tags,
# TODO: tagsi gredo lahko k eventom ali k postom? je to treba ločiti, da ne bo podvajanja/prekrivanja???
#

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(30))

    @staticmethod
    def all_tags():
        return sorted([tag.text for tag in Tag.query.all()], key=lambda tag: tag.lower())


#
# Guidebooks
#

class Guidebook(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    author = db.Column(db.String(100))
    publisher = db.Column(db.String(100))
    year_published = db.Column(db.DateTime)
    description = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    @staticmethod
    def last_added():
        return Guidebook.query.order_by(desc(Guidebook.id)).first()
