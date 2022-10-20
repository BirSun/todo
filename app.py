from flask import Flask, render_template, flash, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

us_id = 0
app = Flask(__name__)
# SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///todo.db"
app.config['SECRET_KEY'] = "my super secret key that no one is supposed to know"
db = SQLAlchemy(app)

class Lists(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    info = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(20), nullable=False)
    date_added = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    posts = db.relationship('Posts', backref='poster',cascade='all, delete')




    # Create a String
    def __repr__(self):
        return '<Name %r>' % self.name

class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    info = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(20), nullable=False)
    date_added = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    done = db.Column(db.Boolean, default=False)
    # Foreign Key To Link Lists (refer to primary key of the user)
    poster_id = db.Column(db.Integer, db.ForeignKey('lists.id'))



# Create a String
    def __repr__(self):
        return '<Name %r>' % self.name

db.create_all()
class PostForm(FlaskForm):
    name = StringField("Namn", validators=[DataRequired()])
    info = StringField("Info")
    category = StringField("Kategori")

    submit = SubmitField("Lägg till")


class ListForm(FlaskForm):
    name = StringField("Namn", validators=[DataRequired()])
    info = StringField("Info")
    category = StringField("Kategori")
    submit = SubmitField("Lägg till")

@app.route('/')
def index():
    our_lists = db.session.query(Lists).all()
    return render_template("listor.html", our_lists=our_lists)
   # return render_template("listor.html")

@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    name=None
    form = ListForm()
    if form.validate_on_submit():
        user = Lists.query.filter_by(info=form.info.data).first()
        print(Posts.poster_id)
        if user is None:
            lista= Lists(name=form.name.data, info=form.info.data, category=form.category.data)
            db.session.add(lista)
            db.session.commit()
#
        elif user is not None:
            flash("Email is not uniqe. Try again!")
            return redirect(url_for("add_user"))
        #name = form.name.data
        #print(user.email)
        us=form.name.data
        print(us)
#
        form.name.data = ''
        form.info.data = ''
        form.category.data = ''
        flash("Lista tillagd!")

    our_lists = Lists.query.order_by(Lists.date_added)
    return render_template("add_user.html",
                           form=form,
                           name=name,
                           our_lists=our_lists)

@app.route('/add_post/add/posts/<int:id>/<namn>', methods=['GET', 'POST'])
def add_post(id,namn):

    global us_id
    form = PostForm()
    list_id = request.args.get('id')
    print(list_id)
    if form.validate_on_submit():
        poster = id
        print(id)
        post = Posts(name=form.name.data, info=form.info.data, category=form.category.data, poster_id=poster)

        # Clear The Form
        form.name.data = ''
        form.info.data = ''
        # form.author.data = ''
        form.category.data = ''

        # Add post data to database
        db.session.add(post)
        db.session.commit()

        # Return a Message
        flash("Post har lagts till!")

    us_id=id
    print(f"{us_id} us_id")
    #name = form.name.data
    posts = db.session.query(Posts, Posts.id, Posts.name, Posts.info, Posts.category, Posts.done, Posts.poster_id).join(Lists).filter(id == Posts.poster_id).order_by(Posts.category).all()

        # Redirect to the webpage
    return render_template("add_post.html",
                form=form,
                namn=namn,
                posts=posts)

@app.route('/lista', methods=["GET", "POST"])

def lista():
    if request.method == "POST":
        # CREATE RECORD
        new_lista = Lists(
            name=request.form["name"],
            info=request.form["info"],
            category=request.form["category"]
        )
        db.session.add(new_lista)
        db.session.commit()

    our_lists = Lists.query.order_by(Lists.date_added)

    return render_template("listor.html",our_lists=our_lists)

@app.route('/edit_lista/<int:id>', methods=['GET', 'POST'])
def edit_lista(id):
    form = ListForm()
    name_to_update = Lists.query.get(id)
    print(id)
    if request.method == "POST":
        name_to_update.name = request.form['name']
        name_to_update.info = request.form['info']
        name_to_update.category = request.form['category']

        db.session.commit()

    return render_template("add_list.html", form=form, name_to_update=name_to_update, id=id)

@app.route("/delete_all/<int:id>")
def delete_all(id):
    list_to_delete = db.session.query(Lists).filter(Lists.id == id).first()
    print(f"{id}del_id")
    print(f"{list_to_delete}del_id")
    db.session.delete(list_to_delete)
    db.session.commit()
    return redirect(url_for('index'))

@app.route("/delete")
def delete():
   list_id = request.args.get('id')
   list_to_delete = Lists.query.get(list_id)
   db.session.delete(list_to_delete)
   print("deleted")
   db.session.commit()
   return redirect(url_for('index'))


@app.route('/delete_post/posts/<int:id>', methods=["GET", "POST"])
def delete_post(id):
    global us_id
    form = PostForm()
    #name = form.name.data

    if request.method == "GET":
        post_to_delete = Posts.query.get(id)
        db.session.delete(post_to_delete)
        # Posts.query.filter_by(id=id).delete()
        db.session.commit()

        print("deleted")
        print(us_id)
        flash("Post raderad!")
        our_lists = db.session.query(Lists).get(us_id)
        namn = our_lists.name
        # posts = db.session.query(Posts, Posts.id, Posts.name, Posts.info, Posts.category, Posts.done, Posts.poster_id).join(Lists).filter(id == Posts.poster_id).order_by(Posts.category).all()
        posts = db.session.query(Posts, Posts.id, Posts.name, Posts.info, Posts.category,Posts.done, Posts.poster_id).join(
            Lists).filter(us_id == Posts.poster_id).order_by(Posts.category).all()
        return render_template("add_post.html", form=form, posts=posts, namn=namn)

    else:

        poster = us_id
        post = Posts(name=form.name.data, info=form.info.data, category=form.category.data, poster_id=poster)

        # Clear The Form
        form.name.data = ''
        form.info.data = ''
        # form.author.data = ''
        form.category.data = ''

        # Add post data to database
        db.session.add(post)
        db.session.commit()

        # Return a Message
        flash("Post tillagd!")
        #name = form.name.data
        our_lists = db.session.query(Lists).get(us_id)
        namn = our_lists.name
        # posts = db.session.query(Posts, Posts.id, Posts.name, Posts.info, Posts.category, Posts.done, Posts.poster_id).join(Lists).filter(id == Posts.poster_id).order_by(Posts.category).all()
        posts = db.session.query(Posts, Posts.id, Posts.name, Posts.info, Posts.category,Posts.done, Posts.poster_id).join(
            Lists).filter(us_id == Posts.poster_id).order_by(Posts.category).all()

        return render_template("add_post.html", form=form, posts=posts, namn=namn)

@app.route("/complete/<int:id>", methods=['GET', 'POST'])
def complete(id):
    form = PostForm()
    if request.method == "GET":
        check = Posts.query.filter_by(id=id).first()
        print(check.done)
        check.done = not check.done
        print("true to false")
        print(check.done)
        db.session.commit()
        posts = db.session.query(Posts, Posts.id, Posts.name, Posts.info, Posts.category, Posts.done, Posts.poster_id).join(
        Lists).filter(us_id == Posts.poster_id).order_by(Posts.category).all()

        our_lists = db.session.query(Lists).get(us_id)
        namn = our_lists.name
        return render_template("add_post.html",posts=posts ,form=form, namn=namn)
    else:
        poster = us_id
        post = Posts(name=form.name.data, info=form.info.data, category=form.category.data, poster_id=poster)

        # Clear The Form
        form.name.data = ''
        form.info.data = ''
        # form.author.data = ''
        form.category.data = ''

        # Add post data to database
        db.session.add(post)
        db.session.commit()

        # Return a Message
        flash("Post tillagd!")
        #name = form.name.data
        our_lists = db.session.query(Lists).get(us_id)
        namn = our_lists.name

        posts = db.session.query(Posts, Posts.id, Posts.name, Posts.info, Posts.category, Posts.done,
                                 Posts.poster_id).join(
            Lists).filter(us_id == Posts.poster_id).order_by(Posts.category).all()

        return render_template("add_post.html", form=form, posts=posts, namn=namn)


@app.route("/complete_false/<int:id>", methods=['GET', 'POST'])
def complete_false(id):
    form = PostForm()
    if request.method == "GET":
        not_check = Posts.query.filter_by(id=id).first()

        print(id)
        print(not_check.done)
        not_check.done = True
        print(not_check.done)
        print("false to true")
        db.session.commit()
        our_lists = db.session.query(Lists).get(us_id)
        namn = our_lists.name

        posts = db.session.query(Posts, Posts.id, Posts.name, Posts.info, Posts.category, Posts.done, Posts.poster_id).join(
        Lists).filter(us_id == Posts.poster_id).order_by(Posts.category).all()

        return render_template("add_post.html",posts=posts,form=form, namn=namn)
    else:
        poster = us_id
        post = Posts(name=form.name.data, info=form.info.data, category=form.category.data, poster_id=poster)

        # Clear The Form
        form.name.data = ''
        form.info.data = ''
        # form.author.data = ''
        form.category.data = ''

        # Add post data to database
        db.session.add(post)
        db.session.commit()

        # Return a Message
        flash("Post tillagd!")
        #name = form.name.data
        our_lists = db.session.query(Lists).get(us_id)
        namn = our_lists.name

        posts = db.session.query(Posts, Posts.id, Posts.name, Posts.info, Posts.category, Posts.done,
                                 Posts.poster_id).join(
            Lists).filter(us_id == Posts.poster_id).order_by(Posts.category).all()

        return render_template("add_post.html", form=form, posts=posts, namn=namn)


"""
@app.route('/delete_post/posts/<int:id>', methods=["GET", "POST"])
def delete_post(id):
    global us_id
    form = PostForm()
    name = form.name.data

    if request.method == "GET":
        post_to_delete = Posts.query.get(id)
        db.session.delete(post_to_delete)
        # Posts.query.filter_by(id=id).delete()
        db.session.commit()

        print("deleted")
        print(us_id)
        flash("Blog Post Deleted Successfully!")

        our_lists = db.session.query(Lists).get(us_id)
        namn = our_lists.name

        posts = db.session.query(Posts, Posts.id, Posts.name, Posts.info, Posts.category, Posts.done, Posts.poster_id).join(Lists).filter(id == Posts.poster_id).all()
        return render_template("add_post.html", form=form, posts=posts, namn=namn)

    else:

        poster = us_id
        post = Posts(name=form.name.data, info=form.info.data, category=form.category.data, poster_id=poster)

        # Clear The Form
        form.name.data = ''
        form.info.data = ''
        # form.author.data = ''
        form.category.data = ''

        # Add post data to database
        db.session.add(post)
        db.session.commit()

        # Return a Message
        flash("Blog Post Submitted Successfully!")
        name = form.name.data
        our_lists = db.session.query(Lists).get(us_id)
        namn = our_lists.name

        posts = db.session.query(Posts, Posts.id, Posts.name, Posts.info, Posts.category, Posts.done, Posts.poster_id).join(Lists).filter(id == Posts.poster_id).all()

        return render_template("add_post.html", form=form, posts=posts, namn=namn)
"""

"""
#@app.route('/delete_post/posts/<int:id>', methods=['GET', 'POST'])
@app.route('/delete_post/posts/<int:id>', methods=['GET', 'POST'])
def delete_post(id):
   global us_id
   form = PostForm()

   print(f"{id} post")
   print(f"{us_id} id!")

   ###
   user_to_delete = Posts.query.get(id)
   db.session.delete(user_to_delete)
   #to_delete = Posts.query.filter_by(id=id).first()
   #db.session.delete(to_delete)
   #post_to_delete = Posts.query.get(id)
   #db.session.delete(post_to_delete)
   db.session.commit()

   print("deleted")
   print(us_id)
   name = form.name.data


   #namn = db.session.query(Lists).get(us_id)
   #nam =  namn
   #print(nam)
   #our_lists = Lists.query.all()

   our_lists = db.session.query(Lists).get(us_id)
   namn = our_lists.name
   print(namn)
   cat = our_lists.id
   print(f"{cat} cat")

   posts = db.session.query(Posts, Posts.id, Posts.name, Posts.info, Posts.category, Posts.done, Posts.poster_id).join(Lists).filter(us_id == Posts.poster_id).order_by(Posts.category).all()
   return render_template("add_post.html",
                          form=form,
                          name=name,
                          posts=posts)
  #return redirect(url_for('add_post', posts=posts, id=id, namn=namn, form=form, name=name))
   #return render_template("add_post.html", form=form, posts=posts, name=name, namn=namn)
   #return render_template("add_post.html", form=form, posts=posts, name=name, namn=namn)
   #return redirect(url_for('add_post',id=id, namn=namn, posts=posts, form=form, name=name))
"""
"""
@app.route("/complete/<int:id>", methods=['GET', 'POST'])
def complete(id):
    form = PostForm()
    check = Posts.query.filter_by(id=id).first()

    print(check.done)
    check.done = not check.done
    print("true to false")
    print(check.done)
    db.session.commit()
    posts = db.session.query(Posts, Posts.id, Posts.name, Posts.info, Posts.category, Posts.done, Posts.poster_id).join(Lists).filter(us_id == Posts.poster_id).all()
   # name = form.name.data
    our_lists = db.session.query(Lists).get(us_id)
    namn = our_lists.name

    #return redirect(url_for("add_post",posts=posts, form=form, id=id, namn=namn))
    #return redirect(url_for("add_post", id=id, namn=namn))
    return render_template("add_post.html",posts=posts ,form=form, namn=namn)

@app.route("/complete_false/<int:id>", methods=['GET', 'POST'])
def complete_false(id):
    form = PostForm()
    not_check = Posts.query.filter_by(id=id).first()

    print(id)
    print(not_check.done)
    not_check.done = True
    print(not_check.done)
    print("false to true")
    db.session.commit()
    our_lists = db.session.query(Lists).get(us_id)
    namn = our_lists.name
    #name = form.name.data
    posts = db.session.query(Posts, Posts.id, Posts.name, Posts.info, Posts.category, Posts.done, Posts.poster_id).join(Lists).filter(us_id == Posts.poster_id).all()
    #return redirect(url_for("add_post",posts=posts, form=form, id=id, namn=namn))
    #return redirect(url_for("add_post", id=id, namn=namn))
    return render_template("add_post.html",posts=posts,form=form, namn=namn)
"""

@app.route('/posts/<int:id>/<name>')
def posts(id,name):
    print(name)

   #if id == post.poster_id:


   # posts = Posts.query(Posts.date_added).filter(id == Posts.poster_id)

    #posts = Posts.query(Posts.date_added).filter(post.poster_id == 2)
    #print(post.poster_id)
    #posts = Posts.query.filter_by(id == Posts.poster_id)
    #posts = session.query(Posts).filter(posts.name.like('K%')).all()
 #    posts = Posts.query.filter_by(Posts.poster_id = "Mat").all()
    #posts = Posts.query.filter_by((Posts.category = 'Mat')).first()

  #       posts = Posts.query.order_by(Posts.date_added).all()


    #posts = Posts.query.filter_by(id=2).all()


    #posts = Posts.query.filter_by(Posts.poster_id=id).first()

    #postid = post.poster_id
    #posts = Posts.query.get_or_404(id)
    #postid = Posts.poster_id
    posts = db.session.query(Posts, Posts.name, Posts.info, Posts.category).join(Lists).filter(id == Posts.poster_id).all()
    for post in posts:

#user = db.session.query(User, Role.index).join(Role).filter(User.email == form.email.data).first()

     return render_template('post.html', posts=posts, name=name)


"""
        if id == post.poster_id:
            print(id)
            print(post.poster_id)
            print(post)
            poster = post
            postid=post.poster_id
            print(postid)
            #return render_template('post.html', posts=posts, postid=postid)
            """


#@app.errorhandler(404)
#def page_not_found(e):
	#return render_template("404.html"), 404



if __name__ == '__main__':
    app.run(debug=False)
