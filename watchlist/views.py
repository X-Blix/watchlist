from flask import  render_template,request,url_for,redirect, flash,Flask

from flask_login import login_user,login_required,logout_user,UserMixin,  current_user

from watchlist import app,db
from watchlist.models import User,Book


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
