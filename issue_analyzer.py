import json
import logging
from typing import Any, Dict, List

from openai import OpenAI

from issue import Comment, Issue, IssueContent, Label
import tools


class IssueAnalyzer:
    """A class to manage issue detection and similarity checking."""

    def __init__(self, model: str = 'gpt-4o'):
        self.client = OpenAI()
        self.model = model

    def _detect_issues_prompt(self, transcript: str) -> str:
        return f"""
        Task: Analyze a given transcript to identify and describe potential bugs or feature requests.

        Given:
        1. Transcript Content: {transcript}

        Instructions:
        1. Carefully read and analyze the provided transcript.
        2. Identify any mentions of unresolved bugs (problems or unexpected behaviors) or feature requests (desired new functionalities or improvements).
        3. For each issue identified:
           a. Create a concise title that summarizes the issue.
           b. Write a detailed description of the issue.
           c. Determine whether it's a bug or a feature request.
           d. Assign a priority level (0-4) to the issue where 0 is no priority, 1 is Urgent, 2 is High, 3 is Medium, and 4 is Low.

        Output Format:
        - For each issue found, provide the structured information as described above.
        - If no bugs or feature requests need to be filed, do not create new issues.

        Note: 
        - Focus on substantial problems or requests, not minor or vague comments.
        - Ensure each issue is distinct to avoid duplicates.
        - For bugs, include steps to reproduce if mentioned in the transcript.
        - For feature requests, explain the user's motivation or the problem they're trying to solve.
        - Consider the context and prioritize issues that seem most impactful or frequently mentioned.
        
        Please analyze the transcript and provide structured descriptions of any issues you identify.
        """

    def _find_and_comment_prompt(self, content: IssueContent,
                                 existing_issues: List[Issue]) -> str:
        return f"""
        Task: Analyze a new issue against existing issues to identify duplicates or closely related items that can be solved together, preventing the creation of redundant entries in the issue tracking system.

        Given:
        1. New Issue Content: {content}
        2. List of Existing Issues: {existing_issues}

        Instructions:
        - Compare the new issue to existing issues based on the following criteria:
          a) The core problem or feature request is essentially the same
          b) The issues can be solved with the same solution or development effort

        Output Format:
        - If a genuine match is found:
          - Existing Issue ID: [ID]
          - Suggested Comment: A brief note highlighting that another user reported the same specific problem/request, including any new information or context from the new issue that adds value to the existing issue.
        - If no match is found, do not create a comment.

        Remember: It's better to not suggest a match than to suggest an incorrect one. Only suggest combining issues if they are truly duplicates or so closely related that solving one would directly solve the other.
        """

    def _get_tool_calls(self, prompt: str,
                        tool: Dict[str, Any]) -> List[Any] | None:
        """Returns ChatCompletionMessageToolCall objects for the given prompt and tool."""
        messages = [{'role': 'user', 'content': prompt}]

        response = self.client.chat.completions.create(
            model='gpt-4o',
            messages=messages,
            tools=[tool],
            tool_choice='auto',
        )
        if not response.choices or not response.choices[0].message:
            logging.error('No response from GPT-4')
            return None

        return response.choices[0].message.tool_calls

    def detect_issues(self, transcript: str) -> List[IssueContent]:
        """Detects issues in a conversation.

        Args:
            transcript: Customer support transcript to analyze.

        Returns:
            A list of detected issues.
        """
        tool_calls = self._get_tool_calls(
            self._detect_issues_prompt(transcript),
            tool=tools.CREATE_ISSUE_TOOL)
        if not tool_calls:
            logging.info('No tool calls found in detect_issues response.')
            return []

        issues = []
        for tool_call in tool_calls:
            if tool_call.type == 'function' and tool_call.function.name == 'create_issue':
                arguments = json.loads(tool_call.function.arguments)
                label = Label.BUG if arguments[
                    'label'] == 'bug' else Label.FEATURE
                issues.append(
                    IssueContent(title=arguments['title'],
                                 description=arguments['description'],
                                 label=label,
                                 priority=arguments['priority']))
        return issues

    def find_and_comment_on_similar_issues(
            self, content: IssueContent,
            existing_issues: List[Issue]) -> List[Comment]:
        """Finds issues similar to the given issue and generates comments for them.

        Args:
            content: The issue content to be compared.
            existing_issues: A list of existing issues.
        Returns:
            A list of comments for similar issues.
        """
        tool_calls = self._get_tool_calls(self._find_and_comment_prompt(
            content, existing_issues),
                                          tool=tools.ADD_COMMENT_TOOL)

        if not tool_calls:
            logging.info('No tool calls found in find_and_comment response.')
            return []

        comments = []
        for tool_call in tool_calls:
            if tool_call.type == 'function' and tool_call.function.name == 'add_comment':
                arguments = json.loads(tool_call.function.arguments)
                comments.append(
                    Comment(issue_id=arguments['issue_id'],
                            comment=arguments['comment']))
        return comments
