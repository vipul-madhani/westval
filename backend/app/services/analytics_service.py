from app import db
from app.models.analytics import Dashboard,Widget,Metric,Report
from datetime import datetime
class AnalyticsService:
    @staticmethod
    def create_dashboard(user_id,name,layout):
        dash=Dashboard(user_id=user_id,name=name,layout=layout)
        db.session.add(dash)
        db.session.commit()
        return dash
    @staticmethod
    def add_widget(dashboard_id,widget_type,position,config):
        widget=Widget(dashboard_id=dashboard_id,widget_type=widget_type,position=position,config=config)
        db.session.add(widget)
        db.session.commit()
        return widget
    @staticmethod
    def log_metric(project_id,metric_name,metric_value,metric_type):
        metric=Metric(project_id=project_id,metric_name=metric_name,metric_value=metric_value,metric_type=metric_type)
        db.session.add(metric)
        db.session.commit()
        return metric
    @staticmethod
    def get_project_metrics(project_id,limit=100):
        return Metric.query.filter_by(project_id=project_id).order_by(Metric.timestamp.desc()).limit(limit).all()
    @staticmethod
    def create_report(project_id,report_type,data,generated_by):
        report=Report(project_id=project_id,report_type=report_type,data=data,generated_by=generated_by)
        db.session.add(report)
        db.session.commit()
        return report
    @staticmethod
    def get_dashboard(dashboard_id):
        return Dashboard.query.get(dashboard_id)
    @staticmethod
    def update_dashboard_filters(dashboard_id,filters):
        dash=Dashboard.query.get(dashboard_id)
        if dash:
            dash.filters=filters
            db.session.commit()
        return dash
