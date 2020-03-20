import logging as log  # for verbose output
import os

import feedparser
import datetime

from .ProjectHolder import ProjectHolder


class MercurialRepoSession(ProjectHolder):
    REPO_URL_PROJECT_COMPONENTS = 1
    KNOWN_REPO_URLS = {
        'nginx.org': {
            'repo': 'nginx',
            'hostname': 'hg.nginx.org',
            'branches': {
                'stable': '\\.\\d?[02468]\\.',
                'mainline': '\\.\\d?[13579]\\.'
            }
        }
    }

    def __init__(self, repo, hostname):
        super(ProjectHolder, self).__init__()
        self.hostname = hostname
        self.repo = repo

    def get_latest(self, pre_ok=False, major=None):
        ret = None
        # to leverage cachecontrol, we fetch the feed using requests as usual
        # then feed the feed to feedparser as a raw string
        # e.g. https://hg.nginx.org/nginx/atom-tags
        r = self.get('https://{}/{}/atom-tags'.format(self.hostname, self.repo))
        feed = feedparser.parse(r.text)
        for tag in feed.entries:
            tag_name = tag['title']
            version = self.sanitize_version(tag_name, pre_ok, major)
            if not version:
                continue
            if not ret or version > ret['version']:
                ret = tag
                tag['tag_name'] = tag['title']
                tag['version'] = version
                # converting from struct
                tag['tag_date'] = datetime.datetime(*tag['published_parsed'][:6])
        return ret

# https://stackoverflow.com/questions/691519/regular-expression-to-match-only-odd-or-even-number
# https://pythonhosted.org/feedparser/common-atom-elements.html
# TODO adapter array should list how many elements make up "repo", e.g. for hg.nginx.com/repo it
#  is only one instead of 2
# https://pymotw.com/2/abc/
