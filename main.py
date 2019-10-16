from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy
from hashutils import make_pw_hash, check_pw_hash

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:3306/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = '(w2#+Bu3Pye_wQ,b'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1200))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    pw_hash = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.pw_hash = make_pw_hash(password)

@app.before_request
def require_login():
    allowed_routes = ['index', 'blog', 'login', 'logout', 'signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users = users)

@app.route('/blog')
def blog():
    blog_posts = Blog.query.all()
    blog_id = request.args.get('id')
    if blog_id:
        blog_post = Blog.query.filter_by(id = blog_id).first()
        owner = User.query.filter_by(id=blog_post.owner_id).first()
        return render_template('single.html', blog_post=blog_post, owner = owner)

    users = User.query.all()
    username = request.args.get('user')
    owner = User.query.filter_by(username=username).first()
    if owner:
        blog_posts = Blog.query.filter_by(owner=owner).all()
        return render_template('singleUser.html', blog_posts=blog_posts, User = User)
    
    return render_template('blog.html', blog_posts=blog_posts, User = User)

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        username_error = False

        password = request.form['password']
        password_error = False

        user = User.query.filter_by(username=username).first()
        
        if not user:
            username_error = True
            return render_template('login.html', username_error = username_error)
            
        else:
            if check_pw_hash(password, user.pw_hash):
                session['username'] = username
                return redirect('/blog/newpost')
            else:
                password_error = True
                return render_template('login.html', password_error = password_error)

    return render_template('login.html')

@app.route('/logout')
def logout():
    if 'username' in session:
        del session['username']
    return redirect('/blog')

@app.route('/signup', methods=['POST', 'GET'])
def signup():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify_password = request.form['verify-password']

        username_error = False
        # TODO - validate username data
        if len(username) < 3 or len(username) > 20 or ' ' in username:
            username_error = True 

        password_error = False
        # TODO - validate password data
        if len(password) < 3 or len(password) > 20 or ' ' in password:
            password_error = True

        verify_password_error = False

        if verify_password != password:
            verify_password_error = True

        if username_error == True or password_error == True or verify_password_error == True:
            return render_template('signup.html', username = username, username_error = username_error, password_error = password_error, verify_password_error = verify_password_error)

        existing_username = User.query.filter_by(username=username).first()
        existing_username_error = False

        if not existing_username:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/blog/newpost')
        else:
            #TODO - error message
            existing_username_error = True
            return render_template('signup.html', existing_username_error = existing_username_error)

    return render_template('signup.html')

@app.route('/blog/newpost', methods=['GET', 'POST'])
def newpost():
    if request.method == 'POST':
        title = request.form['title']
        title_error = False

        body = request.form['body']
        body_error = False  

        if title == '':
            title_error = True

        if body == '':
            body_error = True

        if title_error == True or body_error == True:
            return render_template('newpost.html', title_error = title_error, body_error = body_error)
        else:
            owner = User.query.filter_by(username = session['username']).first()
            new_blog_post = Blog(title, body, owner)
            db.session.add(new_blog_post)
            db.session.commit()
            return redirect('/blog?id='+str(new_blog_post.id))

    return render_template('newpost.html')

if __name__ == '__main__':
    app.run()