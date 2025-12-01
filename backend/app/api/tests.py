"""Test management API"""
from flask import Blueprint

tests_bp = Blueprint('tests', __name__)

@tests_bp.route('/', methods=['GET', 'POST'])
def tests():
    return {'message': 'Tests endpoint'}, 200