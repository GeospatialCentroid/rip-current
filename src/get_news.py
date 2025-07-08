"""
get_news.py
~~~~~~~~
Executes a request to retrieve news articles using GoogleNews api
"""

from GoogleNews import GoogleNews

def get_news(search_string, start_date, end_date):
    results=False
    googlenews = GoogleNews()

    googlenews.set_lang('en')
    #googlenews.set_period('7d')
    if start_date and end_date:
        googlenews.set_time_range(start_date,end_date)
    googlenews.set_encode('utf-8')
    googlenews.get_news(search_string)

    results = googlenews.results()
    return results
