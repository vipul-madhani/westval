from app import db
from app.models.admin_config import AdminConfig,WorkflowConfig,RolePermission,SystemLog
from datetime import datetime
class AdminConfigService:
    @staticmethod
    def set_config(key,value,description=''):
        cfg=AdminConfig.query.filter_by(config_key=key).first()
        if cfg:
            cfg.config_value=value
            cfg.description=description
        else:
            cfg=AdminConfig(config_key=key,config_value=value,description=description)
        db.session.add(cfg)
        db.session.commit()
        return cfg
    @staticmethod
    def get_config(key):
        cfg=AdminConfig.query.filter_by(config_key=key).first()
        return cfg.config_value if cfg else None
    @staticmethod
    def create_workflow(name,stages,approvers,sla_days=5,parallel=False):
        wf=WorkflowConfig(workflow_name=name,stages=stages,approvers=approvers,sla_days=sla_days,parallel_approval=parallel)
        db.session.add(wf)
        db.session.commit()
        return wf
    @staticmethod
    def get_workflow(name):
        return WorkflowConfig.query.filter_by(workflow_name=name).first()
    @staticmethod
    def log_action(user_id,action,resource,details):
        log=SystemLog(user_id=user_id,action=action,resource=resource,details=details)
        db.session.add(log)
        db.session.commit()
        return log
    @staticmethod
    def get_audit_logs(resource_type=None,limit=100):
        q=SystemLog.query
        if resource_type:
            q=q.filter_by(resource=resource_type)
        return q.order_by(SystemLog.timestamp.desc()).limit(limit).all()
