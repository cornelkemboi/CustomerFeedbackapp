from flask import Blueprint, request, jsonify
from app import db
from app.models import SurveyResponse
from app.schemas import SurveyResponseSchema

bp = Blueprint('survey', __name__)


@bp.route('/surveys', methods=['GET'])
def get_surveys():
    # Example: Fetching all survey responses
    surveys = SurveyResponse.query.all()
    survey_schema = SurveyResponseSchema(many=True)
    result = survey_schema.dump(surveys)
    return jsonify(result)
