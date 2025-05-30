import requests
import html2text
import os
import asyncio


url_section = "https://support.optisigns.com/api/v2/help_center/en-us/sections"
url_article = "https://support.optisigns.com/api/v2/help_center/en-us/sections/{section_id}/articles"
max_articles = 40

def fetch_all_sections():
    url = url_section
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        return []
    return response.json()

def get_all_sectionIds():
    sections = fetch_all_sections()
    items = sections['sections']
    sectionIds = []
    for item in items:
        sectionIds.append(item['id'])
    return sectionIds

def fetch_articles_from_section(section_id):
    url = url_article.format(section_id=section_id)
    params = {
        "sort_by": "position",
        "sort_order": "desc",
        "per_page": 100
    }

    articles = []
    while url:
        response = requests.get(url, params=params)
        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            break
        data = response.json()
        articles.extend(data.get("articles", []))
        url = data.get("next_page")  # phân trang

    return articles

def save_as_markdown(article):
    slug = article["title"].lower().replace(" ", "-").replace("/", "-")
    markdown = clean_html(article["body"])
    with open(f"articles/{slug}.md", "w", encoding="utf-8") as f:
        f.write(f"# {article['title']}\n\n")
        f.write(markdown)

def clean_html(html):
    return html2text.html2text(html)


def delete_all_file():
    for file in os.listdir("articles"):
        os.remove(f"articles/{file}")


def create_all_articles():
    delete_all_file()

    sectionIds = get_all_sectionIds()
    
    total_articles = 0
    for sectionId in sectionIds:
        if total_articles >= max_articles:
            break
            
        all_articles = fetch_articles_from_section(sectionId)
        for article in all_articles:
            if total_articles >= max_articles:
                break
            save_as_markdown(article)
            total_articles += 1
    print(f"Total articles: {total_articles}")
    
if __name__ == "__main__":

    create_all_articles()    
