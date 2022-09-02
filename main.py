from plistlib import Data

from dominate.svg import use
from flask import Flask, render_template, redirect, url_for, flash,request, send_from_directory,Response , abort
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor, upload_success, upload_fail
import datetime
import os
import psycopg2
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_authorize import Authorize
from functools import wraps
from flask_bcrypt import Bcrypt
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from flask_authorize import RestrictionsMixin, AllowancesMixin
from flask_authorize import PermissionsMixin
import smtplib, ssl
from werkzeug.utils import secure_filename
import base64
from forms import CreateDataPostForm, CreatePostForm, LoginForm, ContactForm



#https://colorhunt.co/palette/6e85b7b2c8dfc4d7e0f8f9d7 PALETTE

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")

DATABASE_URL = os.environ['DATABASE_URL']

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(DATABASE_URL)

conn = psycopg2.connect(DATABASE_URL, sslmode='require')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

ckeditor = CKEditor(app)

bootstrap = Bootstrap5(app)

login_manager = LoginManager()
login_manager.init_app(app)


smtp_server = "smtp.gmail.com"
port = 587  # For starttls

# Create a secure SSL context
context = ssl.create_default_context()




class User(UserMixin,db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), unique=True, nullable=False)

class DsPost(db.Model):
    __tablename__ = "dspost"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), unique=False, nullable=False)
    author = db.Column(db.String(120), unique=False, nullable=False)
    body = db.Column(db.Text, unique=False, nullable=False)
    img_url = db.Column(db.String(120), unique=False, nullable=False)
    date = db.Column(db.String(80), unique=False, nullable=False)
    imgs = db.relationship("Img",backref="dspost",lazy = True)

class Post(db.Model):
    __tablename__ = "blog_post"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), unique=False, nullable=False)
    body = db.Column(db.Text, unique=False, nullable=False)
    subbody = db.Column(db.String(120), unique=False, nullable=True)
    author = db.Column(db.String(120), unique=False, nullable=False)
    img_url = db.Column(db.String(120), unique=False, nullable=False)
    date = db.Column(db.String(80), unique=False, nullable=False)

class Img(db.Model):
    __tablename__ = "images"
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Text, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('dspost.id'), unique=False, nullable=False)
    mimetype = db.Column(db.Text, nullable=False)
    name =  db.Column(db.Text, nullable = False)




db.create_all()

def admin_only(f):
    @wraps(f)
    def route(*args,**kwargs):
            if current_user.id == 1:
                return f(*args,**kwargs)
            else:
                return abort(403)
    return route

@app.route("/")
def main():
    blog_posts = Post.query.all()
    return render_template("home.html",blog_posts = blog_posts)


@app.route("/home")
def home():
    blog_posts = Post.query.all()
    return render_template("home.html",blog_posts = blog_posts)



@app.route("/ds_add_post",methods= ["GET","POST"])
@admin_only
def ds_add_post():
    form = CreateDataPostForm()

    if(request.method == "POST"):

                new_ds_post = DsPost(title = request.form["title"],
                                     body = request.form["body"],
                                     img_url = request.form["img_url"],
                                     author = "Gokay",
                                     date=datetime.datetime.now().strftime("%b %d"))

                db.session.add(new_ds_post)
                db.session.commit()

                return redirect(url_for("dsPage"))

    return render_template("ds_add_post.html",form = form)


@app.route("/ds_edit")
@admin_only
def ds_edit():

    return render_template("ds_edit_post.html")


@app.route("/data-science")
def dsPage():
    dsPosts = DsPost.query.all()
    #decode images
    for ds in dsPosts:
        for img in ds.imgs:
            print("BEFORE DECODING")

            print(str(img.data))


    return render_template("portfolio_ds.html",dsPosts = dsPosts)

@app.route("/upload-image/<int:post_id>", methods=["GET","POST"])
@admin_only
def UploadImage(post_id):

    if request.method == "POST":
        if request.files:
            image = request.files["image"]
            filename = secure_filename(image.filename)
            data = base64.b64encode(image.read()).decode("utf-8")
            mimetype = image.mimetype
            img = Img(data = data,mimetype = mimetype,name = filename,post_id = post_id)
            db.session.add(img)
            db.session.commit()

            return redirect(url_for("dsPage"))


    return render_template("portfolio_ds.html")




@app.route("/posts/<int:post_id>")
def showPost(post_id):
    current_post = Post.query.filter_by(id = post_id).first()
    return render_template("postPage.html",post = current_post)


@app.route("/addPost",methods=["GET","POST"])
@admin_only
def add_post():
    form = CreatePostForm()
    if request.method == "POST":
        new_blog_post = Post(title=request.form["title"],
                             body=request.form.get('ckeditor'),
                             img_url=request.form["img_url"],
                             subbody= request.form["subtitle"],
                             author="Gokay",
                             date=datetime.datetime.now().strftime("%b %d"))

        db.session.add(new_blog_post)
        db.session.commit()

        return redirect(url_for("home"))

    return render_template("add_post.html",form = form)

@app.route("/blog_post_delete/<int:post_id>")
@admin_only
def delete_blog_post(post_id):

    Post.query.filter_by(id = post_id).delete()
    db.session.commit()


    return redirect(url_for("home"))


@app.route("/ds_post_delete/<int:post_id>")
@admin_only
def delete_ds_post(post_id):

     DsPost.query.filter_by(id = post_id).delete()
     Img.query.filter_by(post_id = post_id).delete()
     db.session.commit()

     return redirect(url_for("dsPage"))



@app.route('/admin_panel', methods=['GET', 'POST'])
def admin_panel():
    form = LoginForm()

    if (not User.query.filter_by(id =1).first()):
        admin_user = User(username="gokay1904",
                          password=generate_password_hash("adgmina123!", method='pbkdf2:sha256', salt_length=8))
        db.session.add(admin_user)
        db.session.commit()

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username = username).first()
        if user:
            if (check_password_hash(user.password, password)):
                User.query.filter_by(username = username).first()
                login_user(user)
                print("Hey")
                return redirect(url_for("home"))
            else:
                print("BBHey")
                flash("Incorrect Password")
                return redirect(url_for("admin_panel"))
        else:
            flash("Incorrect Username")
            return redirect(url_for("admin_panel"))

    return render_template("adminpanel.html", form = form)


@app.route("/allposts")
def showAllPosts():
    blog_posts = Post.query.all()
    print(blog_posts)
    return render_template("allposts.html",posts = blog_posts)

@app.route("/about")
def about():

    return render_template("about.html")

@app.route("/contact",methods = ["GET","POST"])
def contact():
   contact_form = ContactForm()
   # receiver_email = "reciever@gmail.com"
   # sender_email = "my@gmail.com" #Email for sending the message to owner's email
   # password = input("Type your password and press enter: ")
   # # Try to log in to server and send email
   # try:
   #     server = smtplib.SMTP(smtp_server, port)
   #     server.ehlo()  # Can be omitted
   #     server.starttls(context=context)  # Secure the connection
   #     server.ehlo()  # Can be omitted
   #     server.login(sender_email, password)
   #     # TODO: Send email here
   #     server.sendmail(sender_email, receiver_email, message)
   # except Exception as e:
   #     # Print any error messages to stdout
   #     print(e)
   # finally:
   #     server.quit()


   return render_template("contact.html",form = contact_form)



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


if __name__ == '__main__':
    app.run(debug=True)