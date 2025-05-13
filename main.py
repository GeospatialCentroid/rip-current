'''

Description: the following scripts handels

loading recent news article data

Populating a spreadsheet with results

pulling pertinent information out of the news articles

If called on its own
 python main.py -f process_articles -d "rip_current_articles.csv"

Or if just testing the loaded articles use:
python main.py -f read_articles -d "rip_current_articles.csv" -r 4 -q "questions.csv"
'''

import argparse
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'


import warnings
import re

warnings.simplefilter(action='ignore', category=FutureWarning)

import get_news
import read_news
import get_location

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

def main():

    try:
        news_df = pd.read_csv(args.data, encoding='cp1252')
    except Exception as e:
        print("creating new CSV",args.data)
        # this is the first time we're running this
        # setup the a new spreadsheet with all the needed columns
        column_names=[]
        with open("column_names.txt", 'r') as file:
            for line in file:
                column_names.append(line.rstrip('\n'))
        print(column_names)
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
    row =news_df.iloc[args.row-2] # get reference to the row and subtract two, to account for zero based indexing and the header column

    reporter=str(row["reporter"]).replace("By "," ")
    file_name=row["title"]+"_"+str(row["media"])+"_"+reporter
    file_name=re.sub(r'[^a-zA-Z0-9\s]', '', file_name)# strip file name of special characters
    questions = False
    if args.questions:
        questions = args.questions

    responses = read_news.read_news(row["link"], file_name+".txt",reporter,questions)
    for index, r in responses.iterrows():
        news_df[r["column name"].strip()].iloc[args.row] = r["response"]

    # check for city	state	beach
    if isinstance(row["city"], str) and row["city"]!='' \
            and isinstance(row["state"], str) and row["state"]!='' \
            and isinstance(row["beach"], str) and row["beach"]!='':
        location = get_location.get_location(row["city"]+","+row["state"]+","+row["beach"])
        print(location, "is the location")
    else:
        print("no location found!")

    news_df["processed"].iloc[args.row] = 'y'
    news_df.to_csv(output, index=False)
    print("saved", output)

if __name__ == "__main__":
    main()