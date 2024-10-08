from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import validators

app = Flask(__name__)

# Helper function to get all data from the website
def scrape_website_data(url):
    # Sends an HTTP GET request to the URL
    response = requests.get(url)
    
    # Parses the HTML content of the response
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract various elements from the parsed HTML
    data = {
        # Extracts image URLs from all <img> tags
        'images': [img.get('src') for img in soup.find_all('img') if img.get('src')],
        
        # Extracts href attributes from <a> tags where the href is a valid URL
        'links': [a.get('href') for a in soup.find_all('a', href=True) if validators.url(a.get('href'))],
        
        # Extracts the URL of favicon icons from <link> tags with rel='icon'
        'favicons': [link.get('href') for link in soup.find_all('link', rel='icon')],
        
        # Extracts the URL of CSS stylesheets from <link> tags with rel='stylesheet'
        'stylesheets': [link.get('href') for link in soup.find_all('link', rel='stylesheet')],
        
        # Extracts the source URLs of JavaScript files from <script> tags
        'scripts': [script.get('src') for script in soup.find_all('script') if script.get('src')],
        
        # Extracts text content from heading tags (h1-h6)
        'headings': {
            'h1': [h.text.strip() for h in soup.find_all('h1')],
            'h2': [h.text.strip() for h in soup.find_all('h2')],
            'h3': [h.text.strip() for h in soup.find_all('h3')],
            'h4': [h.text.strip() for h in soup.find_all('h4')],
            'h5': [h.text.strip() for h in soup.find_all('h5')],
            'h6': [h.text.strip() for h in soup.find_all('h6')]
        },
        
        # Extracts all <meta> tags and their attributes
        'meta_tags': [meta.attrs for meta in soup.find_all('meta')]
    }
    
    return data

# Function to search for a specific term in links and images
def search_in_data(data, search_term):
    # Filters links that contain the search term (case-insensitive)
    filtered_links = [link for link in data['links'] if search_term.lower() in link.lower()]
    
    # Filters images that contain the search term (case-insensitive)
    filtered_images = [img for img in data['images'] if search_term.lower() in img.lower()]
    
    return {
        'links': filtered_links,
        'images': filtered_images
    }

# Function to perform dynamic search using a search engine or a search bar on a specific website
def dynamic_search(base_url, search_term):
    # Constructs a search URL by appending the search term as a query parameter
    search_url = f"{base_url}?q={search_term.replace(' ', '+')}"
    
    # Sends a GET request to the search URL
    response = requests.get(search_url)

    if response.status_code == 200:
        # Parses the search results page
        soup = BeautifulSoup(response.content, 'html.parser')
        results = []

        # Finds search result items (assumes search results are in <li> tags with class 'search-results__item')
        for item in soup.find_all('li', class_='search-results__item'):
            title = item.find('h3')  # Extracts the title of the result
            link = item.find('a', href=True)  # Extracts the link to the result
            
            # Appends the title and link to the results if they exist
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
    # Renders the index.html template as the homepage
    return render_template('index.html')

# Route to scrape the website based on user input
@app.route('/scrape', methods=['POST'])
def scrape():
    # Gets the URL and user selection from the form submission
    url = request.form['url']
    selection = request.form.get('selection')
    search_term = request.form.get('search_term')

    # Scrapes the website data
    data = scrape_website_data(url)

    # Helper function to filter data based on the search term (case-insensitive)
    def filter_data(data_list, search_term):
        return [item for item in data_list if search_term.lower() in item.lower()]

    # Handles each selection case based on the user choice in the dropdown menu
    if selection == 'links':
        if search_term:
            filtered_links = filter_data(data['links'], search_term)
            return render_template('result.html', data={'links': filtered_links}, display_type='links', search_term=search_term)
        return render_template('result.html', data={'links': data['links']}, display_type='links', search_term=search_term)

    elif selection == 'images':
        if search_term:
            filtered_images = filter_data(data['images'], search_term)
            return render_template('result.html', data={'images': filtered_images}, display_type='images', search_term=search_term)
        return render_template('result.html', data={'images': data['images']}, display_type='images', search_term=search_term)

    elif selection == 'favicons':
        if search_term:
            filtered_favicons = filter_data(data['favicons'], search_term)
            return render_template('result.html', data={'favicons': filtered_favicons}, display_type='favicons', search_term=search_term)
        return render_template('result.html', data={'favicons': data['favicons']}, display_type='favicons', search_term=search_term)

    elif selection == 'stylesheets':
        if search_term:
            filtered_stylesheets = filter_data(data['stylesheets'], search_term)
            return render_template('result.html', data={'stylesheets': filtered_stylesheets}, display_type='stylesheets')
        return render_template('result.html', data={'stylesheets': data['stylesheets']}, display_type='stylesheets')

    elif selection == 'scripts':
        if search_term:
            filtered_scripts = filter_data(data['scripts'], search_term)
            return render_template('result.html', data={'scripts': filtered_scripts}, display_type='scripts')
        return render_template('result.html', data={'scripts': data['scripts']}, display_type='scripts')

    elif selection == 'headings':
        if search_term:
            # Filters headings across all heading levels
            filtered_headings = {
                level: filter_data(headings, search_term) for level, headings in data['headings'].items()
            }
            return render_template('result.html', data={'headings': filtered_headings}, display_type='headings')
        return render_template('result.html', data={'headings': data['headings']}, display_type='headings')

    elif selection == 'meta_tags':
        if search_term:
            # Meta tags are dictionaries, so convert them to strings for filtering
            filtered_meta_tags = [str(meta) for meta in data['meta_tags'] if search_term.lower() in str(meta).lower()]
            return render_template('result.html', data={'meta_tags': filtered_meta_tags}, display_type='meta_tags')
        return render_template('result.html', data={'meta_tags': data['meta_tags']}, display_type='meta_tags')

    elif selection == 'all':
        # If the user selected 'all', apply the search term to each field if provided
        if search_term:
            filtered_data = {
                'links': filter_data(data['links'], search_term),
                'images': filter_data(data['images'], search_term),
                'favicons': filter_data(data['favicons'], search_term),
                'stylesheets': filter_data(data['stylesheets'], search_term),
                'scripts': filter_data(data['scripts'], search_term),
                'headings': {
                    level: filter_data(headings, search_term) for level, headings in data['headings'].items()
                },
                'meta_tags': [str(meta) for meta in data['meta_tags'] if search_term.lower() in str(meta).lower()]
            }
            return render_template('result.html', data=filtered_data, display_type='all')
        return render_template('result.html', data=data, display_type='all')

    else:
        # Returns an error message if an invalid selection is made
        return "Invalid selection", 400

if __name__ == '__main__':
    # Runs the Flask application in debug mode
    app.run(debug=True)
