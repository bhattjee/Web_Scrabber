from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import validators

app = Flask(__name__)

# Helper function to get all data from the website
def scrape_website_data(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    data = {
        'images': [img.get('src') for img in soup.find_all('img') if img.get('src')],
        'links': [a.get('href') for a in soup.find_all('a', href=True) if validators.url(a.get('href'))],
        'favicons': [link.get('href') for link in soup.find_all('link', rel='icon')],
        'stylesheets': [link.get('href') for link in soup.find_all('link', rel='stylesheet')],
        'scripts': [script.get('src') for script in soup.find_all('script') if script.get('src')],
        'headings': {
            'h1': [h.text.strip() for h in soup.find_all('h1')],
            'h2': [h.text.strip() for h in soup.find_all('h2')],
            'h3': [h.text.strip() for h in soup.find_all('h3')],
            'h4': [h.text.strip() for h in soup.find_all('h4')],
            'h5': [h.text.strip() for h in soup.find_all('h5')],
            'h6': [h.text.strip() for h in soup.find_all('h6')]
        },
        'meta_tags': [meta.attrs for meta in soup.find_all('meta')]
    }
    return data

# New function to perform search within the scraped data
def search_in_data(data, search_term):
    filtered_links = [link for link in data['links'] if search_term.lower() in link.lower()]
    filtered_images = [img for img in data['images'] if search_term.lower() in img.lower()]
    
    return {
        'links': filtered_links,
        'images': filtered_images
    }

# New function to perform dynamic search
def dynamic_search(base_url, search_term):
    search_url = f"{base_url}?q={search_term.replace(' ', '+')}"
    response = requests.get(search_url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        results = []

        # Adjust this selector based on the actual structure of the search results page
        for item in soup.find_all('li', class_='search-results__item'):  # Change to the correct class
            title = item.find('h3')
            link = item.find('a', href=True)
            if title and link:
                results.append({
                    'title': title.text.strip(),
                    'url': link['href']
                })
        return results
    else:
        print("Failed to retrieve search results")
        return []

# Route for the homepage
@app.route('/')
def index():
    return render_template('index.html')

# Route to scrape the website based on user input
@app.route('/scrape', methods=['POST'])
def scrape():
    url = request.form['url']
    selection = request.form.get('selection')
    search_term = request.form.get('search_term')

    # If a search term is provided, perform a dynamic search instead
    if search_term:
        results = dynamic_search(url, search_term)
        return render_template('result.html', data={'results': results}, display_type='search')
    
    # Scrape the website normally
    data = scrape_website_data(url)

    # Render results based on the selection
    if selection == 'images':
        return render_template('result.html', data={'images': data['images']}, display_type='images')
    elif selection == 'links':
        return render_template('result.html', data={'links': data['links']}, display_type='links')
    elif selection == 'favicons':
        return render_template('result.html', data={'favicons': data['favicons']}, display_type='favicons')
    elif selection == 'stylesheets':
        return render_template('result.html', data={'stylesheets': data['stylesheets']}, display_type='stylesheets')
    elif selection == 'scripts':
        return render_template('result.html', data={'scripts': data['scripts']}, display_type='scripts')
    elif selection == 'headings':
        return render_template('result.html', data={'headings': data['headings']}, display_type='headings')
    elif selection == 'meta_tags':
        return render_template('result.html', data={'meta_tags': data['meta_tags']}, display_type='meta_tags')
    elif selection == 'all':
        return render_template('result.html', data=data, display_type='all')
    else:
        return "Invalid selection", 400

if __name__ == '__main__':
    app.run(debug=True)
