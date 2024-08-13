from flask import Blueprint, request, session, redirect, url_for, flash, render_template, jsonify, abort
from sqlalchemy import or_
import bcrypt

from app import db
from app.models import RegisterUser
from app.schemas import RegisterUserSchema, UserSchema
from functools import wraps

bp = Blueprint('auth', __name__)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('You need to log in to access this page.', 'danger')
            return redirect(url_for('auth.user_login'))
        return f(*args, **kwargs)

    return decorated_function


@bp.route('/admin', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = RegisterUser.query.filter_by(email=email).first()
        if user:
            try:
                # Check if the password matches
                if bcrypt.checkpw(password.encode(), user.password.encode()):
                    session['user_id'] = user.id
                    session['role'] = user.role
                    return redirect(url_for('auth.dashboard'))
                else:
                    flash('Invalid email or password. Please try again.', 'danger')
            except ValueError as e:
                flash(f"Password check error: {str(e)}", 'danger')
        else:
            flash('Invalid email or password. Please try again.', 'danger')

        return redirect(url_for('auth.user_login'))

    return render_template('admin/login.html')


@bp.route('/dashboard')
@login_required
def dashboard():
    user_role = session.get('role', 'user')
    return render_template('admin/dashboard.html', user_role=user_role)


@bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    try:
        user_id = request.form.get('user_id')
        email = request.form.get('email')
        new_password = request.form.get('new_password')

        if not (email or user_id) or not new_password:
            flash("Either email or user ID and new password must be provided", "danger")
            return redirect(url_for('auth.dashboard'))

        user = RegisterUser.query.filter(or_(RegisterUser.email == email, RegisterUser.id == user_id)).first()

        if user:
            user.password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
            db.session.commit()
            flash("Password updated successfully.", "success")
        else:
            flash("User not found", "danger")
    except Exception as e:
        flash(f"There was an error during password change: {str(e)}", "danger")

    return redirect(url_for('auth.dashboard'))


@bp.route('/user-change-password', methods=['POST'])
def user_change_password():
    try:
        email = request.form.get('email')
        new_password = request.form.get('new_password')

        if not email or not new_password:
            flash("Either email or user ID and new password must be provided", "danger")
            return redirect(url_for('auth. user_change_password'))

        user = RegisterUser.query.filter(RegisterUser.email == email).first()

        if user:
            user.password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
            db.session.commit()
            flash("Password updated successfully.", "success")
        else:
            flash("User not found", "danger")
    except Exception as e:
        flash(f"There was an error during password change: {str(e)}", "danger")

    return redirect(url_for('auth.user_login'))


@bp.route('/delete-user', methods=['POST'])
@login_required
def delete_user():
    try:
        user_id = request.form['user_id']

        user = RegisterUser.query.get(user_id)
        if user:
            user.active = False
            db.session.commit()
            flash("User deleted successfully.", "success")
        else:
            flash("User not found", "danger")
    except Exception as e:
        flash(f"There was an error during user deletion: {str(e)}", "danger")

    return redirect(url_for('auth.dashboard'))


@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    try:
        user_id = session.get('user_id')
        if not user_id:
            flash('You are not logged in.', 'danger')
            return redirect(url_for('auth.user_login'))

        user = RegisterUser.query.get(user_id)
        if user is None:
            flash('User not found.', 'danger')
            return jsonify({'error': 'User not found'}), 404

        user_schema = RegisterUserSchema()
        user_data = user_schema.dump(user)
    except Exception as e:
        flash(f"There was an error fetching profile data: {str(e)}", "danger")
        return jsonify({'error': 'Internal server error'}), 500

    return jsonify(user_data)


@bp.route('/users', methods=['GET'])
@login_required
def api_users():
    try:
        users = RegisterUser.query.all()
        users_data = [{
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'role': user.role,
        } for user in users if user.active]

        schema = UserSchema(many=True)
        result = schema.dump(users_data)
    except Exception as e:
        return jsonify({'error': f"There was an error fetching users: {str(e)}"}), 500

    return jsonify(result)


@bp.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        role = request.form['role']

        if password != confirm_password:
            flash('Passwords do not match. Please try again.', 'danger')
            return redirect(url_for('auth.dashboard'))

        existing_user = RegisterUser.query.filter_by(email=email, active=True).first()

        if existing_user:
            flash('User with this email already exists. Please try another email.', 'danger')
            return redirect(url_for('auth.dashboard'))

        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        new_user = RegisterUser(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=hashed_password,
            role=role
        )
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful!', 'success')
        return redirect(url_for('auth.dashboard'))

    return render_template('admin/dashboard.html')


@bp.route('/logout')
def user_logout():
    try:
        session.pop('user_id', None)
        flash('You have been logged out.', 'info')
    except Exception as e:
        flash(f"There was an error during logout: {str(e)}", "danger")
    return redirect(url_for('auth.user_login'))
