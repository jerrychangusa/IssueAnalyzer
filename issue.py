from dataclasses import dataclass
from enum import Enum


class Label(Enum):
  BUG = 0
  FEATURE = 1


@dataclass
class IssueContent:
  title: int
  description: str
  label: Label
  priority: int


@dataclass
class Issue:
  id: str
  content: IssueContent


@dataclass
class Comment:
  issue_id: str
  comment: str
