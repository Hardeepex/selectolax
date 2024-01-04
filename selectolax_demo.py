import requests
from selectolax.parser import HTMLParser


def get_html(url):
    response = requests.get(url)
    html = HTMLParser(response.text)
    return html

def extract_links(html):
    links = [node.attrs.get('href') for node in html.css('a')]
    return links

def main():
    url = 'https://www.example.com'
    html = get_html(url)
    links = extract_links(html)
    print(links)

if __name__ == "__main__":
    main()
