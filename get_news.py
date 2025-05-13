from GoogleNews import GoogleNews
import pandas as pd
def get_news():
    results=False
    googlenews = GoogleNews()

    googlenews.set_lang('en')
    #googlenews.set_period('7d')
    #googlenews.set_time_range('02/01/2020','02/28/2020')
    googlenews.set_encode('utf-8')
    googlenews.get_news('"rip current" OR "rip current drowning"')
    # googlenews.search('rip current, rip current drowning, rip currents, sneaker waves, sneaker wave drowning')

    # googlenews.search('"rip current" OR "rip current drowning"')
    #
    # all_data = pd.DataFrame(googlenews.result())
    #
    # print("All article start length: ", len(all_data))
    # # googlenews.total_count() not working
    # # ref: https://medium.com/analytics-vidhya/googlenews-api-live-news-from-google-news-using-python-b50272f0a8f0
    # for i in range(2, 4):
    #     googlenews.getpage(i)
    #     all_data = pd.concat([all_data, pd.DataFrame(googlenews.result())], ignore_index=True)
    #
    # all_data = all_data.drop_duplicates(subset=['title', 'desc', 'date'])  # Check for duplicates
    # print("After duplicate drop length: ", len(all_data))
    # return all_data
    results = googlenews.results()
    return results
