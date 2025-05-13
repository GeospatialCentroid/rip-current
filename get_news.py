from GoogleNews import GoogleNews

def get_news():

    googlenews = GoogleNews()

    googlenews.set_lang('en')
    #googlenews.set_period('7d')
    # googlenews.set_time_range('02/01/2020','02/28/2020')
    googlenews.set_encode('utf-8')

    googlenews.get_news('rip current, rip current drowning, rip currents, sneaker waves, sneaker wave drowning')

    # googlenews.total_count() not working
    results = googlenews.results()
    return results
