import hashlib
from datetime import datetime

from flask import Blueprint, request, jsonify, flash, render_template
from sqlalchemy import func
from sqlalchemy.exc import NoResultFound

from app import db
from app.models import SurveyResponse, SurveyResponseDepartment, Department, RegisterUser, Quarter
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
    start_date = request.args.get('start_date', None)
    end_date = request.args.get('end_date', None)

    if not start_date and not end_date:
        current_date = datetime.now().date()
        try:
            date_query = db.session.query(Quarter).filter(
                Quarter.start_date <= current_date,
                Quarter.end_date >= current_date
            ).one()
            start_date = date_query.start_date
            end_date = date_query.end_date
        except NoResultFound:
            return {"error": "No quarter found for the current date"}, 404

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
        create_date = datetime.fromisoformat(response_data['create_date'].replace('Z', '+00:00'))

        # Format the date to include only day and hour
        formatted_date = create_date.strftime('%d/%m/%Y %H:%M:%S')
        response_data['create_date'] = formatted_date
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


@bp.route('/')
def index_page():
    return render_template('index.html')


@bp.route('/customer/feedback', methods=['GET', 'POST'])
def customer_feedback():
    try:
        print(request.form)

        if request.method == 'POST':
            name = request.form.get('name')
            age = request.form.get('age')
            gender = request.form.get('gender')
            pwd = request.form.get('pwd')
            organization = request.form.get('organization')
            departments = request.form.getlist('departments[]')
            service = request.form.get('service')
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
    except Exception as e:
        raise f"There was an error during customer_feedback put {str(e)}"
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
    try:
        # Define the subquery for quarters
        quarters_subquery = db.session.query(
            Quarter.name.label('quarter'),
            Quarter.start_date,
            Quarter.end_date
        ).subquery()

        # Join with the quarters table
        stats = db.session.query(
            func.year(SurveyResponse.create_date).label('year'),
            quarters_subquery.c.quarter,
            func.count(SurveyResponse.id).label('count')
        ).join(
            quarters_subquery,
            SurveyResponse.create_date.between(quarters_subquery.c.start_date, quarters_subquery.c.end_date)
        ).group_by('year', 'quarter').all()

        # Convert the result to a list of dictionaries
        user_stats = [
            {'year': stat.year, 'quarter': stat.quarter, 'count': stat.count}
            for stat in stats
        ]

        # Serialize the data using Marshmallow
        user_stats_schema = UserStatsSchema(many=True)
        user_stats_json = user_stats_schema.dump(user_stats)
    except Exception as e:
        raise f"There was an error during user_stats_route fetch {str(e)}"
    return jsonify(user_stats_json)
