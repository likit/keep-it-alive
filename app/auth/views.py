from flask import render_template, request, flash, redirect, url_for
from flask_login import login_user, current_user, logout_user

from app.auth import auth_bp as auth
from app.auth.forms import LoginForm
from app.auth.models import User


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if user.verify_password(form.password.data):
                login_user(user)
                flash('Logged in successfully', 'success')
                next = request.args.get('next')
                return redirect(next or url_for('tracker.index'))
            else:
                flash('Invalid email or password', 'danger')
        else:
            flash('Invalid email or the email does not exist.', 'danger')
    else:
        for e in form.errors:
            flash(f'{e}: {form.errors[e]}', 'danger')
    return render_template('auth/login.html', form=form)


@auth.get('/logout')
def logout():
    if current_user.is_authenticated:
        logout_user()
        flash('You have been logged out.', 'success')
        return redirect(url_for('auth.login'))
    return redirect(url_for('tracker.index'))