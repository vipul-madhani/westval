"""Jira integration service for bidirectional sync"""
import os
from jira import JIRA
from typing import List, Dict, Optional

class JiraService:
    def __init__(self):
        self.jira_url = os.getenv('JIRA_URL')
        self.jira_email = os.getenv('JIRA_EMAIL')
        self.jira_token = os.getenv('JIRA_API_TOKEN')
        self.client = None
        
        if all([self.jira_url, self.jira_email, self.jira_token]):
            try:
                self.client = JIRA(
                    server=self.jira_url,
                    basic_auth=(self.jira_email, self.jira_token)
                )
            except Exception as e:
                print(f"Failed to initialize Jira client: {e}")
    
    def is_connected(self) -> bool:
        """Check if Jira connection is active"""
        return self.client is not None
    
    def sync_requirements_from_jira(self, project_key: str) -> List[Dict]:
        """Import requirements from Jira project"""
        if not self.client:
            return []
        
        try:
            # Search for issues in project
            issues = self.client.search_issues(
                f'project={project_key}',
                maxResults=100
            )
            
            requirements = []
            for issue in issues:
                requirements.append({
                    'external_id': issue.key,
                    'title': issue.fields.summary,
                    'description': issue.fields.description or '',
                    'priority': str(issue.fields.priority) if issue.fields.priority else 'Medium',
                    'status': str(issue.fields.status),
                    'issue_type': str(issue.fields.issuetype),
                    'source': f'Jira: {issue.key}'
                })
            
            return requirements
        except Exception as e:
            print(f"Failed to sync from Jira: {e}")
            return []
    
    def create_jira_issue(self, project_key: str, requirement_data: Dict) -> Optional[str]:
        """Create Jira issue from requirement"""
        if not self.client:
            return None
        
        try:
            issue_dict = {
                'project': {'key': project_key},
                'summary': requirement_data['title'],
                'description': requirement_data.get('description', ''),
                'issuetype': {'name': 'Story'}
            }
            
            new_issue = self.client.create_issue(fields=issue_dict)
            return new_issue.key
        except Exception as e:
            print(f"Failed to create Jira issue: {e}")
            return None
    
    def sync_test_results_to_jira(self, issue_key: str, test_results: Dict) -> bool:
        """Update Jira issue with test execution results"""
        if not self.client:
            return False
        
        try:
            issue = self.client.issue(issue_key)
            
            comment = f"""Test Execution Results:
            Test Case: {test_results.get('test_case_id')}
            Status: {test_results.get('status')}
            Executed: {test_results.get('executed_at')}
            Result: {test_results.get('actual_result', 'N/A')}
            """
            
            self.client.add_comment(issue, comment)
            
            # Update status if test passed
            if test_results.get('status') == 'Passed':
                transitions = self.client.transitions(issue)
                for t in transitions:
                    if t['name'].lower() in ['done', 'closed', 'resolved']:
                        self.client.transition_issue(issue, t['id'])
                        break
            
            return True
        except Exception as e:
            print(f"Failed to sync test results: {e}")
            return False
    
    def get_project_info(self, project_key: str) -> Optional[Dict]:
        """Get Jira project information"""
        if not self.client:
            return None
        
        try:
            project = self.client.project(project_key)
            return {
                'key': project.key,
                'name': project.name,
                'lead': str(project.lead),
                'description': project.description
            }
        except Exception as e:
            print(f"Failed to get project info: {e}")
            return None