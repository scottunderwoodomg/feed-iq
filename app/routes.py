from flask import render_template
from app import app
from datetime import datetime

@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Scott'}
    feeds = [
        {
            'child': 'Charlie',
            'feed_datetime': datetime(2022,5,29,11,46,42),
            'feed_type': 'Breast'
        },
        {
            'child': 'Charlie',
            'feed_datetime': datetime(2022,5,29,8,35,41),
            'feed_type': 'Breast'
        }
    ]
    return render_template('index.html', title='Home', user=user, feeds=feeds)

