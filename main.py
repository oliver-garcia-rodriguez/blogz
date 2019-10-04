from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:build-a-blog@localhost:3306/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1200))

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/')
def index():

    return redirect('/blog')

@app.route('/blog')
def blog():
    blog_posts = Blog.query.all()

    blog_id = request.args.get('id')
    if blog_id:
        blog_post = Blog.query.filter_by(id = blog_id).first()
        return render_template('single.html', title="Build a Blog", blog_post=blog_post)
    
    return render_template('blog.html', title="Build a Blog", blog_posts=blog_posts)

@app.route('/newpost', methods=['GET', 'POST'])
def newpost():
    title_error = ''
    body_error = '' 

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']    

        if title == '':
            title_error = 'Please fill in the title'

        if body == '':
            body_error = 'Please fill in the body'

        if title != '' and body != '':
            new_blog_post = Blog(title, body)
            db.session.add(new_blog_post)
            db.session.commit()
            return redirect('/blog?id='+str(new_blog_post.id))

    return render_template('newpost.html',title="Add a Blog Entry", title_error=title_error, body_error=body_error)

if __name__ == '__main__':
    app.run()