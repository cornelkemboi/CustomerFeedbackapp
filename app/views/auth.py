from flask import Blueprint, request, session, redirect, url_for, flash, render_template, jsonify
import hashlib
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


@bp.route('/login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        hashed_password = hashlib.md5(password.encode()).hexdigest()

        # Query the user from the database
        user = RegisterUser.query.filter_by(email=email).first()

        if user and hashed_password == user.password:
            session['user_id'] = user.id
            session['role'] = user.role
            return redirect(url_for('auth.dashboard'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')
            return redirect(url_for('auth.user_login'))

    return render_template('admin/login.html')


@bp.route('/dashboard')
def dashboard():
    user_role = session.get('role', 'user')
    return render_template('admin/dashboard.html', user_role=user_role)


@bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    user_id = request.form['user_id']
    new_password = request.form['new_password']
    hashed_password = hashlib.md5(new_password.encode()).hexdigest()

    user = RegisterUser.query.get(user_id)
    if user:
        user.password = hashed_password
        user.write_date = db.func.now()
        db.session.commit()

    return render_template('admin/dashboard.html')


@bp.route('/delete-user', methods=['POST'])
@login_required
def delete_user():
    user_id = request.form['user_id']

    user = RegisterUser.query.get(user_id)
    if user:
        user.active = False
        db.session.commit()

    return render_template('admin/dashboard.html')


@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
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
    return jsonify(user_data)


@bp.route('/users', methods=['GET'])
@login_required
def api_users():
    # Query the database using SQLAlchemy
    users = RegisterUser.query.all()

    # Prepare data for serialization
    users_data = [{
        'id': user.id,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'role': user.role,
        'create_date': user.create_date
    } for user in users if user.active]

    # Serialize the data
    schema = UserSchema(many=True)
    result = schema.dump(users_data)

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
            return render_template('admin/dashboard.html')

        existing_user = RegisterUser.query.filter_by(email=email, active=True).first()

        if existing_user:
            flash('User with this email already exists. Please try another email.', 'danger')
            return render_template('admin/dashboard.html')

        hashed_password = hashlib.md5(password.encode()).hexdigest()

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
        return render_template('admin/dashboard.html')

    return render_template('admin/dashboard.html')


@bp.route('/logout')
def user_logout():
    session.pop('user_id', None)
    return redirect(url_for('auth.user_login'))
