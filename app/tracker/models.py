from datetime import datetime

from dateutil.tz import tz

from app import db
from app.auth.models import User

bkktz = tz.gettz('Asia/Bangkok')


class TrackerActivity(db.Model):
    __tablename__ = 'tracker_activities'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(), nullable=False, info={'label': 'Title'})
    description = db.Column(db.Text(), nullable=False, info={'label': 'Detail'})
    priority = db.Column(db.Integer, nullable=False, default=0,
                         info={'choices': [(i, c) for i, c in [(1, 'Low'), (2, 'Medium'), (3, 'High')]],
                               'label': 'Priority'})
    start_at = db.Column(db.DateTime(timezone=True), nullable=False, info={'label': 'Start'})
    end_at = db.Column(db.DateTime(timezone=True), nullable=False, info={'label': 'End'})
    created_at = db.Column(db.DateTime(timezone=True))
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator = db.relationship(User, backref=db.backref('activities', lazy='dynamic'))
    finished_at = db.Column(db.DateTime(timezone=True))
    alive_until = db.Column(db.DateTime(timezone=True))

    @property
    def remaining_days(self):
        delta = self.end_at.astimezone(bkktz) - datetime.now(tz=bkktz)
        return delta.days

    @property
    def total_days(self):
        delta = self.end_at.astimezone(bkktz) - self.start_at.astimezone(bkktz)
        return delta.days

    @property
    def unfinished_tasks(self):
        if self.tasks.count():
            return self.tasks.filter_by(finished_at=None).count()
        else:
            return self.tasks.count()

    @property
    def last_active(self):
        unfinished_tasks = self.tasks.filter_by(finished_at=None)
        last_update = None
        if unfinished_tasks.count():
            for task in unfinished_tasks:
                if task.updated_at:
                    if not last_update:
                        last_update = task.updated_at
                    else:
                        if task.updated_at > last_update:
                            last_update = task.updated_at
        return last_update

    @property
    def life_in_days(self):
        alive_until = self.alive_until.astimezone(bkktz)
        end_delta = self.end_at.astimezone(bkktz) - datetime.now(tz=bkktz)
        delta = alive_until - datetime.now(tz=bkktz)
        if delta.days > end_delta.days:
            return end_delta.days if end_delta.days > 0 else 0
        else:
            return delta.days if delta.days > 0 else 0


class TrackerTask(db.Model):
    __tablename__ = 'tracker_tasks'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    task = db.Column(db.String(), nullable=False, info={'label': 'Task'})
    note = db.Column(db.Text(), info={'label': 'Note'})
    created_at = db.Column(db.DateTime(timezone=True))
    finished_at = db.Column(db.DateTime(timezone=True))
    updated_at = db.Column(db.DateTime(timezone=True))
    activity_id = db.Column(db.Integer, db.ForeignKey('tracker_activities.id'))
    activity = db.relationship(TrackerActivity,
                               backref=db.backref('tasks',
                                                  cascade="all, delete-orphan",
                                                  lazy='dynamic',
                                                  order_by='TrackerTask.created_at'),
                               )
    progress = db.Column(db.Integer, default=0,
                         info={'choices': [(p, f'{p}%') for p in range(0, 110, 10)],
                               'label': 'Progress'})
