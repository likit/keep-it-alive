from flask_login import login_required

from app.tracker import tracker_bp as tracker


@tracker.get('/')
@login_required
def index():
    return 'Welcome to your Activity Tracker!'