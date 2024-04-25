import os
import sys

import click
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

WIN = sys.platform.startswith('win')
if WIN:  # 如果是 Windows 系统，使用三个斜线
    prefix = 'sqlite:///'
else:  # 否则使用四个斜线
    prefix = 'sqlite:////'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭对模型修改的监控
# 在扩展类实例化前加载配置
db = SQLAlchemy(app)


@app.cli.command()
def forge():
    """Generate fake data."""
    db.create_all()

    # 全局的两个变量移动到这个函数内
    name = 'X-Blix'
    books = [
    {'title': '红楼梦', 'author': '曹雪芹'},
    {'title': '活着', 'author': '余华'},
    {'title': '百年孤独', 'author': '加西亚·马尔克斯 '},
    {'title': '飘', 'author': ' 玛格丽特·米切尔'},
    {'title': '三国演义（全二册）', 'author': '罗贯中'},
    {'title': '福尔摩斯探案全集（上中下）', 'author': '阿·柯南道尔'},
    {'title': '白夜行', 'author': '东野圭吾'},
    {'title': '小王子', 'author': ' 圣埃克苏佩里'},
    {'title': '野草', 'author': '鲁迅'},
    {'title': '沉默的大多数 ', 'author': '王小波'}
]

    user = User(name=name)
    db.session.add(user)
    for b in books:
        book = Book(title=b['title'], author=b['author'])
        db.session.add(book)

    db.session.commit()
    click.echo('Done.')



@app.cli.command()  # 注册为命令，可以传入 name 参数来自定义命令
@click.option('--drop', is_flag=True, help='Create after drop.')  # 设置选项
def initdb(drop):
    """Initialize the database."""
    if drop:  # 判断是否输入了选项
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')  # 输出提示信息




class User(db.Model):  # 表名将会是 user（自动生成，小写处理）
    id = db.Column(db.Integer, primary_key=True)  # 主键
    name = db.Column(db.String(20))  # 名字

class Book(db.Model):  # 表名将会是 book
    id = db.Column(db.Integer, primary_key=True)  # 主键
    title = db.Column(db.String(60))  # 标题
    author = db.Column(db.String(10))  # 作者

@app.route('/')
def index():
    user = User.query.first()
    books = Book.query.all()
    return render_template('index.html', user=user, books=books)