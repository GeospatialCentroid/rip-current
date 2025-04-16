'''

Description: the following scripts handels

loading recent news article data

Populating a spreadsheet with results

pulling pertinent information out of the news articles

If called on its own
 python main.py -f process_articles -d "rip_current_articles.csv"

Or if just testing the loaded articles use:
python main.py -f read_articles -d "rip_current_articles.csv" -r 4
'''

import argparse
import pandas as pd
import warnings
import re

warnings.simplefilter(action='ignore', category=FutureWarning)

import get_news
import read_news

# Create an ArgumentParser object
parser = argparse.ArgumentParser(description="")

# Add arguments
parser.add_argument("-d","--data", type=str, help="The input data file")

parser.add_argument("-f","--function", type=str, help="function to call")

parser.add_argument("-r","--row", type=int, help="row to run")

# Parse arguments
args = parser.parse_args()

print(args.data)

def main():

    try:
        news_df = pd.read_csv(args.data)
    except:
        column_names = [
            'title',
            'desc',
            'date',
            'datetime',
            'link',
            'img',
            'media',
            'site',
            'reporter',
            'processed',
            'is_fatality',
            'deceased_name',
            'deceased_age',
            'date_of_occurrence'
        ]

        # Create an empty DataFrame with the specified column names
        news_df = pd.DataFrame(columns=column_names)

    if args.function == 'read_articles':
        read_articles(news_df,args.data)
    else:
        articles = pd.DataFrame(get_news.get_news())

        process_articles(news_df,articles,args.data)



def process_articles(archive,latest_news,output):
    #
    len_before = len(archive)
    all_data = pd.concat([archive, latest_news], ignore_index=True)

    all_data = all_data.drop_duplicates(subset=['title','reporter','date'])  # Check for duplicates
    len_after = len(all_data)

    all_data.to_csv(output, index=False)
    print("saved", output, "Articles added:",len_after-len_before)


def read_articles(news_df,output):

    # print(news_df.iloc[0]["link"])
    row =news_df.iloc[args.row]
    reporter=str(row["reporter"]).replace("By "," ")
    file_name=row["title"]+"_"+row["media"]+"_"+reporter
    file_name=re.sub(r'[^a-zA-Z0-9\s]', '', file_name)
    read_news.read_news(row["link"], file_name+".txt",reporter)

    news_df["processed"].iloc[args.row] = 'y'
    news_df.to_csv(output, index=False)
    print("saved", output)

if __name__ == "__main__":
    main()