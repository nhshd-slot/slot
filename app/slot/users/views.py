################
#    imports   #
################
from flask import Blueprint, render_template
from app.slot.models import User
from flask import flash, redirect, render_template, request, \
    url_for, Blueprint

from flask.ext.login import login_user, \
    login_required, logout_user

from .forms import LoginForm

################
#    config    #
################
users_blueprint = Blueprint(
        'users', __name__,
        template_folder='templates')


################
#    routes    #
################
@users_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    form = LoginForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            if request.form['username'] == 'slot' and request.form['password'] == 'test':
                user = User('slot', 'test')
                login_user(user)
                flash('You were logged in. Go Crazy.')
                return redirect(url_for('index'))
            else:
                print('Invalid credentials')
                flash('Invalid credentials. Try again.')
    return render_template('login.html', form=form, error=error)


@users_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You were logged out.')
    return redirect(url_for('users.login'))
