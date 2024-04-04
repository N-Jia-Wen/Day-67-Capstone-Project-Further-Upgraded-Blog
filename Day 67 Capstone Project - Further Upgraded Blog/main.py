from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
from datetime import date


app = Flask(__name__)
ckeditor = CKEditor(app)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)


# CREATE DATABASE
class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
database = SQLAlchemy(model_class=Base)
database.init_app(app)


# CONFIGURE TABLE
class BlogPost(database.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)


with app.app_context():
    database.create_all()


# WTForm:
class Form(FlaskForm):
    title = StringField(label="Blog Post Title", validators=[DataRequired()])
    subtitle = StringField(label="Subtitle", validators=[DataRequired()])
    author = StringField(label="Your Name", validators=[DataRequired()])
    img_url = StringField(label="Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField(label="Blog Content", validators=[DataRequired()])
    submit = SubmitField(label="Submit Post")


@app.route('/')
def get_all_posts():
    posts = database.session.execute(database.select(BlogPost)).scalars().all()
    return render_template("index.html", all_posts=posts)


@app.route('/blog-post/<int:post_id>')
def show_post(post_id):
    requested_post = database.get_or_404(BlogPost, post_id)
    return render_template("post.html", post=requested_post)


@app.route('/new-post', methods=["GET", "POST"])
def add_new_post():
    if request.method == "GET":
        add_post_form = Form()
        title = "New Post"
        return render_template("make-post.html", form=add_post_form, title=title)

    elif request.method == "POST":
        new_post = BlogPost(
            title=request.form.get("title"),
            subtitle=request.form.get("subtitle"),
            date=date.today().strftime("%B %d, %Y"),
            body=request.form.get("body"),
            author=request.form.get("author"),
            img_url=request.form.get("img_url")
        )
        database.session.add(new_post)
        database.session.commit()
        return redirect(url_for('get_all_posts'))


@app.route('/edit-post/<int:post_id>', methods=["GET", "POST"])
def edit_post(post_id):
    if request.method == "GET":
        requested_post = database.get_or_404(BlogPost, post_id)
        edit_post_form = Form(
            title=requested_post.title,
            subtitle=requested_post.subtitle,
            img_url=requested_post.img_url,
            author=requested_post.author,
            body=requested_post.body
        )
        title = "Edit Post"
        return render_template("make-post.html", form=edit_post_form, title=title)

    elif request.method == "POST":
        post_to_edit = database.get_or_404(BlogPost, post_id)
        post_to_edit.title = request.form.get("title")
        post_to_edit.subtitle = request.form.get("subtitle")
        post_to_edit.body = request.form.get("body")
        post_to_edit.author = request.form.get("author")
        post_to_edit.img_url = request.form.get("img_url")
        database.session.commit()
        return redirect(url_for('show_post', post_id=post_id))


@app.route('/delete/<post_id>')
def delete_post(post_id):
    post_to_delete = database.get_or_404(BlogPost, post_id)
    database.session.delete(post_to_delete)
    database.session.commit()
    return redirect(url_for('get_all_posts'))

# Below is the code from previous lessons. No changes needed.
@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(port=5003)
