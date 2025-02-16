import requests
from requests import Session
from bs4 import BeautifulSoup
from typing import Optional, Union

def get_website(url: str, **kwargs) -> Optional[requests.Response]:
    """
    Fetches the given URL using GET with optional cookies and returns the Response object.
    
    :param url: The URL to fetch.
    :param kwargs: Optional keyword arguments:
        - cookies (dict): cookies to include in the request
        - headers (dict): additional headers
    :return: A requests.Response object if successful, otherwise None on failure.
    """
    cookies = kwargs.get("cookies")
    headers = kwargs.get("headers", {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                      " AppleWebKit/537.36 (KHTML, like Gecko)"
                      " Chrome/58.0.3029.110 Safari/537.3"
    })
    try:
        resp = requests.get(url, cookies=cookies, headers=headers, allow_redirects=False)
        resp.raise_for_status()
        return resp
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None


def start_session(url: str, **kwargs) -> Optional[requests.Response]:
    """
    Starts a Session, optionally with cookies, and fetches the given URL.

    :param url: The URL to fetch.
    :param kwargs: Optional keyword arguments:
        - cookies (dict): cookies to include in the request
        - headers (dict): additional headers
    :return: A requests.Response object if successful, otherwise None on failure.
    """
    cookies = kwargs.get("cookies")
    headers = kwargs.get("headers", {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                      " AppleWebKit/537.36 (KHTML, like Gecko)"
                      " Chrome/58.0.3029.110 Safari/537.3"
    })
    session = Session()
    try:
        resp = session.get(url, cookies=cookies, headers=headers, allow_redirects=False)
        resp.raise_for_status()
        return resp
    except requests.exceptions.RequestException as e:
        print(f"Error starting session for {url}: {e}")
        return None


def parse_to_html(res: Union[requests.Response, None]) -> Optional[BeautifulSoup]:
    """
    Converts a Response object to a BeautifulSoup (HTML parser) object.

    :param res: A requests.Response object or None.
    :return: A BeautifulSoup object if successful, otherwise None.
    """
    if res is None:
        return None
    try:
        return BeautifulSoup(res.content, "html.parser")
    except Exception as e:
        print(f"Error parsing response to HTML: {e}")
        return None


def print_html_to_file(res: Union[requests.Response, BeautifulSoup, None], 
                       filename: str = "data.html") -> None:
    """
    Prints the prettified HTML to a file.

    :param res: Either a requests.Response, a BeautifulSoup object, or None.
    :param filename: Output file name (default "data.html").
    """
    if res is None:
        print(f"No response to print for {filename}.")
        return

    soup: Optional[BeautifulSoup]
    if isinstance(res, BeautifulSoup):
        soup = res
    else:
        soup = parse_to_html(res)

    if soup is None:
        print(f"Could not parse HTML for {filename}.")
        return

    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(soup.prettify())
        print(f"HTML output written to {filename}")
    except IOError as e:
        print(f"Error writing to {filename}: {e}")
