import requests
import xml.etree.cElementTree as xml
from urllib.parse import urlparse

xml_propfind = '<?xml version="1.0" encoding="utf-8"?><propfind xmlns="DAV:"><prop><checked-in xmlns="DAV:"/><version-name xmlns="DAV:"/></prop></propfind>'


class PublicSvn():
    name = "PublicSvn"

    def __init__(self, credential):
        credential.uuid = None

    def validate(self):
        return False

    def list_branches(self, url):
        return [b['name'] for b in self.get_last_commit_for_branches(url)]

    def get_versions_for_branch(self, url):

        headers = {
            "User-Agent": "SVN/1.14.2 (x86_64-redhat-linux-gnu) serf/1.3.9",
            "Depth": "1",
            "Content-Type": "text/xml",
        }

        if 'trunk' in url:
            headers['Depth'] = "0"

        res = requests.request("PROPFIND", url, headers=headers, data=xml_propfind)
        tree = xml.fromstring(res.content)
        entries = set()

        if 'trunk' in url:
            prefix = ''
            elements = tree.findall('{DAV:}response')
        else:
            prefix = url.split('/')[-2] + "/"
            elements = tree.findall('{DAV:}response')[1:]

        for elem in elements:
            link = elem.find('{DAV:}href').text.split('/')[-2]
            version = elem.find('.//{DAV:}version-name').text
            entries.add((prefix + link, version))
        return entries

    def get_bases_url(self, url):
        up = urlparse(url)
        base_url = up.scheme + "://" + up.netloc
        headers = {
            "User-Agent": "SVN/1.14.2 (x86_64-redhat-linux-gnu) serf/1.3.9",
            "Depth": "1",
            "Content-Type": "text/xml",
        }

        res = requests.request("PROPFIND", url, headers=headers, data=xml_propfind)
        tree = xml.fromstring(res.content)
        entries = []

        for elem in tree.findall('{DAV:}response')[1:]:
            link = elem.find('{DAV:}href').text
            if link.split("/")[-2] in ['tags', 'trunk', 'branches']:
                entries.append(base_url + link)
        return entries

    def get_last_commit_for_branches(self, url):
        results = []
        entries = self.get_bases_url(url)
        for e in entries:
            for b in self.get_versions_for_branch(e):
                results.append({
                    "name": b[0],
                    "last_commit": b[1],
                })
        return results
