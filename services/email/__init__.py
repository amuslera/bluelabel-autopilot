"""Email services for workflow triggering"""

# Components will be imported when dependencies are available
# from .email_gateway import GmailInboxWatcher, EmailEvent
# from .email_workflow_router import EmailWorkflowRouter, WorkflowRule, RuleType
# from .email_workflow_orchestrator import EmailWorkflowOrchestrator
from .email_dag_connector import EmailDAGConnector, MockEmailListener

__all__ = [
    # 'GmailInboxWatcher', 
    # 'EmailEvent',
    # 'EmailWorkflowRouter',
    # 'WorkflowRule',
    # 'RuleType',
    # 'EmailWorkflowOrchestrator',
    'EmailDAGConnector',
    'MockEmailListener'
]