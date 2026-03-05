"""
get_news.py
~~~~~~~~
Executes a request to retrieve news articles using GoogleNews api
"""

#from GoogleNews import GoogleNews
from pygooglenews import GoogleNews
import pandas as pd


def get_news(search_string, start_date, end_date, last_start_date, last_end_date):
    results=False
    googlenews = GoogleNews(lang = 'en')

    #googlenews.set_lang('en')
    #googlenews.set_period('7d')

    # make an exception for pulling the latest data since the last run
    _from = None
    _to = None
    if start_date =='last' and last_start_date:
        print('starting at',last_start_date)
        _from= last_start_date
        _to= last_end_date
    elif start_date and end_date:
        # also allow passing start and end dates
       _from = start_date
       _to = end_date


    print("searching for news with",search_string)

    s = googlenews.search(search_string, helper = True, when = None, from_ = _from, to_ = _to, proxies=None, scraping_bee=None)

    results = pd.DataFrame(s['entries'])
    results= results.rename(columns={"published": "date", "source": "media"})


    results['media'] = results['media'].str['title']
    results = results.drop(columns=['summary','summary_detail','title_detail','links','sub_articles','published_parsed','guidislink','id'])

    first_row_series = results.iloc[0]

    
    for column_name, value in first_row_series.items():
        print(f"{column_name}: {value}")

    
    return results
