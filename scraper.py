import requests
from bs4 import BeautifulSoup

def scrape_website(url, detail_type):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an error for bad responses
        soup = BeautifulSoup(response.text, 'html.parser')

        if detail_type == "title":
            return soup.title.string if soup.title else "No title found", None

        elif detail_type == "meta":
            meta_tags = soup.find_all('meta')
            return [str(meta) for meta in meta_tags] if meta_tags else "No meta tags found", None

        elif detail_type == "headings":
            headings = {
                "h1": [h.text.strip() for h in soup.find_all('h1')],
                "h2": [h.text.strip() for h in soup.find_all('h2')],
                "h3": [h.text.strip() for h in soup.find_all('h3')],
            }
            return headings, None

        elif detail_type == "images":
            images = [img['src'] for img in soup.find_all('img') if 'src' in img.attrs]
            return images if images else "No images found", None

        elif detail_type == "links":
            links = [a['href'] for a in soup.find_all('a', href=True)]
            return links if links else "No links found", None

    except requests.exceptions.RequestException as e:
        return None, f"Error fetching the website: {str(e)}"
    except Exception as e:
        return None, f"An unexpected error occurred: {str(e)}"
