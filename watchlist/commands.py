import click

from watchlist import app, db
from watchlist.models import User, Book

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
