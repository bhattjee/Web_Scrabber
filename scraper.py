import requests  # Importing the requests library to handle HTTP requests
from bs4 import BeautifulSoup  # Importing BeautifulSoup for parsing HTML

def scrape_website(url, detail_type):
    try:
        # Sending a GET request to the specified URL
        response = requests.get(url)
        
        # Raise an error if the response was not successful (status codes 4xx or 5xx)
        response.raise_for_status()  
        
        # Parsing the HTML content of the page using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # If the user wants the title of the webpage
        if detail_type == "title":
            # Return the title text if it exists, otherwise return a message
            return soup.title.string if soup.title else "No title found", None

        # If the user wants to scrape meta tags
        elif detail_type == "meta":
            # Find all <meta> tags and convert them to string format
            meta_tags = soup.find_all('meta')
            return [str(meta) for meta in meta_tags] if meta_tags else "No meta tags found", None

        # If the user wants to scrape headings (h1, h2, h3)
        elif detail_type == "headings":
            # Create a dictionary to hold headings of different levels
            headings = {
                "h1": [h.text.strip() for h in soup.find_all('h1')],
                "h2": [h.text.strip() for h in soup.find_all('h2')],
                "h3": [h.text.strip() for h in soup.find_all('h3')],
            }
            return headings, None  # Return the headings dictionary

        # If the user wants to scrape images
        elif detail_type == "images":
            # Extract the 'src' attribute from all <img> tags
            images = [img['src'] for img in soup.find_all('img') if 'src' in img.attrs]
            return images if images else "No images found", None

        # If the user wants to scrape links
        elif detail_type == "links":
            # Extract the 'href' attribute from all <a> tags
            links = [a['href'] for a in soup.find_all('a', href=True)]
            return links if links else "No links found", None

    except requests.exceptions.RequestException as e:
        # Handle request-related exceptions and return an error message
        return None, f"Error fetching the website: {str(e)}"
    except Exception as e:
        # Handle any unexpected exceptions and return an error message
        return None, f"An unexpected error occurred: {str(e)}"
