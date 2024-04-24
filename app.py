from flask import Flask
from flask import Flask, render_template
app = Flask(__name__)

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

@app.route('/')
def index():
    return render_template('index.html', name=name, books=books)