



import time
from ollama import chat
from ollama import Client
import os
import pandas as pd
from googlenewsdecoder import gnewsdecoder

import requests
from bs4 import BeautifulSoup
import json

article_path= "articles"



def read_news(_url, _file_name,question_file,model='gemma3:1b',clean=None):
    """

    :param _url:
    :param _file_name:
    :param author:
    :param questions:
    :return:
    """
    if model== None:
        model = 'gemma3:1b'

    if not os.path.exists(article_path):
        os.makedirs(article_path)

    # print("URL:",_url)
    # if we have already downloaded the article just use the existing download
    if os.path.exists(article_path + "/" + _file_name):
        print("opening the previously downloaded article",article_path + "/" + _file_name)
        file = open(article_path + "/" + _file_name, 'r')
        text = file.read()
    else:
        if "https://news.google.com" in _url:
            _url = get_redirect_url(_url)

        text = download_article(_url,_file_name)

        if text =='' or text == None:
            return False

    # begin the LLM chat message list
    messages = [
        {
            'role': 'user',
            'content': 'Here is the article text I\'m working with "' + text + '"',
        }, ]
    # load the questions
    if question_file==False:
        setup_llm_chat(_file_name, messages,model,clean)
    else:
        return setup_llm_client(pd.read_csv(question_file),messages,model,clean)

def setup_llm_client(questions,messages,model,clean):
    """

    :param questions:
    :param text:
    :return:
    """

    # start by adding a temporary column to store the responses
    questions["response"]=''

    for index, row in questions.iterrows():
        # combine the question parts pre	question	post	options
        question = str(row['pre']) + " " + str(row['question']) + " " + str(row['post']) + " " + str(row['options'])
        messages.append({'role': 'user', 'content': question})
        # capture the message response
        response = chat(model,messages=[*messages, {'role': 'user', 'content': question}],)

        # Add the response to the messages to maintain the history
        messages += [
            {'role': 'user', 'content': question},
            {'role': 'assistant', 'content': response.message.content},
        ]
        # save the message response
        # first remove any weird characters
        questions["response"].iloc[index] = clean_response(response.message.content,clean)
        print(question,":",clean_response(response.message.content,clean))
    # pass the question dataframe back with responses
    return questions

def clean_response(str,clean):
    if clean:
        str = str.replace('’', "'")
        if str.find("</think>") > -1:
            str = str.splitlines()[-1]

    return str


def setup_llm_chat(_file_name,messages, model,clean):
    """
    A function for testing the llm
    :param _file_name:
    :param text:
    :return:
    """
    print("The article name is " + _file_name)
    while True:
        user_input = input("What would you like to know about this article: ")
        if user_input.lower() == 'exit':
            break
        response = chat(
            model,
            messages=messages
                     + [
                         {'role': 'user', 'content': user_input},
                     ],
        )

        # Add the response to the messages to maintain the history
        messages += [
            {'role': 'user', 'content': user_input},
            {'role': 'assistant', 'content': response.message.content},
        ]
        print(clean_response(response.message.content,clean) + '\n')


def get_redirect_url(url):
    try:
        decoded_url = gnewsdecoder(url, interval=1)

        if decoded_url.get("status"):
            return decoded_url["decoded_url"]
        else:
            print("Error:", decoded_url["message"])
    except Exception as e:
        print(f"Error occurred: {e}")

def download_article(url,_file_name, max_retries=3, initial_delay=2):


    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' 
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/115.0.0.0 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9'
    }

    delay = initial_delay

    for attempt in range(1, max_retries + 1):
        try:
            print(f"Attempt {attempt} to download: {url}")
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            # Extract visible text
            text = extract_clean_article_text(response.content)
            # save a copy of the article
            if not os.path.exists(article_path + "/" + _file_name):
                print("saving",article_path + "/" + _file_name)
                f = open(article_path + "/" + _file_name, "a")
                f.write(str(text))
                f.close()

            return str(text)

        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt} failed: {e}")
            if attempt < max_retries:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
                delay *= 2  # Exponential backoff
            else:
                print("All attempts failed.")
                return None

# Reference https://chatgpt.com/share/6877ceba-a8e8-8004-b08e-abb98602cb09
def extract_clean_article_text(content):
    soup = BeautifulSoup(content, 'html.parser')
    output = []


    # Extract author from application/ld+json schema.org metadata
    author_extracted = None
    ld_json_tags = soup.find_all('script', type='application/ld+json')
    for tag in ld_json_tags:
        try:
            data = json.loads(tag.string)
            if isinstance(data, list):
                for entry in data:
                    author_name = extract_author_name_from_json(entry)
                    if author_name:
                        author_extracted = author_name
                        break
            else:
                author_name = extract_author_name_from_json(data)
                if author_name:
                    author_extracted = author_name
                    break
        except (json.JSONDecodeError, TypeError):
            continue

    # Add author line if extracted
    if author_extracted:
        output.append(f"By {author_extracted}\n")

        # Remove unwanted elements
        for tag in soup(['script', 'style', 'nav', 'footer', 'aside']):
            tag.decompose()

        for div in soup.find_all(['div', 'section'], class_=lambda x: x and any(
                c in x.lower() for c in ['ad', 'advert', 'sponsored', 'footer', 'nav'])):
            div.decompose()

        # Extract title
        h1 = soup.find('h1')
        if h1:
            output.append(f"\nTitle: {h1.get_text(strip=True)}\n")
        else:
            page_title = soup.title.string if soup.title else "No Title Found"
            output.append(f"\nTitle: {page_title.strip()}\n")

        # Extract publish date
        time_tag = soup.find('time')
        if time_tag:
            output.append(f"Published: {time_tag.get_text(strip=True)}\n")
        else:
            meta_time = soup.find('meta', attrs={'property': 'article:published_time'})
            if meta_time and meta_time.has_attr('content'):
                output.append(f"Published: {meta_time['content']}\n")

    # Determine main content area
    content_area = soup.find('main') or soup.find('article') or soup.body
    if content_area is None:
        return "\n".join(output)

    # Extract text content
    for tag in content_area.find_all(['h1', 'h2', 'h3', 'p', 'ul', 'ol', 'li'], recursive=True):
        text = tag.get_text(strip=True)
        if not text:
            continue

        if tag.name in ['h1', 'h2', 'h3']:
            output.append(f"\n{text}\n")

        elif tag.name == 'p':
            output.append(text + "\n")

        elif tag.name in ['ul', 'ol']:
            classes = tag.get('class') or []
            # Skip byline list if author already extracted
            if author_extracted and 'article-byline' in [c.lower() for c in classes]:
                continue
            for li in tag.find_all('li', recursive=False):
                li_text = li.get_text(strip=True)
                output.append(f"- {li_text}")
            output.append("\n")

        elif tag.name == 'li':
            parent = tag.find_parent(['ul', 'ol'])
            if parent is None:
                output.append(f"- {text}\n")

    return "\n".join(output).strip()


def extract_author_name_from_json(data):
    """
    Helper to extract author name string from JSON-LD data
    """
    if isinstance(data, dict) and data.get('@type') == 'NewsArticle':
        authors = data.get('author')
        if not authors:
            return None
        if isinstance(authors, dict):
            authors = [authors]

        for author in authors:
            if isinstance(author, dict):
                name = author.get('name', '').strip()
                if name:
                    return name
    return None