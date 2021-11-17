from github import Github
import os

token = ""
# using an access token
g = Github(token)

repo = g.get_repo("AC-GopherBot/test-1")
markdown_sample = """|    |   assignment1 |   assignment2 |   assignment3 |
|---:|--------------:|--------------:|--------------:|
|  0 |             4 |             6 |          1234 |
|  1 |            87 |            45 |           357 |
|  2 |           132 |          1234 |         43327 |
"""
repo.create_issue(title="This is a very new issue", body=markdown_sample)
# issue = repo.get_issue(number=1)
# issue.create_comment("Hello from python\n" + markdown_sample)
