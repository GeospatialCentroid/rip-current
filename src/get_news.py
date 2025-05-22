"""
get_news.py
~~~~~~~~
Executes a request to retrieve news articles using GoogleNews api
"""

from GoogleNews import GoogleNews

def get_news():
    results=False
    googlenews = GoogleNews()

    googlenews.set_lang('en')
    #googlenews.set_period('7d')
    #googlenews.set_time_range('02/01/2020','02/28/2020')
    googlenews.set_encode('utf-8')
    googlenews.get_news('"rip current" OR "rip current drowning"')

    results = googlenews.results()
    return results
