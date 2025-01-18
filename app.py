from flask import url_for, Flask, render_template, request, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from markupsafe import escape
from flask_login import login_required,current_user
import click
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY') or os.urandom(24)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'mysql://root:123@127.0.0.1:3306/student'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manger = LoginManager(app)
login_manger.login_view = 'login'


#创建管理员账户
@app.cli.command()    #这是flask一个装饰器，将函数注册为一个CLI命令，当运行flask admin ，flask会调研该函数
@click.option('--username', prompt=True, help='The username used to login.')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='The password used to login.')
def admin(username, password):
    """Create user."""
    db.create_all()

    user = User.query.first()
    if user is not None:
        click.echo('Updating user...')   #click.echo()是Click提供的函数，用于打印信息到心里话
        user.username = username
        user.set_password(password)  # 设置密码
    else:
        click.echo('Creating user...')
        user = User(username=username, name='Admin')
        user.set_password(password)  # 设置密码
        db.session.add(user)

    db.session.commit()  # 提交数据库会话
    click.echo('Done.')

# 添加初始电影数据的命令
@app.cli.command()
def forge():
    """Generate fake data."""
    db.create_all()
    
    # 全部电影数据
    movies = [
        {'title': '肖申克的救赎', 'year': '1994'},
        {'title': '霸王别姬', 'year': '1993'},
        {'title': '阿甘正传', 'year': '1994'},
        {'title': '泰坦尼克号', 'year': '1997'},
        {'title': '这个杀手不太冷', 'year': '1994'},
        {'title': '千与千寻', 'year': '2001'},
        {'title': '美丽人生', 'year': '1997'},
        {'title': '辛德勒的名单', 'year': '1993'},
        {'title': '盗梦空间', 'year': '2010'},
        {'title': '忠犬八公的故事', 'year': '2009'}
    ]
    
    for m in movies:
        movie = Movie(title=m['title'], year=m['year'])
        db.session.add(movie)
    
    db.session.commit()
    click.echo('Done.')

#模板上下文处理函数
@app.context_processor
def inject_user():
    user = User.query.first()
    return dict(user=user)


# 定义一个 User 模型类，该类继承自 db.Model，这是 SQLAlchemy 定义模型的基本方式。
class User(db.Model,UserMixin):
    # 指定该模型类对应的数据库表名为 'user'
    __tablename__ = 'user'  # 注意：表名应当符合数据库中实际的表名，通常表名是小写的。

    # 定义数据库表中的字段及其类型：
    id = db.Column(db.Integer, primary_key=True)  # 'id' 字段是主键，类型为整数（Integer）。
    name = db.Column(db.String(20))  # 'name' 字段是一个字符串，长度为 20。
    username = db.Column(db.String(20))  #创建一个用户名
    password_hash = db.Column(db.String(512))

    def set_password(self,password):   #用来设置密码的方法，接受密码作为参数
        self.password_hash = generate_password_hash(password)

    def validate_password(self,password):   #用于验证密码的方法，接受密码作为参数
        return check_password_hash(self.password_hash,password)  #返回的是一个布尔值


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer,primary_key = True)
    title = db.Column(db.String(60))
    year = db.Column(db.String(4))


@login_manger.user_loader   #这个装饰器告诉flask-login，当需要加载用户时，应该调用那个函数
def load_user(user_id):  #创建用户加载回调函数，接受用户ID作为参数
    user = User.query.get(int(user_id))  #用ID作为User模型的主键查询对应的用户
    return user #返回用户对象

@app.route('/login',methods = ['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('Invalid input.')
            return redirect(url_for('login'))
        user = User.query.first()

        #验证用户名和密码是否一致
        if username == user.username and user.validate_password(password):
            login_user(user)
            flash('Login success.')
            return redirect(url_for('index'))  #重定向到主页

        flash('Invalid username or password')  #如果验证失败，显示错误消息
        return redirect(url_for('login'))   #重新返回登陆页面
    
    # GET 请求时渲染登录页面
    return render_template('login.html')


#视图保护
@app.route('/movie/delete/<int:movie_id>',methods=['POST'])
@login_required #登陆保护，确保只有登陆的用户才能访问该视图，如果用户未登录，Flask-login会自动重定向到登陆页面
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash('Item deleted.')
    return redirect(url_for('index'))




#登出操作
@app.route('/logout')
@login_required #用于视图保护，后面会详细介绍 ，重定向到主页
def logout():
    logout_user()
    flash('再见')
    return redirect(url_for('index'))


#编辑电影条目
@app.route('/movie/edit/<int:movie_id>', methods=['GET', 'POST'])
@login_required
def edit(movie_id):
    movie = Movie.query.get_or_404(movie_id)

    if request.method == 'POST':  # 处理编辑表单的提交请求
        title = request.form['title']
        year = request.form['year']

        if not title or not year or len(year) != 4 or len(title) > 60:
            flash('Invalid input.')
            return redirect(url_for('edit', movie_id=movie_id))  # 重定向回对应的编辑页面

        movie.title = title  # 更新标题
        movie.year = year  # 更新年份
        db.session.commit()  # 提交数据库会话
        flash('Item updated.')
        return redirect(url_for('index'))  # 重定向回主页

    return render_template('edit.html', movie=movie)  # 传入被编辑的电影记录

@app.route('/',methods=['GET','POST'])
def index():
    if request.method == 'POST':
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
            
        title = request.form.get('title')
        year = request.form.get('year')
        
        if not title or not year or len(year) > 4 or len(title) > 60:
            flash('Invalid input.')
            return redirect(url_for('index'))
            
        try:
            movie = Movie(title=title, year=year)
            db.session.add(movie)
            db.session.commit()
            flash('Item created.')
        except Exception as e:
            db.session.rollback()
            flash(f'Error occurred while creating item: {str(e)}')
        return redirect(url_for('index'))

    movies = Movie.query.all()
    return render_template('index.html', movies=movies)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html',)

#支持设置用户名字
@app.route('/settings',methods=['GET','POST'])
@login_required
def settings():
    if request.method == 'POST':
        name = request.form['name']

        if not name or len(name) > 20:
            flash('Invalid input')
            return redirect(url_for('settings'))

        current_user.name = name
        db.session.commit()
        flash('Settings updated')
        return redirect(url_for('index'))
    return render_template('settings.html')




if __name__ == '__main__':
    app.run()

