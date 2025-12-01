"""Workflow engine for approval routing"""
from datetime import datetime, timedelta
from app import db
from app.models.workflow import WorkflowDefinition, WorkflowInstance, WorkflowTask, Notification
from app.models.user import User
from app.models.audit import AuditLog
import uuid

class WorkflowService:
    
    @staticmethod
    def create_default_workflows():
        """Create standard validation workflows"""
        workflows = [
            {
                'name': 'Document Approval Workflow',
                'entity_type': 'Document',
                'stages': [
                    {'name': 'Author Review', 'roles': ['Validator'], 'order': 1, 'sla_hours': 24},
                    {'name': 'Peer Review', 'roles': ['Validator'], 'order': 2, 'sla_hours': 48},
                    {'name': 'QA Review', 'roles': ['QA'], 'order': 3, 'sla_hours': 72},
                    {'name': 'Final Approval', 'roles': ['Approver'], 'order': 4, 'sla_hours': 48}
                ]
            },
            {
                'name': 'Protocol Approval Workflow',
                'entity_type': 'Protocol',
                'stages': [
                    {'name': 'Draft Review', 'roles': ['Validator'], 'order': 1, 'sla_hours': 48},
                    {'name': 'SME Review', 'roles': ['Validator'], 'order': 2, 'sla_hours': 72},
                    {'name': 'QA Approval', 'roles': ['QA'], 'order': 3, 'sla_hours': 72},
                    {'name': 'Quality Approval', 'roles': ['Approver'], 'order': 4, 'sla_hours': 48}
                ]
            },
            {
                'name': 'Test Execution Workflow',
                'entity_type': 'TestCase',
                'stages': [
                    {'name': 'Test Execution', 'roles': ['Validator'], 'order': 1, 'sla_hours': 120},
                    {'name': 'Result Review', 'roles': ['QA'], 'order': 2, 'sla_hours': 48}
                ]
            }
        ]
        
        for wf_data in workflows:
            existing = WorkflowDefinition.query.filter_by(name=wf_data['name']).first()
            if not existing:
                wf = WorkflowDefinition(
                    id=str(uuid.uuid4()),
                    name=wf_data['name'],
                    entity_type=wf_data['entity_type'],
                    stages=wf_data['stages'],
                    is_active=True
                )
                db.session.add(wf)
        
        db.session.commit()
    
    @staticmethod
    def start_workflow(entity_type, entity_id, user):
        """Start a workflow for an entity"""
        # Get workflow definition
        workflow_def = WorkflowDefinition.query.filter_by(
            entity_type=entity_type,
            is_active=True
        ).first()
        
        if not workflow_def:
            return None
        
        # Create workflow instance
        instance = WorkflowInstance(
            id=str(uuid.uuid4()),
            workflow_definition_id=workflow_def.id,
            entity_type=entity_type,
            entity_id=entity_id,
            current_stage=0,
            status='IN_PROGRESS',
            started_by=user.id
        )
        
        db.session.add(instance)
        db.session.flush()
        
        # Create first stage task
        first_stage = workflow_def.stages[0]
        WorkflowService._create_task(instance, first_stage, workflow_def.stages)
        
        db.session.commit()
        return instance
    
    @staticmethod
    def _create_task(workflow_instance, stage, all_stages):
        """Create a task for a workflow stage"""
        # Find users with required role
        users = User.query.join(User.roles).filter(
            db.func.lower(db.text('roles.name')).in_([r.lower() for r in stage['roles']])
        ).all()
        
        if not users:
            # Fallback to admin if no users found
            users = User.query.filter_by(is_admin=True).all()
        
        # Assign to user with least workload
        assigned_user = WorkflowService._get_least_busy_user(users)
        
        # Calculate due date
        due_date = datetime.utcnow() + timedelta(hours=stage.get('sla_hours', 48))
        
        task = WorkflowTask(
            id=str(uuid.uuid4()),
            workflow_instance_id=workflow_instance.id,
            stage_name=stage['name'],
            stage_order=stage['order'],
            task_type='REVIEW',
            assigned_to=assigned_user.id,
            assigned_role=stage['roles'][0],
            status='PENDING',
            due_date=due_date
        )
        
        db.session.add(task)
        
        # Create notification
        notification = Notification(
            id=str(uuid.uuid4()),
            user_id=assigned_user.id,
            type='TASK_ASSIGNED',
            title=f'New Task: {stage["name"]}',
            message=f'You have been assigned a {stage["name"]} task for {workflow_instance.entity_type}',
            entity_type=workflow_instance.entity_type,
            entity_id=workflow_instance.entity_id,
            priority='NORMAL'
        )
        
        db.session.add(notification)
    
    @staticmethod
    def _get_least_busy_user(users):
        """Get user with least pending tasks"""
        if not users:
            return None
        
        user_workloads = []
        for user in users:
            pending_tasks = WorkflowTask.query.filter_by(
                assigned_to=user.id,
                status='PENDING'
            ).count()
            user_workloads.append((user, pending_tasks))
        
        # Sort by workload
        user_workloads.sort(key=lambda x: x[1])
        return user_workloads[0][0]
    
    @staticmethod
    def complete_task(task_id, user, action, comments=None):
        """Complete a workflow task"""
        task = WorkflowTask.query.get(task_id)
        if not task:
            return None
        
        # Update task
        task.status = 'COMPLETED'
        task.action_taken = action
        task.comments = comments
        task.completed_at = datetime.utcnow()
        
        # Get workflow instance
        workflow = WorkflowInstance.query.get(task.workflow_instance_id)
        workflow_def = WorkflowDefinition.query.get(workflow.workflow_definition_id)
        
        if action == 'APPROVED':
            # Move to next stage
            next_stage_order = task.stage_order + 1
            next_stage = next((s for s in workflow_def.stages if s['order'] == next_stage_order), None)
            
            if next_stage:
                # Create next task
                WorkflowService._create_task(workflow, next_stage, workflow_def.stages)
                workflow.current_stage = next_stage_order
            else:
                # Workflow complete
                workflow.status = 'COMPLETED'
                workflow.completed_at = datetime.utcnow()
                
                # Update entity status
                WorkflowService._update_entity_status(workflow.entity_type, workflow.entity_id, 'Approved')
        
        elif action == 'REJECTED':
            # Reject entire workflow
            workflow.status = 'REJECTED'
            workflow.completed_at = datetime.utcnow()
            
            # Update entity status
            WorkflowService._update_entity_status(workflow.entity_type, workflow.entity_id, 'Rejected')
        
        # Create audit log
        audit = AuditLog(
            user_id=user.id,
            user_name=f"{user.first_name} {user.last_name}",
            action='WORKFLOW_ACTION',
            entity_type='WorkflowTask',
            entity_id=task.id,
            entity_name=task.stage_name,
            change_description=f'{action} - {task.stage_name}',
            reason=comments,
            timestamp=datetime.utcnow()
        )
        db.session.add(audit)
        
        db.session.commit()
        return task
    
    @staticmethod
    def _update_entity_status(entity_type, entity_id, status):
        """Update the status of the entity being processed"""
        if entity_type == 'Document':
            from app.models.document import Document
            entity = Document.query.get(entity_id)
            if entity:
                entity.status = status
        elif entity_type == 'Protocol':
            from app.models.validation import ValidationProtocol
            entity = ValidationProtocol.query.get(entity_id)
            if entity:
                entity.status = status
    
    @staticmethod
    def get_user_tasks(user_id, status=None):
        """Get tasks assigned to a user"""
        query = WorkflowTask.query.filter_by(assigned_to=user_id)
        
        if status:
            query = query.filter_by(status=status)
        
        return query.order_by(WorkflowTask.due_date.asc()).all()
    
    @staticmethod
    def check_overdue_tasks():
        """Check for overdue tasks and escalate"""
        overdue_tasks = WorkflowTask.query.filter(
            WorkflowTask.status == 'PENDING',
            WorkflowTask.due_date < datetime.utcnow(),
            WorkflowTask.escalated == False
        ).all()
        
        for task in overdue_tasks:
            task.is_overdue = True
            
            # Find manager to escalate to
            assigned_user = User.query.get(task.assigned_to)
            admin_users = User.query.filter_by(is_admin=True).all()
            
            if admin_users:
                escalate_to = admin_users[0]
                task.escalated = True
                task.escalated_to = escalate_to.id
                
                # Create escalation notification
                notification = Notification(
                    id=str(uuid.uuid4()),
                    user_id=escalate_to.id,
                    type='ESCALATION',
                    title=f'Overdue Task Escalated: {task.stage_name}',
                    message=f'Task assigned to {assigned_user.email} is overdue and has been escalated to you',
                    entity_type='WorkflowTask',
                    entity_id=task.id,
                    priority='URGENT'
                )
                db.session.add(notification)
        
        db.session.commit()
    
    @staticmethod
    def get_workflow_status(entity_type, entity_id):
        """Get current workflow status for an entity"""
        workflow = WorkflowInstance.query.filter_by(
            entity_type=entity_type,
            entity_id=entity_id
        ).order_by(WorkflowInstance.started_at.desc()).first()
        
        if not workflow:
            return None
        
        workflow_def = WorkflowDefinition.query.get(workflow.workflow_definition_id)
        
        return {
            'workflow_id': workflow.id,
            'status': workflow.status,
            'current_stage': workflow.current_stage,
            'total_stages': len(workflow_def.stages),
            'stages': workflow_def.stages,
            'tasks': [{
                'id': t.id,
                'stage_name': t.stage_name,
                'status': t.status,
                'assigned_to': User.query.get(t.assigned_to).email if t.assigned_to else None,
                'due_date': t.due_date.isoformat() if t.due_date else None,
                'is_overdue': t.is_overdue,
                'action_taken': t.action_taken,
                'completed_at': t.completed_at.isoformat() if t.completed_at else None
            } for t in workflow.tasks]
        }