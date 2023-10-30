from  flask import Flask
from flask import request, redirect, url_for
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'static/posts/images/'

app=Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy()
#  configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.sqlite"
db.init_app(app)

@app.route('/hello')
def hello():
    return '<h1>Hello</h1>'
@app.route('/hello/<user>')
def hello_user(user):

    return f'<h1>Hello {user}</h1>'


posts=[
    {'id': 1, 'title': 'sport', 'body': 'match res with','image': ''},
    {'id': 2, 'title': 'policy', 'body': 'world policy', 'image':''},
    {'id': 3, 'title': 'health', 'body': 'world health', 'image':''}
]

@app.route('/posts_index')
def get_all_posts():
    return posts

@app.route('/post/<int:id>')
def get_post(id):
    # return posts[id-1]
    filter_post=filter(lambda post: post['id']==id, posts)
    filter_post=list(filter_post)
    if filter_post:
        return filter_post[0]
    return '<h1>post not found</h1>'
   
# @app.route('/land')
# def landing():
#     return render_template('index.html',posts=posts)


@app.errorhandler(404)
def not_found(error):
    return render_template('notfound.html')


from views import test
app.add_url_rule('/test1',view_func=test,endpoint='testview')


# models 
class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    body = db.Column(db.String)
    image = db.Column(db.String,nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __str__(self):
        return f'{self.title}'
    
    @classmethod
    def get_all_posts(cls):
        return cls.query.all()
    @classmethod
    def get_speacific_post(cls,id):
        return cls.query.get_or_404(id)
    

@app.route('/posts',endpoint='posts.index')
def post_index():
    posts=Post.get_all_posts()
    return render_template('posts/index.html', posts=posts)

@app.route('/posts/<int:id>',endpoint='posts.show')
def show_post(id):
    post=Post.get_speacific_post(id)
    # post=Post.query.get_or_404(id)

    return render_template('posts/show.html',post=post)


# create a new post

@app.route('/create', methods=['GET', 'POST'], endpoint='posts.create')
def create():
    if request.method == 'POST':
        post = Post(
            title=request.form['title'],
            body=request.form['body'],
        
        )

        # Handle image upload
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_image(file.filename):
                filename = secure_filename(file.filename)

                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

                file.save(file_path)
                post.image = filename  # Update the post's image 
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('posts.index'))

    return render_template('posts/create.html')



ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}

def allowed_image(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS


# edit


@app.route('/edit/<int:id>', methods=['GET', 'POST'], endpoint='posts.edit')
def edit(id):
    post = Post.query.get(id)

    if not post:
        return "Post not found", 404

    if request.method == 'POST':
        post.title = request.form['title']
        post.body = request.form['body']

        # Handle image upload
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_image(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                post.image = filename  # Update the post's image

        db.session.commit()
        return redirect(url_for('posts.index'))

    return render_template('posts/edit.html', post=post)

# delete post
@app.route('/posts/delete/<int:id>', endpoint='posts.delete')
def delete(id):
    post = Post.query.get_or_404(id)

    # Remove the product's image file, if it exists
    if post.image:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], post.image)
        if os.path.exists(image_path):
            os.remove(image_path)

    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('posts.index'))



if __name__ == '__main__':
    app.run(debug=True)