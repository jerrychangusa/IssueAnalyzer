import collections
import logging
from typing import Dict

import all_transcripts
from issue import Label
from issue_analyzer import IssueAnalyzer
from issue_client import IssueClient


def process_transcript(transcript: str) -> Dict[str, int]:
    """Processes transcripts and files issues.
    
    Args:
        transcript (str): The transcript to process.

    Returns:
        A dictionary containing the number of issues filed or comments added.
    """
    analyzer = IssueAnalyzer()
    client = IssueClient()

    new_issues = analyzer.detect_issues(transcript)
    existing_issues = client.fetch_all_issues()
    result = collections.defaultdict(int)

    for new_issue in new_issues:
        comments = analyzer.find_and_comment_on_similar_issues(
            new_issue, existing_issues)

        if comments:
            for comment in comments:
                is_success = client.add_comment(comment)

                if not is_success:
                    result['add_comment_errors'] += 1
                    logging.error(f'Failed to add comment {comment}')
                else:
                    result['added_comments'] += 1
                    logging.info(f'Added comment {comment}')

        else:
            is_success = client.create_issue(new_issue)

            if not is_success:
                result['new_issue_errors'] += 1
                logging.error(f'Failed to create issue {new_issue}')
            else:
                if new_issue.label == Label.BUG:
                    result['bug_created'] += 1
                    logging.info(f'Created bug {new_issue}')
                else:
                    result['feature_request_created'] += 1
                    logging.info(f'Created feature request {new_issue}')

    return result


def main():
    # Processes synthetic customer support transcripts.
    for name, transcript in all_transcripts.transcript_registry.items():
        print(f'Processing transcript: {name}')
        result = process_transcript(transcript)
        for key, val in result.items():
            print(f'{key}: {val}')


if __name__ == '__main__':
    main()
