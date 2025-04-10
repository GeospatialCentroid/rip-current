from newspaper import Article
from newspaper import Config

from time import sleep
from newspaper.article import ArticleException, ArticleDownloadState
import spacy
import ollama
import os

from googlenewsdecoder import gnewsdecoder

article_path="articles"


USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0'

config = Config()
config.browser_user_agent = USER_AGENT
config.request_timeout = 10

def read_news(_url, _file_name,author):

    '''

    :param _url:
    :param _file_name:
    :param author:
    :return:
    '''

    if not os.path.exists(article_path):
        os.makedirs(article_path)

    text =""
    # if we have already downloaded the article just use the existing download
    if os.path.exists(article_path + "/" + _file_name):
        file = open(article_path + "/" + _file_name, 'r')
        text = file.read()
    else:
        text = download_article(get_redirect_url(_url),_file_name)

    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)

    locations = [ent.text for ent in doc.ents if ent.label_ == "GPE"]
    print(locations,locations)

    person = [ee for ee in doc.ents if ee.label_ == 'PERSON']
    for p in person[:]:  # iterate over a copy to avoid index issues
        if str(p).strip() == author.strip():  # remove the author
            person.remove(p)

    print("person",person)



def get_redirect_url(url):
    try:
        decoded_url = gnewsdecoder(url, interval=1)

        if decoded_url.get("status"):
            return decoded_url["decoded_url"]
        else:
            print("Error:", decoded_url["message"])
    except Exception as e:
        print(f"Error occurred: {e}")

def download_article(url,_file_name):
    slept = 0

    article = Article(url, config=config)
    article.download()
    while article.download_state == ArticleDownloadState.NOT_STARTED:
        # Raise exception if article download state does not change after 10 seconds
        if slept > 9:
            raise ArticleException('Download never started')
        sleep(1)
        slept += 1

    article.parse()
    text = article.text

    # save a copy of the article
    if not os.path.exists(article_path + "/" + _file_name):
        f = open(article_path + "/" + _file_name, "a")
        f.write(text)
        f.close()

    return text
