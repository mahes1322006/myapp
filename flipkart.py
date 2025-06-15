import requests
from bs4 import BeautifulSoup
from urllib.parse import quote

def check_flipkart_availability(product_name):
    search_url = f"https://www.flipkart.com/search?q={quote(product_name)}"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(search_url, headers=headers)

    if response.status_code != 200:
        return False, None

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Flipkart item selector (simplified, may need updating)
    products = soup.find_all("a", {"class": "_1fQZEK"})

    if not products:
        products = soup.find_all("a", {"class": "_2rpwqI"})

    if products:
        product_link = "https://www.flipkart.com" + products[0].get("href")
        return True, product_link

    return False, None
