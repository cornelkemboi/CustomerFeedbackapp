from datetime import datetime
import pytz
from . import db

# Define the East African Time timezone
EAT = pytz.timezone('Africa/Nairobi')


def get_eat_now():
    """Return the current time in East African Time."""
    return datetime.now(EAT).strftime("%Y-%m-%d %I:%M:%S")


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
    create_date = db.Column(db.DateTime, default=get_eat_now)
    write_date = db.Column(db.DateTime, default=get_eat_now, onupdate=get_eat_now)
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
    create_date = db.Column(db.DateTime, default=get_eat_now)


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
    date_visited = db.Column(db.DateTime, default=get_eat_now)  # Changed to DateTime
    status = db.Column(db.String(80), default='Send Message')
    msg_id = db.Column(db.String(80))
