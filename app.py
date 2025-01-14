from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

# 配置数据库
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:123@127.0.0.1:3306/first'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 禁用修改追踪

# 初始化数据库
db = SQLAlchemy(app)

# 定义模型类，手动指定表名
class User(db.Model):
    __tablename__ = 'users'  # 手动指定表名
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))  # 用户名

class Movie(db.Model):
    __tablename__ = 'movies'  # 手动指定表名
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20))  # 电影标题
    year = db.Column(db.String(4))  # 电影年份

@app.route('/')
def index():
    user = User.query.first()
    movies = Movie.query.all()
    return render_template('index.html',movies=movies)

@app.context_processor
def inject_user():
    user = User.query.first()
    print(user)
    return dict(user=user)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'),404



# 启动应用
if __name__ == '__main__':

    app.run(debug=True)
