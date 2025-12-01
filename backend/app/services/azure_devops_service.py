"""Azure DevOps integration service"""
import os
from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
from typing import List, Dict, Optional

class AzureDevOpsService:
    def __init__(self):
        self.organization = os.getenv('AZURE_DEVOPS_ORGANIZATION')
        self.pat = os.getenv('AZURE_DEVOPS_PAT')
        self.client = None
        
        if self.organization and self.pat:
            try:
                credentials = BasicAuthentication('', self.pat)
                connection = Connection(
                    base_url=f'https://dev.azure.com/{self.organization}',
                    creds=credentials
                )
                self.client = connection
            except Exception as e:
                print(f"Failed to initialize Azure DevOps client: {e}")
    
    def is_connected(self) -> bool:
        """Check if Azure DevOps connection is active"""
        return self.client is not None
    
    def sync_work_items(self, project_name: str) -> List[Dict]:
        """Import work items from Azure DevOps project"""
        if not self.client:
            return []
        
        try:
            # Get work item tracking client
            wit_client = self.client.clients.get_work_item_tracking_client()
            
            # Query work items
            wiql = f"""
            SELECT [System.Id], [System.Title], [System.Description], [System.State]
            FROM WorkItems
            WHERE [System.TeamProject] = '{project_name}'
            ORDER BY [System.Id]
            """
            
            query_result = wit_client.query_by_wiql({'query': wiql})
            
            work_items = []
            if query_result.work_items:
                ids = [item.id for item in query_result.work_items[:100]]
                items = wit_client.get_work_items(ids, expand='All')
                
                for item in items:
                    work_items.append({
                        'external_id': f'ADO-{item.id}',
                        'title': item.fields['System.Title'],
                        'description': item.fields.get('System.Description', ''),
                        'status': item.fields['System.State'],
                        'work_item_type': item.fields['System.WorkItemType'],
                        'source': f'Azure DevOps: {item.id}'
                    })
            
            return work_items
        except Exception as e:
            print(f"Failed to sync from Azure DevOps: {e}")
            return []
    
    def create_work_item(self, project_name: str, item_data: Dict) -> Optional[str]:
        """Create work item in Azure DevOps"""
        if not self.client:
            return None
        
        try:
            wit_client = self.client.clients.get_work_item_tracking_client()
            
            document = [
                {
                    'op': 'add',
                    'path': '/fields/System.Title',
                    'value': item_data['title']
                },
                {
                    'op': 'add',
                    'path': '/fields/System.Description',
                    'value': item_data.get('description', '')
                }
            ]
            
            work_item = wit_client.create_work_item(
                document=document,
                project=project_name,
                type='User Story'
            )
            
            return str(work_item.id)
        except Exception as e:
            print(f"Failed to create work item: {e}")
            return None