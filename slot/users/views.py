#   imports    #
from flask import flash, redirect, render_template, request, url_for, Blueprint
from flask_login import login_user, login_required, logout_user

import controller as user_controller
from slot.users.models import User
from .forms import LoginForm

#    config    #
users_blueprint = Blueprint(
        'users', __name__,
        template_folder='templates')


#    routes    #
@users_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    form = LoginForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():

            user = user_controller.return_user_if_valid_credentials(
                request.form['username'],
                request.form['password'])

            if user:
                login_user(user)
                flash('You were logged in.')
                return redirect(url_for('dashboard'))

            else:
                flash('Invalid credentials. Try again.')

    return render_template('login.html', form=form, error=error)


@users_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You were logged out.')
    return redirect(url_for('users.login'))
