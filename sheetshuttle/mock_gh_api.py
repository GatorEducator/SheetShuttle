"""Implement mock APIs for github for the purposes of testing"""


class MockGH:
    """Supports the used mock functionalities of GitHub API"""

    def __init__(self) -> None:
        self.name = "gh-mock-api"
        self.repos = {}

    def get_repo(self, repo_name: str):
        """Mimics the return of a repo object.

        Args:
            repo_name (str): name of the repo to create and return
        """
        if repo_name not in self.repos:
            self.repos[repo_name] = MockRepo(repo_name)
        return self.repos[repo_name]


class MockRepo:
    """Create mock repos with posting functionalities"""

    def __init__(self, name: str) -> None:
        self.name = name
        # create empty issue to start with
        self.issues = [MockIssue("empty", "empty", number=1, labels=["empty"])]
        self.issues_last_index = 0

    def create_issue(self, title: str, body: str, labels=None):
        """Mock the create issue function."""
        self.issues_last_index += 1
        issue = MockIssue(title, body, labels=labels, number=self.issues_last_index)
        self.issues = [issue] + self.issues
        return issue

    def get_issues(self, state="all"):
        return list(self.issues)

    def get_issue(self, number: int):
        return self.issues[number - 1]


class MockIssue:
    """Create mock issue tracker with body, title, and labels information"""

    def __init__(self, title: str, body: str, number: int, labels=None) -> None:
        self.title = title
        self.body = body
        self.number = number
        self.labels = []
        if labels:
            for label in labels:
                self.labels.append(MockLabel(label))
        self.comments = []
        self.state = "open"

    def create_comment(self, body: str):
        self.comments.append(MockComment(body))

    def get_comments(self):
        return self.comments

    def add_to_labels(self, label_name: str):
        self.labels.append(MockLabel(label_name))

    def edit(self, state: str):
        self.state = state


class MockLabel:
    """Create mock label with name infomation."""

    def __init__(self, name: str) -> None:
        self.name = name


class MockComment:
    """Create mock comment with body infomation."""

    def __init__(self, body: str) -> None:
        self.body = body
