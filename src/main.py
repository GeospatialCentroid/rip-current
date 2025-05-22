'''

Description: the following script is the main command-line driver for:

├── get_location.py   ← Geolocation and WFO identifyer
├── get_news.py       ← Google News accesser
├── read_news.py      ← News article reader using AI and offline‑article manager
├── upload_points.py  ← Uploader of unique points to ArcGIS Online Feature Service

The likely sequence of calls through this script are

 python -m src.main -f get_news -d "rip_current_articles.csv"

 python -m src.main -f read_articles -d "rip_current_articles.csv" -r 1 -q questions.csv

 python -m src.main -f upload_points -d "rip_current_articles.csv"
'''

import argparse
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'


import warnings
import re

warnings.simplefilter(action='ignore', category=FutureWarning)

from . import get_news
from . import read_news
from . import get_location
from . import upload_points

# Create an ArgumentParser object
parser = argparse.ArgumentParser(description="")

# Add arguments
parser.add_argument("-d","--data", type=str, help="The input data file")

parser.add_argument("-q","--questions", type=str, help="The questions to ask of the data")

parser.add_argument("-f","--function", type=str, help="function to call")

parser.add_argument("-r","--row", type=int, help="row to run")

# Parse arguments
args = parser.parse_args()

print(args.data)

def main() -> None:
    """
    The main entry point to for the program
    :return:
    """

    try:
        # Tries to open the CSV files specified
        news_df = pd.read_csv(args.data, encoding='utf8', skip_blank_lines=True)
        news_df.dropna(how='all', inplace=True)
        print("Number of valid rows in file :",len(news_df))
    except Exception as e:
        # If the CSV file can't be opened, create a new one
        print(e)
        print("creating new CSV",args.data)

        # Setup the a new spreadsheet with all the needed columns
        column_names=[]
        with open("column_names.txt", 'r') as file:
            for line in file:
                column_names.append(line.rstrip('\n'))

        # Create the empty DataFrame with the specified column names
        news_df = pd.DataFrame(columns=column_names)

    # Now decide what to do based on the function argument
    if args.function == 'read_articles':
        read_articles(news_df,args.data)
    if args.function == 'upload_points':
        upload_points.upload_points(news_df, args.data)
    else:
        # Fetch the articles
        articles = pd.DataFrame(get_news.get_news())
        process_articles(news_df,articles,args.data)



def process_articles(archive,latest_news,output):
    """
    The following takes news articles found and checks them against articles we already have in the spreadsheet

    :param archive:
    :param latest_news:
    :param output:
    :return:
    """
    # Check the length of articles we have
    len_before = len(archive)
    # add all the new articles
    all_data = pd.concat([archive, latest_news], ignore_index=True)
    # remove the duplicates
    all_data = all_data.drop_duplicates(subset=['title','desc','date'])  # Check for duplicates
    # get the new length
    len_after = len(all_data)
    # update the CSV file
    all_data.to_csv(output, index=False)
    print("New article(s) added:",len_after-len_before)


def read_articles(news_df,output):
    """
    Worked through the selected news articles in the spreadsheet
    Opening, saving, reading, prompting and storing the relevant information

    :param news_df: the spreadshee
    :param output: the name of the file to be saved
    :return:
    """
    if 'index' not in news_df.columns:
        news_df.insert(0, 'index', range(0, len(news_df) )) # force an index to keep track

    if not args.row:
        # populate a list of all the rows that haven't been processed
        rows=[]
        for index, row in news_df[news_df["processed"]!='y'].iterrows():
            rows.append(row)
    else:
        rows = [news_df.loc[args.row]]

    print("About to update ",len(rows)," row(s)")
    for row in rows:
        reporter=str(row["reporter"]).replace("By "," ") # clean reporter name for file name
        file_name=str(row["title"])+"_"+str(row["media"])+"_"+reporter # create file name
        file_name=re.sub(r'[^a-zA-Z0-9\s]', '', file_name)# strip file name of special characters

        # determine if we're working with questions
        questions = False
        if args.questions:
            questions = args.questions

        # read the articles and get the answers to the prompt
        responses = read_news.read_news(row["link"], file_name + ".txt", reporter, questions)

        if responses is not False:
            #populate the record columns based on the prompt responses
            for index, r in responses.iterrows():
                news_df[r["column name"].strip()].loc[row["index"]] = r["response"]

            # check for city, state and beach to geolocate
            if isinstance(row["city"], str) and row["city"]!='' \
                    and isinstance(row["state"], str) and row["state"]!='' \
                    and isinstance(row["beach"], str) and row["beach"]!='':
                location = get_location.get_location( row["beach"]+ ", " + row["city"] + ", " + row["state"])
                print(location, "is the location")
                if location:
                    news_df[r["lat"].strip()].loc[row["index"]] = location["lat"]
                    news_df[r["lng"].strip()].loc[row["index"]] = location["lng"]
                    #
                    location["geo"]
            else:
                print("no location found!")

                news_df["processed"].loc[row["index"]] = 'y'
            news_df.to_csv(output, index=False)
            print("saved", output)
        else:
            print("Unable to open the article")

if __name__ == "__main__":
    main()