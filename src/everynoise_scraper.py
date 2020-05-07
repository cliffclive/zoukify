import os, json, re, requests
from bs4 import BeautifulSoup

def scrape_all_links(domain, path, target_pattern):
    """
    Scrapes a website and compiles a list of urls that match a target pattern.
    
    Inputs: 
    - domain: domain of the website you want to scrape
    - path: path to the page that you want to scrape from `domain`
    - target_pattern: regex that specifies the types of links you want to collect
    
    Outputs:
    - target_urls: list of all the links on domain/path that match target_pattern
    """
    main_page = '/'.join(['http:/', domain, path])
    response = requests.get(main_page)

    if response.status_code != 200:
        raise ConnectionError(f"Failed to connect to {main_page}.")

    soup = BeautifulSoup(response.text, "html.parser")

    target_regex = re.compile(target_pattern)
    target_urls = ['/'.join(['http:/', domain, x['href']])
                    for x in soup.find_all('a', {'href':target_regex})]

    return target_urls

def scrape_links_from_each_page(urls, target_pattern, labeler=(lambda x:x)):
    """
    Loops over a list of urls and finds links that matches a target pattern from each page.
    
    Inputs:
    - urls: the list of urls to scrape links from
    - target_pattern: regex that specifies the types of links you want to collect
    - labeler: function that parses a url and returns a label for that page
    
    Outputs:
    - links: a dictionary with key/value pairs {url_label:[scraped_links]}
    """
    links = {}

    for url in urls:
        response = requests.get(url)
        label = labeler(url)

        if response.status_code != 200:
            raise ConnectionError(f"Failed to connect to {url}.")

        soup = BeautifulSoup(response.text, "html.parser")

        target_regex = re.compile(target_pattern)
        target_urls = [x['href'] for x in soup.find_all('a', {'href':target_regex})]

        links[label] = target_urls
    
    return links

def scrape_everynoise_genre_playlists(filepath='everynoise_genre_playlists.json'):
    print("Scraping genres from Every Noise At Once...")
    genre_urls = scrape_all_links(
        domain='everynoise.com', 
        path='engenremap.html', 
        target_pattern='engenremap-[a-z]*')

    print(f"Found {len(genre_urls)} genres.")
    print("Scraping Spotify playlist links...")

    genre_playlists = scrape_links_from_each_page(
        urls=genre_urls,
        labeler=(lambda url: url.split('/')[-1].split('-')[-1].split('.')[0]),
        target_pattern='open.spotify.com')

    with open(filepath, 'w') as outfile:
        json.dump(genre_playlists, outfile)


if __name__ == "__main__":
    scrape_everynoise_genre_playlists('everynoise_genre_playlists.json')
