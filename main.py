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
import upload_points

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
        news_df = pd.read_csv(args.data, encoding='utf8', skip_blank_lines=True)
        news_df.dropna(how='all', inplace=True)
        print("Number of valid rows in file :",len(news_df))
    except Exception as e:
        print(e)
        print("creating new CSV",args.data)
        # this is the first time we're running this
        # setup the a new spreadsheet with all the needed columns
        column_names=[]
        with open("column_names.txt", 'r') as file:
            for line in file:
                column_names.append(line.rstrip('\n'))
        # Create an empty DataFrame with the specified column names
        news_df = pd.DataFrame(columns=column_names)

    if args.function == 'read_articles':
        read_articles(news_df,args.data)
    if args.function == 'upload_points':
        upload_points.upload_points(news_df, args.data)

    else:
        articles = pd.DataFrame(get_news.get_news())

        process_articles(news_df,articles,args.data)



def process_articles(archive,latest_news,output):
    #
    len_before = len(archive)
    all_data = pd.concat([archive, latest_news], ignore_index=True)

    all_data = all_data.drop_duplicates(subset=['title','desc','date'])  # Check for duplicates
    len_after = len(all_data)

    all_data.to_csv(output, index=False)
    print("saved", output, "Articles added:",len_after-len_before)


def read_articles(news_df,output):
    if 'index' not in news_df.columns:
        news_df.insert(0, 'index', range(0, len(news_df) )) # force an index to keep track

    if not args.row:
        # populate a list of all the rows that haven't been processed
        rows=[]
        for index, row in news_df[news_df["processed"]!='y'].iterrows():
            rows.append(row)
    else:
        rows = [news_df.iloc[
            args.row - 2] ] # get reference to the row and subtract two, to account for zero based indexing and the header column

    print("About to update ",len(rows)," rows")
    for row in rows:
        reporter=str(row["reporter"]).replace("By "," ") # clean reporter name for file name
        file_name=str(row["title"])+"_"+str(row["media"])+"_"+reporter # create file name
        file_name=re.sub(r'[^a-zA-Z0-9\s]', '', file_name)# strip file name of special characters

        # determine if we're working with questions
        questions = False
        if args.questions:
            questions = args.questions

        # read the articles and get the answers to the prompt
        responses = read_news.read_news(row["link"], file_name+".txt",reporter,questions)

        if responses is not False:
            #populate the record columns based on the prompt responses
            for index, r in responses.iterrows():
                news_df[r["column name"].strip()].iloc[row["index"]] = r["response"]

            # check for city, state and beach to geolocate
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
        else:
            print("Unable to open the article")

if __name__ == "__main__":
    main()