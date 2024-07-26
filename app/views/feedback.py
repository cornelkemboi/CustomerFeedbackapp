import hashlib
from datetime import datetime

from flask import Blueprint, request, jsonify, flash, render_template
from sqlalchemy import func

from app import db
from app.models import SurveyResponse, SurveyResponseDepartment, Department, RegisterUser
from app.schemas import DepartmentSchema, SurveyResponseSchema, DepartmentPieChartSchema, RegisterUserSchema, \
    UserStatsSchema
from app.views.auth import login_required

bp = Blueprint('feedback', __name__)


@bp.route('/departments', methods=['GET'])
def get_departments():
    departments = Department.query.order_by(Department.name).all()
    department_schema = DepartmentSchema(many=True)
    departments_data = department_schema.dump(departments)
    return jsonify(departments_data)


@bp.route('/feedback', methods=['GET'])
@login_required
def feedback():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Query SurveyResponses
    query = db.session.query(SurveyResponse)

    if start_date and end_date:
        query = query.filter(SurveyResponse.create_date.between(start_date, end_date))

    survey_responses = query.all()

    feedback_data = []

    for response in survey_responses:
        # Query associated departments
        departments = (
            db.session.query(Department)
            .join(SurveyResponseDepartment)
            .filter(SurveyResponseDepartment.survey_response_id == response.id)
            .all()
        )

        # Serialize departments
        department_schema = DepartmentSchema(many=True)
        departments_data = department_schema.dump(departments)
        department_names = [dept['name'] for dept in departments_data]

        # Serialize survey response
        response_data = SurveyResponseSchema().dump(response)
        response_data['departments'] = ", ".join(department_names)

        feedback_data.append(response_data)

    return jsonify(feedback_data)


@bp.route('/department-pie-chart')
@login_required
def department_pie_chart():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Define your query
    query = db.session.query(
        Department.name.label('department'),
        db.func.count(SurveyResponseDepartment.department_id).label('count')
    ).join(SurveyResponseDepartment, Department.id == SurveyResponseDepartment.department_id
           ).join(SurveyResponse, SurveyResponse.id == SurveyResponseDepartment.survey_response_id
                  ).filter(SurveyResponse.create_date.between(start_date, end_date)
                           ).group_by(Department.name)

    # Execute the query and fetch results
    results = query.all()

    # Use Marshmallow schema to serialize the data
    schema = DepartmentPieChartSchema(many=True)
    department_data = schema.dump(results)

    return jsonify(department_data)


@bp.route('/', methods=['GET', 'POST'])
def main_page():
    if request.method == 'POST':
        name = request.form.get('name')
        age = request.form.get('age')
        gender = request.form.get('gender')
        pwd = request.form.get('pwd')
        organization = request.form.get('organization')
        departments = request.form.getlist('departments[]')
        service = request.form.get('service')
        activity_or_product = request.form.get('activity_or_product')
        interacted_with = request.form.get('interacted_with')
        person_attitude = request.form.get('person_attitude')
        recommend = request.form.get('recommend')
        comments = request.form.get('comments')
        phone = request.form.get('phone')
        email = request.form.get('email')
        create_date = datetime.utcnow()

        # Insert data into the survey_responses table
        new_response = SurveyResponse(
            name=name,
            age=age,
            gender=gender,
            pwd=pwd,
            organization=organization,
            service=service,
            activity_or_product=activity_or_product,
            interacted_with=interacted_with,
            person_attitude=person_attitude,
            recommend=recommend,
            comments=comments,
            phone=phone,
            email=email,
            create_date=create_date
        )
        db.session.add(new_response)
        db.session.commit()

        # Insert into the survey_response_departments table
        for department_id in departments:
            new_response_department = SurveyResponseDepartment(
                survey_response_id=new_response.id,
                department_id=department_id
            )
            db.session.add(new_response_department)

        db.session.commit()
        flash('Form submitted successfully!', 'success')

        kippra_website = 'https://kippra.or.ke/'
        feedback = (f"Thank you for your feedback! We appreciate your visit to our"
                    f" organization and look forward to welcoming you again. For more information, please visit our"
                    f" website <a href='{kippra_website}' target='_blank'>here</a>.")
        return render_template('success.html', feedback=feedback)

    return render_template('index.html')


@bp.route('/content/<page>')
@login_required
def load_content(page):
    if page == 'profile':
        return render_template('admin/profile.html')
    elif page == 'users':
        return render_template('admin/users.html')
    elif page == 'user_register':
        return render_template('admin/register.html')
    elif page == 'dashboard':
        return render_template('admin/dashboard.html')
    else:
        return "Content not found", 404


@bp.route('/user-stats', methods=['GET'])
@login_required
def user_stats_route():
    # Query the database using SQLAlchemy
    stats = db.session.query(
        func.date_format(SurveyResponse.create_date, '%Y-%m').label('month'),
        func.count(SurveyResponse.id).label('count')
    ).group_by('month').all()

    # Convert the result to a list of dictionaries
    user_stats = [{'month': stat.month, 'count': stat.count} for stat in stats]

    # Serialize the data using Marshmallow
    user_stats_schema = UserStatsSchema(many=True)
    user_stats_json = user_stats_schema.dump(user_stats)

    return jsonify(user_stats_json)