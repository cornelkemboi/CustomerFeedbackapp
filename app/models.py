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


class SurveyResponse(db.Model):
    __tablename__ = 'survey_responses'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    age = db.Column(db.String(20))
    gender = db.Column(db.String(10))
    pwd = db.Column(db.String(6))
    organization = db.Column(db.String(255))
    service = db.Column(db.String(255))
    activity_or_product = db.Column(db.String(255))
    interacted_with = db.Column(db.String(255))
    person_attitude = db.Column(db.Integer)
    recommend = db.Column(db.Integer)
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
