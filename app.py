"""Blogly application."""

from flask import Flask, request, redirect, render_template, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Post, Tag

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///flask_blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'shhhhhh'


toolbar = DebugToolbarExtension(app)


connect_db(app)
db.create_all()


@app.route("/")
def home():
    posts = Post.query.order_by(Post.create_at.desc()).limit(5).all()
    return render_template("posts/homepage.html", posts=posts)


@app.errorhandler(404)
def page_not_found(e):

    return render_template('404.html'), 404

######user routes

@app.route("/users")
def list_users():
    """list of users and option to add user"""

    users = User.query.order_by(User.last_name, User.first_name).all()
    return render_template("users/index.html", users=users)


@app.route("/users/new", methods=["GET"])
def new_user_form():
    """create new user form"""
    return render_template('users/new.html')



@app.route("/users/new", methods=["POST"])
def users_new():
    """Handle form submission for new user"""

    new_user = User(
        first_name=request.form['first_name'],
        last_name=request.form['last_name'],
        image_url=request.form.get('image_url') or None
        )

    db.session.add(new_user)
    db.session.commit()
    flash(f"User {new_user.full_name} added.")

    return redirect("/users")


@app.route("/users/<int:user_id>")
def user_info(user_id):
    """show specific user info"""
    user = User.query.get_or_404(user_id)
    return render_template("users/show.html", user=user)


@app.route("/users/<int:user_id>/edit")
def edit_user(user_id):
    """form to edit user"""
    user = User.query.get_or_404(user_id)
    return render_template('users/edit.html', user=user)


@app.route('/users/<int:user_id>/edit', methods=["POST"])
def users_update(user_id):
    """Handle form submission and update user"""

    user = User.query.get_or_404(user_id)
    user.first_name = request.form['first_name']
    user.last_name = request.form['last_name']
    user.image_url = request.form['image_url']

    db.session.add(user)
    db.session.commit()
    flash(f"User {user.full_name} has been edited")

    return redirect("/users")


@app.route('/users/<int:user_id>/delete', methods=["POST"])
def user_delete(user_id):
    """Handle form submission for deleting an existing post"""

    user = User.query.get_or_404(user_id)

    db.session.delete(user)
    db.session.commit()
    flash(f"Post '{user.full_name} deleted.")

    return redirect("/users/")


# @app.route("/users/<int:user_id>/delete", methods=["POST"])
# def delete_user(user_id):
#     user = User.query.get_or_404(user_id)
#     db.session.delete(user)
#     db.session.commit()
#     flash(f"User {user.full_name} has been deleted")

#     return redirect("/users")


#######posts route

@app.route('/users/<int:user_id>/posts/new')
def posts_new_form(user_id):
    user = User.query.get_or_404(user_id)
    tags = Tag.query.all()
    return render_template ('posts/new.html', user=user, tags=tags)


@app.route('/users/<int:user_id>/posts/new', methods= ["POST"])
def posts_new(user_id):
    user = User.query.get_or_404(user_id)
    tag_ids = [int(num) for num in request.form.getlist("tags")]
    tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()
    new_post = Post(title=request.form['title'], content=request.form['content'], user=user, tags=tags)

    db.session.add(new_post)
    db.session.commit()
    flash(f"Post '{new_post.title}' has been added.")

    return redirect(f"/users/{user_id}")


@app.route('/posts/<int:post_id>')
def posts_show(post_id):

    post = Post.query.get_or_404(post_id)
    return render_template('posts/show.html', post=post)


@app.route('/posts/<int:post_id>/edit')
def posts_edit(post_id):

    post = Post.query.get_or_404(post_id)
    tags = Tag.query.all()
    return render_template('posts/edit.html', post=post, tags=tags)


@app.route('/posts/<int:post_id>/edit', methods=["POST"])
def posts_update(post_id):

    post = Post.query.get_or_404(post_id)
    post.title = request.form['title']
    post.content = request.form['content']
    tag_ids = [int(num) for num in request.form.getlist("tags")]
    post.tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()

    db.session.add(post)
    db.session.commmit()
    flash(f"Post '{post.title}' edited.")

    return redirect(f"/users/{post.user_id}")


@app.route('/posts/<int:post_id>/delete', methods=['POST'])
def delete_posts(post_id):

    post = Post.query.get_or_404(post_id)

    db.session.delete(post)
    db.session.commit()
    flash(f"Post '{post.title} deleted.")

    return redirect(f"/users/{post.user_id}")



######tags route

@app.route('/tags')
def list_tags():
    """list all tags"""
    tags = Tag.query.all()
    return render_template("tags/list.html", tags=tags)



@app.route('/tags/new')
def new_tag_form():
    """form to create a new tag"""
    posts= Post.query.all()
    return render_template('tags/new.html', posts=posts)



@app.route('/tags/new', methods=["POST"])
def tags_new():
    """post new tag to tags page"""


    post_ids = [int(num) for num in request.form.getlist("posts")]
    posts = Post.query.filter(Post.id.in_(post_ids)).all()
    new_tag = Tag(name = request.form['name'], posts=posts)
    db.session.add(new_tag)
    db.session.commit()
    flash(f"New tag: {new_tag.name} has been added.")

    return redirect("/tags")



@app.route('/tags/<int:tag_id>')
def show_tag(tag_id):
    """visit a specific tag"""
    tag = Tag.query.get_or_404(tag_id)
    return render_template('tags/show.html', tag=tag)



@app.route("/tags/<int:tag_id>/edit")
def edit_tag(tag_id):
    """edit a tag"""
    tag = Tag.query.get_or_404(tag_id)
    posts = Post.query.all()
    return render_template('tags/edit.html', tag=tag, posts=posts)


@app.route('/tags/<int:tag_id>/edit', methods=["POST"])
def tags_update(tag_id):
    """commit the tag to edit"""
    tag = Tag.query.get_or_404(tag_id)
    tag.name = request.form['name']
    post_ids = [int(num) for num in request.form.getlist("posts")]
    tag.posts = Post.query.filter(Post.id.in_(post_ids)).all()


    db.session.add(tag)
    db.session.commit()
    flash(f"Tag {tag.name} has beenb updated")

    return redirect("/tags")


@app.route('/tags/<int:tag_id>/delete', methods=['POST'])
def delete_tags(tag_id):
    """delete tag"""
    tag = Tag.query.get_or_404(tag_id)

    db.session.delete(tag)
    db.session.commit()
    flash(f"Tag: '{tag.name} has been deleted.")

    return redirect(f"/tags")