"""
Update star
Author: xiejiahe
@example python3 star.py README_zh-CN.md
"""
import sys
import os
import re
from requests import get
from operator import itemgetter
from urllib.parse import urlparse

filename = sys.argv[1] if len(sys.argv) >= 2 else 'README.md'
file_path = os.path.join(os.getcwd(), filename)
access_token = os.environ.get('github_access_token')
headers = {}

if access_token:
    headers['Authorization'] = 'token ' + access_token


def get_star(repo_name):
    req_url = 'https://api.github.com/repos' + repo_name
    resp = get(req_url, headers=headers)
    print('Fetching {}'.format(req_url))

    try:
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
    star_regex = re.compile(r'(★\s\d+)')
    url_regex = re.compile(r'\[.+\]\(([^)]+)\)', re.IGNORECASE)
    sort_lines = []

    with open(file_path, 'rt') as f:
        lines = f.readlines()
        for idx, line in enumerate(lines):
            search = url_regex.search(line)
            if search:
                try:
                    result = search.group(1)
                    url = urlparse(result)
                    if url.hostname == 'github.com':
                        ok, star = get_star(url.path)

                        if not ok:
                            continue

                        lines[idx] = star_regex.sub('★ ' + str(star), line)
                except:
                    pass

        # 二级列表根据star降序
        for line in lines:
            # 二级
            if line.startswith('  - '):
                search_star = star_regex.search(line)
                star = search_star.groups(0)[0].replace('★ ', '') if search_star else 0
                if not isinstance(sort_lines[-1], list):
                    sort_lines.append([])
                sort_lines[-1].append({
                    'star': int(star),
                    'content': line
                })
            else:
                # 排序
                if sort_lines and isinstance(sort_lines[-1], list):
                    sort_list = sorted(sort_lines[-1], key=itemgetter('star'), reverse=True)
                    sort_lines.pop()
                    for item in sort_list:
                        sort_lines.append(item['content'])

                sort_lines.append(line)

        with open(file_path, 'wt') as wf:
            wf.writelines(sort_lines)
            print('\n\n Finished!')


if __name__ == '__main__':
    read_file()
