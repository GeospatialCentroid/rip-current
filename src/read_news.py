



from newspaper import Article
from newspaper import Config

from time import sleep
from newspaper.article import ArticleException, ArticleDownloadState
from ollama import chat
from ollama import Client
import os
import pandas as pd
from googlenewsdecoder import gnewsdecoder

article_path= "../articles"


USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0'

config = Config()
config.browser_user_agent = USER_AGENT
config.request_timeout = 10

def read_news(_url, _file_name,question_file,model='gemma3:1b'):
    """

    :param _url:
    :param _file_name:
    :param author:
    :param questions:
    :return:
    """

    if not os.path.exists(article_path):
        os.makedirs(article_path)

    # print("URL:",_url)
    # if we have already downloaded the article just use the existing download
    if os.path.exists(article_path + "/" + _file_name):
        file = open(article_path + "/" + _file_name, 'r')
        text = file.read()
    else:
        if "https://news.google.com" in _url:
            _url = get_redirect_url(_url)

        text = download_article(_url,_file_name)
        if text =='':
            return False

        # begin the LLM chat message list
    messages = [
        {
            'role': 'user',
            'content': 'Here is the article text I\'m working with "' + text + '"',
        }, ]
    # load the questions
    if question_file==False:
        setup_llm_chat(_file_name, text, messages,model)
    else:
        return setup_llm_client(pd.read_csv(question_file),text,messages,model)

def setup_llm_client(questions,text,messages,model='gemma3:1b'):
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
        questions["response"].iloc[index]=response.message.content.replace('’',"'")
        print(question,":",response.message.content)
    # pass the question dataframe back with responses
    return questions

def setup_llm_chat(_file_name,text,messages, model):
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
        print(response.message.content + '\n')


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
    try:
        article.parse()
        text = article.text

        # save a copy of the article
        if not os.path.exists(article_path + "/" + _file_name):
            f = open(article_path + "/" + _file_name, "a")
            f.write(text)
            f.close()
    except Exception as e:
            print(e)
            return ''

    return text

def chat_with_ollama(model_name, prompt):
    response = ollama.chat(model=model_name, messages=[{'role': 'user', 'content': prompt}])
    return response['message']['content']