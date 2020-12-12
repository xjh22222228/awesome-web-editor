"""
Update star
Author: xiejiahe
@example python3 README_zh-CN.md
"""
import sys
import os
import re
from requests import get
from urllib.parse import urlparse

filename = sys.argv[1] if len(sys.argv) >= 2 else 'README.md'
file_path = os.path.join(os.getcwd(), filename)
access_token = os.environ.get('access_token')
headers = {}

if access_token:
    headers['Authorization'] = 'token ' + access_token


def get_star(repo_name):
    req_url = 'https://api.github.com/repos' + repo_name
    print('Fetching {}'.format(req_url))

    try:
        resp = get(req_url, headers=headers)
        if resp.status_code == 200:
            json = resp.json()
            star = json['stargazers_count']
            print('Success {} ★ {}\n'.format(req_url, str(star)))
            return True, star
        else:
            raise Exception()
    except:
        print('Failed {}\n'.format(req_url))
        return False, 0


def read_file():
    star_regex = r'(★\s\d+)'
    url_regex = r'\[.{1,}\]\(([^)]{1,})\)'

    with open(file_path, 'rt') as f:
        lines = f.readlines()
        for idx, line in enumerate(lines):
            search = re.search(url_regex, line, re.IGNORECASE)
            if search:
                g = search.group(1)
                try:
                    url = urlparse(g)
                    if url.hostname == 'github.com':
                        ok, star = get_star(url.path)

                        if not ok:
                            continue

                        lines[idx] = re.sub(star_regex, '★ ' + str(star), line)
                except:
                    pass

        with open(file_path, 'wt') as wf:
            wf.writelines(lines)


if __name__ == '__main__':
    read_file()
