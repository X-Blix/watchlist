from flask import render_template

from watchlist import app

@app.errorhandler(400)
def page_not_found(e):
    return render_template('errors/400.html'), 400


@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def page_not_found(e):
    return render_template('errors/404.html'), 500





