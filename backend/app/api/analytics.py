from flask import Blueprint,request,jsonify
from app.services.analytics_service import AnalyticsService
from functools import wraps
analytics_bp=Blueprint('analytics',__name__,url_prefix='/api/analytics')
def token_required(f):
    @wraps(f)
    def decorated(*args,**kwargs):
        if not request.headers.get('Authorization'):return jsonify({'error':'Unauthorized'}),401
        return f(*args,**kwargs)
    return decorated
@analytics_bp.route('/dashboard',methods=['POST'])
@token_required
def create_dashboard():
    data=request.json
    dash=AnalyticsService.create_dashboard(data['user_id'],data['name'],data.get('layout'))
    return jsonify({'dashboard_id':dash.id}),201
@analytics_bp.route('/dashboard/<int:dash_id>/widget',methods=['POST'])
@token_required
def add_widget(dash_id):
    data=request.json
    widget=AnalyticsService.add_widget(dash_id,data['type'],data.get('pos'),data.get('config'))
    return jsonify({'widget_id':widget.id}),201
@analytics_bp.route('/metric',methods=['POST'])
@token_required
def log_metric():
    data=request.json
    metric=AnalyticsService.log_metric(data['project_id'],data['name'],data['value'],data.get('type'))
    return jsonify({'metric_id':metric.id}),201
@analytics_bp.route('/project/<int:proj_id>/metrics',methods=['GET'])
@token_required
def get_metrics(proj_id):
    metrics=AnalyticsService.get_project_metrics(proj_id)
    return jsonify([{'name':m.metric_name,'value':m.metric_value,'ts':m.timestamp.isoformat()} for m in metrics]),200
@analytics_bp.route('/report',methods=['POST'])
@token_required
def create_report():
    data=request.json
    user_id=request.headers.get('user_id',1)
    report=AnalyticsService.create_report(data['project_id'],data['type'],data['data'],user_id)
    return jsonify({'report_id':report.id}),201
