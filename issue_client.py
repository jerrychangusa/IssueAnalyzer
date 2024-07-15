import os
from typing import List

from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport

from issue import Comment, Issue, IssueContent, Label

LABEL_TO_LINEAR_ID_MAP = {
    Label.BUG: '83f21759-814f-409d-9f21-93e3b37271a9',
    Label.FEATURE: 'b476cf81-b28d-456a-b507-435ed225b601'
}


def create_linear_client() -> Client:
    headers = {
        "Content-Type": "application/json",
        "Authorization": os.environ['LINEAR_API_KEY'],
    }
    transport = AIOHTTPTransport(url="https://api.linear.app/graphql",
                                 headers=headers)
    return Client(transport=transport, fetch_schema_from_transport=True)


def fetch_default_team_id(client: Client) -> str | None:
    query = gql("""
    query getTeams {
      teams {
        nodes {
          id
          name
        }
      }
    }
    """)
    result = client.execute(query)
    team_ids = [team['id'] for team in result['teams']['nodes']]
    return team_ids[0] if team_ids else None


class IssueClient:
    """A class to manage issues using the Linear API."""

    def __init__(self):
        self.client = create_linear_client()
        self.team_id = fetch_default_team_id(self.client)

    def create_issue(self, content: IssueContent) -> bool:
        """Creates a new issue

        Args:
            content: The issue content to be reported.
            
        Returns:
            Whether the issue was successfully created.
        """
        query = gql("""
        mutation CreateIssue($input: IssueCreateInput!) {
            issueCreate(input: $input) {
                success
                issue {
                    id
                    title
                    description
                }
            }
        }
        """)
        variables = {
            "input": {
                "teamId": self.team_id,
                "title": content.title,
                "description": content.description,
                "labelIds": [LABEL_TO_LINEAR_ID_MAP[content.label]],
                "priority": content.priority
            }
        }
        result = self.client.execute(query, variable_values=variables)
        return result.get('issueCreate', {}).get('success', False)

    def add_comment(self, comment: Comment) -> bool:
        """Adds a comment to an existing issue

        Args:
            comment: The comment to be added.

        Returns:
            Whether the comment was successfully added.
        """
        query = gql("""
        mutation AddCommentToIssue($input: CommentCreateInput!) {
          commentCreate(input: $input) {
            success
            comment {
              id
              body
              createdAt
            }
          }
        }
        """)
        variables = {
            "input": {
                "issueId": comment.issue_id,
                "body": comment.comment
            }
        }
        result = self.client.execute(query, variable_values=variables)
        return result.get('commentCreate', {}).get('success', False)

    def fetch_all_issues(self) -> List[Issue]:
        """Fetches all existing issues.

        Returns:
            A list of issues.
        """
        query = gql("""
            query getIssues {
              issues {
                nodes {
                  id
                  title
                  description
                  priority
                  labels {
                    nodes {
                        id
                        name
                    }
                 }
                }
              }
            }
        """)
        result = self.client.execute(query)
        issues = []
        for node in result['issues']['nodes']:
            label_ids = [
                label['id'] for label in node['labels']['nodes']
                if label['id'] in LABEL_TO_LINEAR_ID_MAP.values()
            ]
            if len(label_ids) > 1:
                raise ValueError(
                    f"Issue is labeled with both feature request and bug "
                    f"for issue {node['id']}: {label_ids}")

            if len(label_ids) == 1:
                for label, label_id in LABEL_TO_LINEAR_ID_MAP.items():
                    if label_id == label_ids[0]:
                        issues.append(
                            Issue(id=node['id'],
                                  content=IssueContent(
                                      title=node['title'],
                                      description=node['description'],
                                      label=label,
                                      priority=node['priority'])))
        return issues
