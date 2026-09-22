"""evidently #1898: the LLM quickstart uses DeclineLLMEval but never says to install openai.

Needs internet. The docs live in a separate repo (evidentlyai/docs). This reads the quickstart
source and looks for an install line that includes openai. The code side is informational:
DeclineLLMEval defaults to provider="openai", and a plain `pip install evidently` has no openai.
Open pull request: evidentlyai/docs #2 (the earlier docs #3 was closed without merging).
"""
import importlib.util
import re
import urllib.request

URL = "https://raw.githubusercontent.com/evidentlyai/docs/main/quickstart_llm.mdx"
text = urllib.request.urlopen(URL, timeout=30).read().decode("utf-8")
installs = re.findall(r"pip install[^\n]*", text)
uses_decline = "DeclineLLMEval" in text
mentions_openai = any("openai" in line.lower() for line in installs)
print("install lines in the quickstart:", installs)
print("uses DeclineLLMEval:", uses_decline, "| an install line mentions openai:", mentions_openai)
print("openai installed in this environment:", importlib.util.find_spec("openai") is not None)
print("STATUS:", "Reproduced" if uses_decline and not mentions_openai else "Fixed")
