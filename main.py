import httpx
from selectolax.parser import HTMLParser
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
# Define the Selenium Grid hub URL
grid_hub_url = "http://localhost:4444/wd/hub"


def main():
    grid_hub_url = "http://localhost:4444/wd/hub"  # Update with your Selenium Grid hub URL

    # Define Chrome options with desired capabilities
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--start-maximized')  # Example: Start the browser maximized

    driver = webdriver.Remote(
        grid_hub_url,
        chrome_options.to_capabilities()
    )


def get_html(baseurl, page):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:10.0) Gecko/20100101 Firefox/111.0"
    }
    resp = httpx.get(baseurl + str(page), headers=headers, follow_redirects=True)
    if resp.text == '':
        print(f"Blank response for {resp.url}.")
        return False
    try:
        resp.raise_for_status()
        return HTMLParser(resp.text)
    except httpx.HTTPStatusError as exc:
        print(f"Error response {exc.response.status_code} while requesting {exc.request.url!r}. Page Limit Exceeded")
        return False

def extract_text(html, sel):
    try:
        return html.css_first(sel).text()
    except AttributeError:
        return None

def parse_page(html):
    products = html.css("li.VcGDfKKy_dvNbxUqm29K")
    for product in products:
        item = {
           "name": extract_text(product, "span[data-ui='product-title']"),
            "price": extract_text(product, "span[data-ui='sale-price']"),
            "savings": extract_text(product, "span[data-ui='savings']"),
        }
        yield item

def main():
    baseurl = "https://www.rei.com/c/camping-and-hiking/f/scd-deals?page="

    # Create a WebDriver instance that connects to the Selenium Grid hub
    driver = webdriver.Remote(grid_hub_url, webdriver.DesiredCapabilities.CHROME)

    for x in range(1, 100):
        print(f"Gathering page: {x}")
        html = get_html(baseurl, x)
        if html is False:
            # If getting HTML fails, log an error message and break from the loop to stop further processing
            print(f'Error occurred when fetching page {x}. Stopping the scraping process.')
            break
        data = parse_page(html)
        # Open a file in append mode to save the product details
        with open('product_details.txt', 'a') as file:
            for item in data:
                # Writing product details to the file
                file.write(f'{item}\n')

        # Delay between requests to avoid overloading the server
        time.sleep(1)

    # Close the browser
    driver.quit()

if __name__ == "__main__":
    main()
