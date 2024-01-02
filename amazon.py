from typing import List, Optional
from selectolax.parser import HTMLParser
from attrs import define
from rich import print as rprint
import csv
from selenium import webdriver
from concurrent.futures import ThreadPoolExecutor

@define
class Review:
    title: Optional[str]
    helpful: Optional[str]
    body: Optional[str]

@define
class Item:
    asin: str
    title: Optional[str]
    reviews: List[Review]

def extract(html, selector, output):
    element = html.css_first(selector)
    if element is not None:
        if output == "text":
            return element.text(strip=True)
        elif output == "attrs":
            return element.attributes

def parse_html(html):
    reviews = html.css("div[data-hook=review]")
    for review in reviews:
        yield Review(
            title=extract(review, "span[data-hook=review-title] span", output="text"),
            helpful=extract(review, "span[data-hook=review-helpful] span", output="text"),  # Add logic to extract `helpful`
            body=extract(review, "span[data-hook=review-body] span", output="text")  # Add logic to extract `body`
        )

def pagination(html):
    next_page = html.css_first("li.a-last a")
    if next_page is None:
        return False

def load_products():
    with open("products.csv", newline="") as f:
        reader = csv.reader(f)
        return [item[0] for item in list(reader)]

def run(product):
    total_pages = 5

    options = webdriver.ChromeOptions()
    driver = webdriver.Remote(
        command_executor="http://172.18.0.3:5555", options=options
    )
    for page in range(1, int(total_pages) + 1):
        url = f"https://www.amazon.co.uk/product-reviews/{product.asin}/?pageNumber={page}"
        rprint(url)
        driver.get(url)
        html = HTMLParser(driver.page_source)
        product.title = extract(html, "a[data-hook=product-link]", "text")

        for item in parse_html(html):
            product.reviews.append(item)
            rprint(item)
        if not pagination(html):
            rprint("no more pages")
            break
    driver.quit()

def main():
    items = [Item(asin=item, title=None, reviews=[]) for item in load_products()]

    with ThreadPoolExecutor() as executor:
        executor.map(run, items)

if __name__ == "__main__":
    main()
