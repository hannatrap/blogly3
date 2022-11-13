import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

DEFAULT_IMAGE_URL = "https://www.freeiconspng.com/uploads/icon-user-blue-symbol-people-person-generic--public-domain--21.png"




class User(db.Model):
    """user"""

    __tablename__= 'users'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.Text, nullable=False)
    last_name = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.Text, nullable=False, default = DEFAULT_IMAGE_URL)

    posts = db.relationship("Post", backref="user", cascade="all, delete-orphan")

    @property
    def full_name(self):
        """combine into full name"""
        return f"{self.first_name} {self.last_name}"



class Post(db.Model):
    """post model"""

    __tablename__="posts"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False)
    create_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    @property
    def friendly_date(self):
        """create a nicely formated date for posts"""
        return self.create_at.strftime("%a %b %-d %Y, %-I:%M %p")




class Tag(db.Model):
    """tags"""

    __tablename__="tags"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, unique=True, nullable=False)

    posts = db.relationship(
        'Post', secondary="posttags", backref="tags")


class PostTag(db.Model):
    """joins post and tag together"""

    __tablename__="posttags"

    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), primary_key=-True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'), primary_key=-True)

def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)