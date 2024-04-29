from datetime import datetime, timedelta

from dateutil.tz import tz
from flask import render_template, flash, redirect, url_for, make_response, request
from flask_login import login_required, current_user
from sqlalchemy import func

from app import db
from app.tracker import tracker_bp as tracker
from app.tracker.forms import ActivityForm, TaskForm
from app.tracker.models import TrackerActivity, TrackerTask


@tracker.get('/')
@login_required
def index():
    filter = request.args.get('filter', 'unfinished')
    activities = TrackerActivity.query.filter_by(creator=current_user) \
        .filter(func.timezone('Asia/Bangkok', TrackerActivity.end_at) > datetime.now(tz=tz.gettz('Asia/Bangkok')))
    if filter == 'unfinished':
        activities = activities.filter_by(finished_at=None)
    return render_template('tracker/index.html',
                           activities=activities.order_by(TrackerActivity.end_at))


@tracker.route('/activities', methods=['GET', 'POST'])
@tracker.route('/activities/<int:activity_id>/edit', methods=['GET', 'POST', 'PATCH', 'DELETE'])
@login_required
def edit_activity(activity_id=None):
    if activity_id is None:
        form = ActivityForm()
    else:
        activity = TrackerActivity.query.get(activity_id)
        form = ActivityForm(obj=activity)
    if request.method == 'DELETE':
        db.session.delete(activity)
        db.session.commit()
        flash('Activity deleted!', 'success')
        resp = make_response()
        resp.headers['HX-Redirect'] = url_for('tracker.index')
        return resp
    if request.method == 'PATCH':
        activity.finished_at = datetime.now(tz=tz.gettz('Asia/Bangkok'))
        db.session.add(activity)
        db.session.commit()
        return make_response()
    if form.validate_on_submit():
        if not activity_id:
            activity = TrackerActivity()
            flash('New activity was added.', 'success')
        else:
            flash('The activity has been updated.', 'success')
        form.populate_obj(activity)
        activity.start_at.replace(tzinfo=tz.gettz('Asia/Bangkok'))
        activity.end_at.replace(tzinfo=tz.gettz('Asia/Bangkok'))
        activity.created_at = datetime.now(tz=tz.gettz('Asia/Bangkok'))
        activity.creator = current_user
        if not activity_id:
            activity.alive_until = activity.start_at + timedelta(days=3)
        db.session.add(activity)
        db.session.commit()
        next = request.args.get('next')
        return redirect(next or url_for('tracker.edit_activity'))
    else:
        for e in form.errors:
            flash(f'{e}: {form.errors[e]}', 'danger')
    return render_template('tracker/edit_activity.html', form=form)


@tracker.route('/activities/<int:activity_id>/tasks')
@login_required
def show_tasks(activity_id):
    activity = TrackerActivity.query.get(activity_id)
    form = TaskForm()
    if form.validate_on_submit():
        task = TrackerTask()
        form.populate_obj(task)
        task.created_at = datetime.now(tz=tz.gettz('Asia/Bangkok'))
        task.activity = activity
        db.session.add(task)
        db.session.commit()
        flash('Task added successfully!', 'success')
        return redirect(url_for('tracker.edit_task', task_id=task.id, activity_id=activity_id))
    return render_template('tracker/tasks.html', form=form, activity=activity)


@tracker.route('/activities/<int:activity_id>/tasks/new', methods=['GET', 'POST'])
@tracker.route('/activities/<int:activity_id>/tasks/<int:task_id>', methods=['GET', 'POST', 'DELETE'])
@login_required
def edit_task(activity_id, task_id=None):
    activity = TrackerActivity.query.get(activity_id)
    if task_id:
        task = TrackerTask.query.get(task_id)
        form = TaskForm(obj=task)
    else:
        form = TaskForm()
    if request.method == 'DELETE':
        task = TrackerTask.query.get(task_id)
        db.session.delete(task)
        db.session.commit()
        resp = make_response()
        resp.headers['HX-Refresh'] = 'true'
        return resp
    if form.validate_on_submit():
        if not task_id:
            task = TrackerTask()
        form.populate_obj(task)

        if not task_id:
            task.created_at = datetime.now(tz=tz.gettz('Asia/Bangkok'))
            task.activity = activity
        else:
            # We encourage users to work on a project on a daily basis.
            # Therefore, updating a bunch of tasks in one day is not rewarded much.
            if task.activity.last_active.astimezone(tz.gettz('Asia/Bangkok')).date() != \
                    datetime.now(tz=tz.gettz('Asia/Bangkok')).date():
                task.activity.alive_until = task.activity.alive_until + timedelta(days=3)
        if task.progress == 100:
            task.finished_at = datetime.now(tz=tz.gettz('Asia/Bangkok'))
        task.updated_at = datetime.now(tz=tz.gettz('Asia/Bangkok'))
        db.session.add(task)
        db.session.commit()
        flash('Task added successfully!', 'success')
        resp = make_response()
        resp.headers['HX-Redirect'] = url_for('tracker.show_tasks', task_id=task_id, activity_id=activity_id)
        return resp
    return render_template('tracker/modals/task_form.html',
                           form=form, task_id=task_id, activity=activity)
