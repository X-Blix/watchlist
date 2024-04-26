import os
import sys

import click
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

from flask import request, url_for, redirect, flash


WIN = sys.platform.startswith('win')
if WIN:  # 如果是 Windows 系统，使用三个斜线
    prefix = 'sqlite:///'
else:  # 否则使用四个斜线
    prefix = 'sqlite:////'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭对模型修改的监控

app.config['SECRET_KEY'] = 'dev'  #设置签名所需的密钥

# 在扩展类实例化前加载配置
db = SQLAlchemy(app)



@app.cli.command()  # 注册为命令，可以传入 name 参数来自定义命令
@click.option('--drop', is_flag=True, help='Create after drop.')  # 设置选项
def initdb(drop):
    """Initialize the database."""
    if drop:  # 判断是否输入了选项
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')  # 输出提示信息

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


class User(db.Model):  # 表名将会是 user（自动生成，小写处理）
    id = db.Column(db.Integer, primary_key=True)  # 主键
    name = db.Column(db.String(20))  # 名字

class Book(db.Model):  # 表名将会是 book
    id = db.Column(db.Integer, primary_key=True)  # 主键
    title = db.Column(db.String(60))  # 标题
    author = db.Column(db.String(10))  # 作者


@app.context_processor
def inject_user():  # 函数名可以随意修改
    user = User.query.first()
    return dict(user=user)  # 需要返回字典，等同于 return {'user': user}

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':  # 判断是否是 POST 请求
        # 获取表单数据
        title = request.form.get('title')  # 传入表单对应输入字段的 name 值
        author = request.form.get('author')
        # 验证数据

        if not title or not author:
            flash('Invalid input.')  # 显示错误提示
            return redirect(url_for('index'))  # 重定向回主页
        
        # 保存表单数据到数据库
        book = Book(title=title, author=author)  # 创建记录
        db.session.add(book)  # 添加到数据库会话
        db.session.commit()  # 提交数据库会话
        flash('Item created.')  # 显示成功创建的提示
        return redirect(url_for('index'))  # 重定向回主页

    books = Book.query.all()
    return render_template('index.html', books=books) # 重定向回主页

# 编辑图书条目 
@app.route('/book/edit/<int:book_id>', methods=['GET', 'POST'])
def edit(book_id):
    book = Book.query.get_or_404(book_id)

    if request.method == 'POST':  # 处理编辑表单的提交请求
        title = request.form['title']
        author = request.form['author']

        if not title or not author:
            flash('Invalid input.')
            return redirect(url_for('edit', book_id=book_id))  # 重定向回对应的编辑页面
    
        book.title = title  # 更新标题
        book.author = author  # 更新年份
        db.session.commit()  # 提交数据库会话
        flash('Item updated.')
        return redirect(url_for('index'))  # 重定向回主页

    return render_template('edit.html', book=book)  # 传入被编辑的电影记录

# 编辑删除条目 
@app.route('/book/delete/<int:book_id>', methods=['POST'])  # 限定只接受 POST 请求
def delete(book_id):
    book = Book.query.get_or_404(book_id)  # 获取电影记录
    db.session.delete(book)  # 删除对应的记录
    db.session.commit()  # 提交数据库会话
    flash('Item deleted.')
    return redirect(url_for('index'))  # 重定向回主页