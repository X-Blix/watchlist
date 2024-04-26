import os
import sys

import click
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

from flask import request, url_for, redirect, flash

from werkzeug.security import generate_password_hash, check_password_hash

from flask_login import UserMixin, login_user, current_user
from flask_login import LoginManager

from flask_login import login_required, logout_user

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

login_manager = LoginManager(app)  # 实例化扩展类


@login_manager.user_loader
def load_user(user_id):  # 创建用户加载回调函数，接受用户 ID 作为参数
    user = User.query.get(int(user_id))  # 用 ID 作为 User 模型的主键查询对应的用户
    return user  # 返回用户对象

login_manager.login_view = 'login'



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



@app.cli.command()
@click.option('--username', prompt=True, help='The username used to login.')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='The password used to login.')
def admin(username, password):
    """Create user."""
    db.create_all()

    user = User.query.first()
    if user is not None:
        click.echo('Updating user...')
        user.username = username
        user.set_password(password)  # 设置密码
    else:
        click.echo('Creating user...')
        user = User(username=username, name='Admin')
        user.set_password(password)  # 设置密码
        db.session.add(user)

    db.session.commit()  # 提交数据库会话
    click.echo('Done.')


class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True,autoincrement = True)
    name = db.Column(db.String(20))
    username = db.Column(db.String(20))  # 用户名
    password_hash = db.Column(db.String(128))  # 密码散列值

    def set_password(self, password):  # 用来设置密码的方法，接受密码作为参数
        self.password_hash = generate_password_hash(password)  # 将生成的密码保持到对应字段

    def validate_password(self, password):  # 用于验证密码的方法，接受密码作为参数
        return check_password_hash(self.password_hash, password)  # 返回布尔值


class Book(db.Model):  # 表名将会是 book
    id = db.Column(db.Integer, primary_key=True)  # 主键
    title = db.Column(db.String(60))  # 标题
    author = db.Column(db.String(10))  # 作者



@app.cli.command()  # 注册为命令，可以传入 name 参数来自定义命令
@click.option('--drop', is_flag=True, help='Create after drop.')  # 设置选项
def initdb(drop):
    """Initialize the database."""
    if drop:  # 判断是否输入了选项
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')  # 输出提示信息




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

        if not current_user.is_authenticated:
            return redirect(url_for('index'))

        title = request.form['title']
        author = request.form['author']

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
@login_required
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
@login_required  # 登录保护
def delete(book_id):
    book = Book.query.get_or_404(book_id)  # 获取电影记录
    db.session.delete(book)  # 删除对应的记录
    db.session.commit()  # 提交数据库会话
    flash('Item deleted.')
    return redirect(url_for('index'))  # 重定向回主页

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('Invalid input.')
            return redirect(url_for('login'))

        user = User.query.first()

        if username == user.username and user.validate_password(password):
            login_user(user)
            flash('Login success.')
            return redirect(url_for('index'))

        flash('Invalid username or password.')
        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
@login_required  # 用于视图保护，后面会详细介绍
def logout():
    logout_user()  # 登出用户
    flash('Goodbye.')
    return redirect(url_for('index'))  # 重定向回首页


# 支持设置用户名字
@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        name = request.form['name']

        if not name or len(name) > 20:
            flash('Invalid input.')
            return redirect(url_for('settings'))

        current_user.name = name
        # current_user 会返回当前登录用户的数据库记录对象
        # 等同于下面的用法
        # user = User.query.first()
        # user.name = name
        db.session.commit()
        flash('Settings updated.')
        return redirect(url_for('index'))

    return render_template('settings.html')