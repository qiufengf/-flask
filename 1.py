from flask import Flask
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

# 创建数据库表
@app.before_request
def create_tables():
    db.create_all()  # 创建表



# 启动应用
if __name__ == '__main__':
    app.run(debug=True)
