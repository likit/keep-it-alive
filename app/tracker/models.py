from datetime import datetime

from dateutil.tz import tz

from app import db
from app.auth.models import User

bkktz = tz.gettz('Asia/Bangkok')


class TrackerActivity(db.Model):
    __tablename__ = 'tracker_activities'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(), nullable=False)
    description = db.Column(db.Text(), nullable=False)
    priority = db.Column(db.Integer, nullable=False, default=0,
                         info={'choices': [(i, c) for i, c in [(1, 'Low'), (2, 'Medium'), (3, 'High')]]})
    start_at = db.Column(db.DateTime(timezone=True), nullable=False)
    end_at = db.Column(db.DateTime(timezone=True), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True))
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator = db.relationship(User, backref=db.backref('activities', lazy='dynamic'))

    @property
    def remaining_days(self):
        delta = self.end_at.astimezone(bkktz) - datetime.now(tz=bkktz)
        return delta.days

    @property
    def total_days(self):
        delta = self.end_at.astimezone(bkktz) - self.start_at.astimezone(bkktz)
        return delta.days

    @property
    def percent_finished_tasks(self):
        if self.tasks.count():
            return len(self.tasks.filter_by(finished_at=None).all()) / self.tasks.count()
        else:
            return self.tasks.count()


class TrackerTask(db.Model):
    __tablename__ = 'tracker_tasks'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    task = db.Column(db.String(), nullable=False)
    note = db.Column(db.Text())
    created_at = db.Column(db.DateTime(timezone=True))
    finished_at = db.Column(db.DateTime(timezone=True))
    activity_id = db.Column(db.Integer, db.ForeignKey('tracker_activities.id'))
    activity = db.relationship(TrackerActivity,
                               backref=db.backref('tasks',
                                                  cascade="all, delete-orphan",
                                                  lazy='dynamic',
                                                  order_by='TrackerTask.created_at'),
                               )
    progress = db.Column(db.Integer, default=0,
                         info={'choices': [(p, f'{p}%') for p in range(0, 110, 10)]})
