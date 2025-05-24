"""Email to Workflow Routing Engine

This module provides a rule-based routing system that maps email metadata
to appropriate workflow YAML files for execution.
"""

import re
import logging
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class RuleType(Enum):
    """Types of matching rules supported"""
    EXACT = "exact"          # Exact string match
    CONTAINS = "contains"    # Substring match
    REGEX = "regex"          # Regular expression match
    DOMAIN = "domain"        # Email domain match


@dataclass
class WorkflowRule:
    """Represents a single workflow routing rule"""
    name: str
    workflow_path: str
    priority: int = 0
    
    # Matching criteria
    from_email: Optional[Union[str, List[str]]] = None
    from_domain: Optional[Union[str, List[str]]] = None
    subject_contains: Optional[Union[str, List[str]]] = None
    subject_regex: Optional[str] = None
    has_attachment: Optional[bool] = None
    attachment_type: Optional[Union[str, List[str]]] = None
    
    # Additional conditions
    all_conditions: bool = True  # If True, all criteria must match
    enabled: bool = True
    
    def __post_init__(self):
        """Normalize list fields"""
        # Convert single strings to lists for easier processing
        for field_name in ['from_email', 'from_domain', 'subject_contains', 'attachment_type']:
            value = getattr(self, field_name)
            if isinstance(value, str):
                setattr(self, field_name, [value])


class EmailWorkflowRouter:
    """
    Routes emails to appropriate workflows based on configurable rules.
    
    Example usage:
        >>> config = {
        ...     "rules": [
        ...         {
        ...             "name": "newsletter_digest",
        ...             "workflow_path": "workflows/newsletter_digest.yaml",
        ...             "from_domain": "newsletter.example.com",
        ...             "subject_contains": ["digest", "newsletter"],
        ...             "priority": 10
        ...         },
        ...         {
        ...             "name": "pdf_processor",
        ...             "workflow_path": "workflows/pdf_ingestion.yaml",
        ...             "has_attachment": True,
        ...             "attachment_type": "application/pdf"
        ...         }
        ...     ],
        ...     "default_workflow": "workflows/generic_email.yaml"
        ... }
        >>> 
        >>> router = EmailWorkflowRouter(config)
        >>> workflow = router.select_workflow({
        ...     "from": "updates@newsletter.example.com",
        ...     "subject": "Weekly Digest: Tech News"
        ... })
        >>> print(workflow)
        workflows/newsletter_digest.yaml
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the router with configuration.
        
        Args:
            config: Configuration dictionary containing:
                - rules: List of rule dictionaries
                - default_workflow: Optional default workflow path
                - workflows_dir: Optional base directory for workflows
        """
        self.config = config
        self.rules: List[WorkflowRule] = []
        self.default_workflow = config.get('default_workflow')
        self.workflows_dir = Path(config.get('workflows_dir', 'workflows'))
        
        # Load and validate rules
        self._load_rules(config.get('rules', []))
        
        logger.info(f"Initialized EmailWorkflowRouter with {len(self.rules)} rules")
    
    def _load_rules(self, rules_config: List[Dict[str, Any]]):
        """Load and validate routing rules from configuration"""
        for rule_dict in rules_config:
            try:
                rule = WorkflowRule(**rule_dict)
                if rule.enabled:
                    self.rules.append(rule)
                    logger.debug(f"Loaded rule: {rule.name}")
            except Exception as e:
                logger.error(f"Invalid rule configuration: {e}")
                continue
        
        # Sort rules by priority (higher priority first)
        self.rules.sort(key=lambda r: r.priority, reverse=True)
    
    def select_workflow(self, metadata: Dict[str, Any]) -> Optional[str]:
        """
        Select the appropriate workflow based on email metadata.
        
        Args:
            metadata: Email metadata dictionary containing:
                - from: Sender email address
                - subject: Email subject
                - attachments: List of attachment info (optional)
                - body: Email body (optional)
        
        Returns:
            Path to the workflow YAML file, or None if no match
        """
        logger.debug(f"Selecting workflow for email from: {metadata.get('from')}")
        
        # Check each rule in priority order
        for rule in self.rules:
            if self._matches_rule(rule, metadata):
                workflow_path = self._resolve_workflow_path(rule.workflow_path)
                logger.info(f"Matched rule '{rule.name}' -> {workflow_path}")
                return workflow_path
        
        # Return default workflow if no rules match
        if self.default_workflow:
            workflow_path = self._resolve_workflow_path(self.default_workflow)
            logger.info(f"No rules matched, using default -> {workflow_path}")
            return workflow_path
        
        logger.warning("No matching workflow found and no default configured")
        return None
    
    def _matches_rule(self, rule: WorkflowRule, metadata: Dict[str, Any]) -> bool:
        """Check if email metadata matches a rule"""
        conditions = []
        
        # Check sender email
        if rule.from_email:
            sender = metadata.get('from', '').lower()
            matches = any(
                email.lower() in sender 
                for email in rule.from_email
            )
            conditions.append(matches)
        
        # Check sender domain
        if rule.from_domain:
            sender = metadata.get('from', '').lower()
            domain = sender.split('@')[-1] if '@' in sender else ''
            matches = any(
                domain == d.lower() or domain.endswith(f".{d.lower()}")
                for d in rule.from_domain
            )
            conditions.append(matches)
        
        # Check subject contains
        if rule.subject_contains:
            subject = metadata.get('subject', '').lower()
            matches = any(
                keyword.lower() in subject 
                for keyword in rule.subject_contains
            )
            conditions.append(matches)
        
        # Check subject regex
        if rule.subject_regex:
            subject = metadata.get('subject', '')
            try:
                matches = bool(re.search(rule.subject_regex, subject, re.IGNORECASE))
                conditions.append(matches)
            except re.error:
                logger.error(f"Invalid regex in rule '{rule.name}': {rule.subject_regex}")
                conditions.append(False)
        
        # Check attachments
        attachments = metadata.get('attachments', [])
        
        if rule.has_attachment is not None:
            has_attachments = len(attachments) > 0
            conditions.append(has_attachments == rule.has_attachment)
        
        if rule.attachment_type and attachments:
            attachment_types = [
                att.get('mimeType', '').lower() 
                for att in attachments
            ]
            matches = any(
                any(att_type == t.lower() or att_type.startswith(f"{t.lower()}/")
                    for att_type in attachment_types)
                for t in rule.attachment_type
            )
            conditions.append(matches)
        
        # Apply condition logic
        if not conditions:
            return False
        
        if rule.all_conditions:
            return all(conditions)
        else:
            return any(conditions)
    
    def _resolve_workflow_path(self, path: str) -> str:
        """Resolve workflow path relative to workflows directory"""
        if Path(path).is_absolute():
            return path
        # If path already starts with workflows_dir, return as is
        if path.startswith(str(self.workflows_dir) + '/'):
            return path
        return str(self.workflows_dir / path)
    
    def add_rule(self, rule: WorkflowRule):
        """Add a new rule to the router"""
        self.rules.append(rule)
        self.rules.sort(key=lambda r: r.priority, reverse=True)
        logger.info(f"Added rule: {rule.name}")
    
    def remove_rule(self, rule_name: str) -> bool:
        """Remove a rule by name"""
        original_count = len(self.rules)
        self.rules = [r for r in self.rules if r.name != rule_name]
        removed = len(self.rules) < original_count
        if removed:
            logger.info(f"Removed rule: {rule_name}")
        return removed
    
    def list_rules(self) -> List[Dict[str, Any]]:
        """List all configured rules"""
        return [
            {
                "name": rule.name,
                "workflow": rule.workflow_path,
                "priority": rule.priority,
                "enabled": rule.enabled,
                "criteria": {
                    "from_email": rule.from_email,
                    "from_domain": rule.from_domain,
                    "subject_contains": rule.subject_contains,
                    "subject_regex": rule.subject_regex,
                    "has_attachment": rule.has_attachment,
                    "attachment_type": rule.attachment_type,
                    "all_conditions": rule.all_conditions
                }
            }
            for rule in self.rules
        ]


# Sample configuration
SAMPLE_CONFIG = {
    "rules": [
        {
            "name": "ai_newsletter",
            "workflow_path": "workflows/ai_newsletter_digest.yaml",
            "from_domain": ["aiweekly.com", "mlnews.org"],
            "subject_contains": ["AI", "machine learning", "digest"],
            "priority": 20
        },
        {
            "name": "pdf_reports",
            "workflow_path": "workflows/pdf_report_processor.yaml",
            "subject_contains": ["report", "analysis"],
            "has_attachment": True,
            "attachment_type": "application/pdf",
            "priority": 15
        },
        {
            "name": "customer_feedback",
            "workflow_path": "workflows/customer_feedback.yaml",
            "from_email": ["feedback@", "support@"],
            "subject_regex": r"(feedback|review|complaint)",
            "priority": 10
        },
        {
            "name": "url_processor",
            "workflow_path": "workflows/url_ingestion.yaml",
            "subject_contains": ["check this out", "interesting article", "link:"],
            "priority": 5
        }
    ],
    "default_workflow": "workflows/generic_email_handler.yaml",
    "workflows_dir": "workflows"
}


# Testing and examples
if __name__ == "__main__":
    # Example 1: Newsletter routing
    router = EmailWorkflowRouter(SAMPLE_CONFIG)
    
    test_emails = [
        {
            "from": "editor@aiweekly.com",
            "subject": "AI Weekly Digest: Latest in Machine Learning",
            "attachments": []
        },
        {
            "from": "john@company.com",
            "subject": "Q4 Financial Report",
            "attachments": [{"mimeType": "application/pdf", "filename": "report.pdf"}]
        },
        {
            "from": "customer@gmail.com",
            "subject": "Feedback on your service",
            "attachments": []
        },
        {
            "from": "friend@example.com",
            "subject": "Check this out - interesting article on AI",
            "attachments": []
        },
        {
            "from": "random@example.com",
            "subject": "Hello",
            "attachments": []
        }
    ]
    
    print("Email Workflow Routing Examples:")
    print("-" * 60)
    
    for email in test_emails:
        workflow = router.select_workflow(email)
        print(f"From: {email['from']}")
        print(f"Subject: {email['subject']}")
        print(f"Attachments: {len(email['attachments'])}")
        print(f"→ Workflow: {workflow}")
        print("-" * 60)