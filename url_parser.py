import subprocess
import requests as req
from bs4 import BeautifulSoup as bs


# Get response from website with optional cookie
def get_website(url, **kwargs):
    cookies = kwargs.get("cookies")
    return req.get(url, cookies=cookies, allow_redirects=False)

# Start session for browser with optional cookie
def start_session(url, **kwargs):
    session = req.Session()
    cookies = kwargs.get("cookies")
    return session.get(url, cookies=cookies, allow_redirects=False)

# Convert web response to html
def parse_to_html(res):
    return bs(res.content, "html.parser")

# Print BeutifulSoup value to html file
def print_html_to_file(res):
    if (type(res) != bs):
        res = parse_to_html(res)
    with open("data.html","w", encoding="utf-8") as f:
        print(res.prettify(), file=f)