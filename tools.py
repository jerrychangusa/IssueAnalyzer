"""Tools used for issue detection and analysis."""

CREATE_ISSUE_TOOL = {
    "type": "function",
    "function": {
        "name": "create_issue",
        "description": "Files a feature request or bug.",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Title of the feature request or bug.",
                },
                "description": {
                    "type": "string",
                    "description": "Contents of the feature request or bug",
                },
                "label": {
                    "type": "string",
                    "enum": ["bug", "feature_request"]
                },
                "priority": {
                    "type": "integer",
                    "description": "Priority of the feature request or bug",
                }
            },
            "required": ["title", "description", "label", "priority"],
        },
    },
}

ADD_COMMENT_TOOL = {
    "type": "function",
    "function": {
        "name": "add_comment",
        "description": "Adds a comment to an existing feature request or bug.",
        "parameters": {
            "type": "object",
            "properties": {
                "issue_id": {
                    "type": "string",
                    "description":
                    "Id of the existing feature request or bug.",
                },
                "comment": {
                    "type": "string",
                    "description":
                    "The text content of the comment to be added.",
                },
            },
            "required": [
                "issue_id",
                "comment",
            ],
        },
    },
}
