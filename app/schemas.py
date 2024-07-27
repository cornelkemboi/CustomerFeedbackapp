from marshmallow import Schema, fields

from . import ma
from .models import Department, RegisterUser, SurveyResponse, SurveyResponseDepartment


class DepartmentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Department


class RegisterUserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = RegisterUser


class SurveyResponseSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = SurveyResponse


class SurveyResponseDepartmentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = SurveyResponseDepartment


class DepartmentPieChartSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = SurveyResponseDepartment


# Custom schema for department pie chart data
class DepartmentPieChartSchema(Schema):
    department = fields.String()
    count = fields.Integer()


# Schema for User, defined separately
class UserSchema(Schema):
    id = fields.Integer()
    first_name = fields.String()
    last_name = fields.String()
    email = fields.String()
    role = fields.String()
    create_date = fields.DateTime(format='%Y-%m-%dT%H:%M:%S')


class UserStatsSchema(Schema):
    year = fields.Str(required=True)
    count = fields.Int(required=True)
    quarter = fields.Str(required=True)


class QuarterSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    start_date = fields.Date()
    end_date = fields.Date()
