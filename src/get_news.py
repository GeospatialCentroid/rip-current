"""
get_news.py
~~~~~~~~
Executes a request to retrieve news articles using GoogleNews api
"""

from GoogleNews import GoogleNews

def get_news(search_string, start_date, end_date, last_start_date, last_end_date):
    results=False
    googlenews = GoogleNews()

    googlenews.set_lang('en')
    #googlenews.set_period('7d')

    # make an exception for pulling the latest data since the last run
    if start_date =='last':
        print('starting at',last_start_date)
        googlenews.set_time_range(last_start_date, last_end_date)
    elif start_date and end_date:
        # also allow passing start and end dates
        googlenews.set_time_range(start_date,end_date)


    googlenews.set_encode('utf-8')
    googlenews.get_news(search_string)

    results = googlenews.results()
    return results
