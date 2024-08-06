from datetime import datetime

from . import db


class Department(db.Model):
    __tablename__ = 'departments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)


class RegisterUser(db.Model):
    __tablename__ = 'register_user'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='User', nullable=False)
    create_date = db.Column(db.DateTime, default=db.func.now())
    write_date = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    active = db.Column(db.Boolean, default=True)


class SurveyResponse(db.Model):
    __tablename__ = 'survey_responses'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    age = db.Column(db.String(20), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    pwd = db.Column(db.String(6), nullable=False)
    organization = db.Column(db.String(255), nullable=False)
    service = db.Column(db.String(255), nullable=False)
    interacted_with = db.Column(db.String(255))
    person_attitude = db.Column(db.Integer)
    recommend = db.Column(db.Integer, nullable=False)
    comments = db.Column(db.Text)
    phone = db.Column(db.String(255))
    email = db.Column(db.String(50))
    create_date = db.Column(db.DateTime, default=db.func.now())


class SurveyResponseDepartment(db.Model):
    __tablename__ = 'survey_response_departments'
    survey_response_id = db.Column(db.Integer, db.ForeignKey('survey_responses.id'), primary_key=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), primary_key=True)


class Quarter(db.Model):
    __tablename__ = 'quarters'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(2), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)

    def __repr__(self):
        return f'<Quarter {self.name}>'


class ReceiptionRecords(db.Model):
    __tablename__ = 'reception_records'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    date_visited = db.Column(db.String(20), default=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    status = db.Column(db.String(80))
