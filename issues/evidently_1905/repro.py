"""evidently #1905: examples/README.md links to examples/tutorials/, which does not exist.

Needs internet. Downloads the README from the main branch, then asks GitHub whether the
folder it links to exists. `cookbook` is the control: it should exist. An open pull request
for this is evidently #1906.
"""
import re
import urllib.error
import urllib.request

RAW = "https://raw.githubusercontent.com/evidentlyai/evidently/main/examples/README.md"
TREE = "https://github.com/evidentlyai/evidently/tree/main/examples/"


def status(url):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, method="HEAD"), timeout=30) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code


readme = urllib.request.urlopen(RAW, timeout=30).read().decode("utf-8")
links = re.findall(r"\]\(\./(tutorials|cookbook)/\)", readme)
print("README links to:", sorted(set(links)))
codes = {name: status(TREE + name) for name in ("tutorials", "cookbook")}
print("GitHub answers :", codes)
print("STATUS:", "Reproduced" if "tutorials" in links and codes["tutorials"] == 404 else "Fixed")
