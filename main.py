from flask import Flask, request, redirect, render_template, flash
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://Blogz:blogz@localhost:8889/Blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

#creating the columns for my database

#used for creating the blog database
class Blog(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(480))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

#used for creating the user database
class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(120), unique = True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref = 'owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

#validation definitions
def is_length(text):
    len_check = len(text)
    if len_check < 3:
        return False
    else:
        return True

def is_same(text1, text2):
    if text1 != text2:
        return False
    else:
        return True




#default page that loads when first going to the site
@app.route('/')
def index():
    blogs = Blog.query.order_by(Blog.id.desc()).all()
    return render_template('main_blog.html', title = "Build a blog", blogs = blogs)

#main page in the site
@app.route('/blog')
def blogpage():
    #path to open a blog on a seperate page
    blog_id = request.args.get('id')
    if (blog_id):
        blog = Blog.query.get(blog_id)
        return render_template('single_blog.html', blog = blog)
    else:
        #displaying all created blogs in order of newest to oldest
        blogs = Blog.query.order_by(Blog.id.desc()).all()
        return render_template('main_blog.html' ,title = "Build a blog", blogs = blogs)

#new blog post page
@app.route('/newpost', methods = ['POST', 'GET'])
def newpost():
    if request.method == 'POST':
        title = request.form['blogtitle']
        body = request.form['blogtext']
        title_error = ''
        body_error = ''
        error_count = 0

        #test to validate if anything was entered and return an error if not
        if title == '':
            title_error = 'Please enter a title'
            error_count += 1
        if body == '':
            body_error = 'Please enter a blog'
            error_count += 1
        if error_count > 0:
            return render_template('new_blog.html', title = 'New Blog Entry', title_error = title_error,
                body_error = body_error)
        #creating a new blog post
        new_entry = Blog(title, body)
    
        db.session.add(new_entry)
        db.session.commit()
        url = "/blog?id=" + str(new_entry.id)
        return redirect(url)
    else:
        return render_template('new_blog.html', title = 'New Blog Entry')

#new user signup
@app.route('/signup', methods = ['POST', 'GET])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        if username == '':
            flash('Please enter in a Username', 'error')
            return render_template('signup.html', title = 'Signup')
        else:
            if not is_length(username):
                flash('Username needs to be greater than 3 characters in length', 'error')
                return render_template('signup.html', title = 'Signup')

        if password == '':
            flash('Please enter a Password', 'error')
            return render_template('signup.html', title = 'Signup', username = username)
        else:
            if not is_length(password):
                flash('Password needs to be greater than 3 characters in length', 'error')
                return render_template('signup.html', title = 'Signup', username = username)

        if not is_same(password, verify):
            flash('Passwords do not match', 'error')
            return render_template('signup.html', title = 'Signup', username = username)
        
        existing_user = User.query.filter_by(username = username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        else:
            flash('Username already exists', 'error')
            return render_template('signup.html', title = 'Signup')

#login page
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username = username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/newpost')
        else:
            flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html', title = 'Login')

#@app.route('/logout', methods = ['POST'])
#def logout():
# TODO finish the logout route



if __name__ == '__main__':
    app.run()
