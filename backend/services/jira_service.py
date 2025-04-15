import aiohttp
from typing import List, Optional
from ..models.jira import Project, Task, Comment

class JiraService:
    def __init__(self, token: str):
        self.token = token
        self.base_url = "https://api.atlassian.com/ex/jira"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    async def _make_request(self, method: str, endpoint: str, **kwargs) -> dict:
        """Make an HTTP request to the Jira API"""
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}{endpoint}"
            async with session.request(method, url, headers=self.headers, **kwargs) as response:
                if response.status >= 400:
                    error_text = await response.text()
                    raise Exception(f"Jira API error: {error_text}")
                return await response.json()

    async def get_projects(self) -> List[Project]:
        """Get all projects the user has access to"""
        response = await self._make_request("GET", "/rest/api/3/project")
        return [Project(**project) for project in response]

    async def get_tasks(
        self,
        project_key: str,
        status: Optional[str] = None,
        assignee: Optional[str] = None
    ) -> List[Task]:
        """Get tasks from a specific project with optional filters"""
        jql = f"project = {project_key}"
        if status:
            jql += f" AND status = {status}"
        if assignee:
            jql += f" AND assignee = {assignee}"

        response = await self._make_request(
            "GET",
            f"/rest/api/3/search?jql={jql}"
        )
        return [Task(**issue) for issue in response["issues"]]

    async def add_comment(self, task_id: str, body: str) -> dict:
        """Add a comment to a specific task"""
        data = {"body": body}
        return await self._make_request(
            "POST",
            f"/rest/api/3/issue/{task_id}/comment",
            json=data
        )

    async def create_task(self, task: Task) -> dict:
        """Create a new task in the specified project"""
        data = {
            "fields": {
                "project": {"key": task.key.split("-")[0]},
                "summary": task.summary,
                "description": task.description,
                "issuetype": {"name": "Task"}
            }
        }
        if task.assignee:
            data["fields"]["assignee"] = {"name": task.assignee}

        return await self._make_request(
            "POST",
            "/rest/api/3/issue",
            json=data
        )

    async def update_task(self, task_id: str, task: Task) -> dict:
        """Update an existing task"""
        data = {
            "fields": {
                "summary": task.summary,
                "description": task.description
            }
        }
        if task.assignee:
            data["fields"]["assignee"] = {"name": task.assignee}

        return await self._make_request(
            "PUT",
            f"/rest/api/3/issue/{task_id}",
            json=data
        ) 