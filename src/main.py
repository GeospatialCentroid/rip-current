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

 For testing (no saving) - geolocation
  python -m src.main -f get_location -d "rip_current_articles.csv" - r 1
'''

import argparse
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'

from datetime import datetime, timedelta,date
import warnings
import re

warnings.simplefilter(action='ignore', category=FutureWarning)

from . import get_news
from . import read_news
from . import get_location
from . import upload_points
from . import create_vector_file

def main(args) -> None:
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

    if args.function == 'get_news' or args.function == 'all':
        # Fetch the articles
        # Look at the existing data to get the last run date
        last_start_date, last_end_date= None,None
        try:
            news_df['datetime'] = pd.to_datetime(news_df['datetime'], errors='coerce')
            last_start_date = news_df['datetime'].max().strftime('%m/%d/%Y')
            last_end_date=date.today().strftime('%m/%d/%Y')
        except Exception as e:
                pass
        # do multiple searches for each search term
        search_strings =  args.search_string.split(",")
        for s in search_strings:
            articles = pd.DataFrame(get_news.get_news(s, args.start_date, args.end_date,last_start_date, last_end_date))
            news_df=process_articles(news_df, articles, args.data)
    # Now decide what to do based on the function argument
    if args.function == 'read_news' or args.function == 'all':
        read_articles(news_df,args.data,args.row,args.questions,args.key,args.model,args.clean)
    if args.function == 'upload_points':
        upload_points.upload_points(news_df, args.data)
    if args.function == 'get_location':
        # for testing purposes
        # subset the list for points without lat
        for index, row in news_df[(news_df["lat"].isna()) & (news_df["lng"].isna() ) & (news_df["processed"] == 'y')].iterrows():
            check_location(row, news_df,args.key)
    if args.function == 'create_vector_file':
        create_vector_file.csv_to_point_vector(news_df[(news_df["lat"]!='') & (news_df["lng"]!='' ) & (news_df["processed"] == 'y')], "lat", "lng", args.output)




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

   # fix the date
    latest_news['datetime'] = latest_news['date'].apply(parse_date).dt.strftime('%m/%d/%Y')
    # add all the new articles
    all_data = pd.concat([archive, latest_news], ignore_index=True)
    # remove the duplicates
    all_data = all_data.drop_duplicates(subset=['title','desc','date'])  # Check for duplicates

    all_data = all_data.assign(OBJECTID=lambda x: range(len(x)))
    # get the new length
    len_after = len(all_data)
    # update the CSV file
    all_data.to_csv(output, index=False)

    print("New article(s) added:",len_after-len_before)
    return all_data


def read_articles(news_df,output,_row=None,_questions=None,_key=None,_model=None,_clean=None):
    """
    Worked through the selected news articles in the spreadsheet
    Opening, saving, reading, prompting and storing the relevant information

    :param news_df: the spreadsheet
    :param output: the name of the file to be saved
    :return:
    """

    if _row is None or _row == '':
        # populate a list of all the rows that haven't been processed
        rows=[]
        for index, row in news_df[news_df["processed"]!='y'].iterrows():
            rows.append(row)
    else:
        rows = [news_df.loc[_row]]

    print("About to update ",len(rows)," row(s)")
    for row in rows:
        reporter=str(row["reporter"]).replace("By "," ") # clean reporter name for file name
        file_name=str(row["title"])+"_"+str(row["media"])+"_"+reporter # create file name
        file_name=re.sub(r'[^a-zA-Z0-9\s]', '', file_name)# strip file name of special characters

        # determine if we're working with questions
        questions = False
        if _questions:
            questions = _questions

        # read the articles and get the answers to the prompt
        responses = read_news.read_news(row["link"], file_name + ".txt", questions,_model,_clean)

        if responses is not False:
            #populate the record columns based on the prompt responses
            for index, r in responses.iterrows():
                # now that the r["column name"] can have more that one value
                if  r["column name"]!=None and type(r["column name"]) is str:
                    cols = r["column name"].strip().split(",")
                    response = [r["response"]]
                    if len(cols)>1:
                        # also break up the response
                        response= r["response"].split(",")
                    # distribute the response over multiple columns if appropriate
                    for i, c in enumerate(cols):
                        if i < len(response):
                            news_df[c].loc[row["OBJECTID"]] = response[i].strip()

            # check for city, state and beach to geolocate
            check_location(news_df.loc[row["OBJECTID"]], news_df,_key)

            # calculate the drowning_datetime
            news_date = None
            # user either the 'datetime' or c
            if news_df.loc[row["OBJECTID"]]['datetime'] !='':
                news_date= parse_date_str(str(news_df.loc[row["OBJECTID"]]['datetime']))


            if news_date and news_df.loc[row["OBJECTID"]]['day'] !='':
                news_day = news_df.loc[row["OBJECTID"]]['day']
                drowning_datetime = get_previous_day(news_date,news_day)
                news_df["drowning_datetime"].loc[row["OBJECTID"]] = drowning_datetime.strftime('%m/%d/%Y')

            news_df["processed"].loc[row["OBJECTID"]] = 'y'
            # print(news_df.loc[row["OBJECTID"]])
            news_df.to_csv(output, index=False)
            # print("saved", output)
        else:
            print("Unable to open the article")

def parse_date_str(date_str):
    for fmt in ('%m/%d/%y', '%m/%d/%Y'):
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Date format not recognized: {date_str}")

def get_previous_day(current_date, target_day):
    days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    current_weekday = current_date.weekday()  # Monday=0

    target_weekday = None
    try:
        target_weekday = days_of_week.index(target_day)
    except Exception as e:
        return current_date

    if current_weekday == target_weekday:
        return current_date  # Same day, no change

    delta_days = (current_weekday - target_weekday + 7) % 7
    return current_date - timedelta(days=delta_days)

def check_location(row,news_df,key=None):
    """

    :param row: the row from the dataframe we want to work with
    :param news_df: whole news_df
    :param key: the API key for performing a google location search
    :return:
    """

    if isinstance(row["city"], str) and row["city"] != '' \
        and isinstance(row["state"], str) and row["state"] != '' \
        and isinstance(row["beach"], str) and row["beach"] != '':

        search_string=row["beach"] + ", " + row["city"] + ", " + row["state"]
        print("Searching for location of: "+search_string)
        if (key):
            location = get_location.get_location_google(search_string, key)
        else:
            location = get_location.get_location(search_string)
        print(location, "is the location")
        if location:
            news_df["lat"].loc[row["OBJECTID"]] = location["lat"]
            news_df["lng"].loc[row["OBJECTID"]] = location["lng"]
            if "WFO" in location:
                news_df["WFO"].loc[row["OBJECTID"]] = location["WFO"]
                news_df["distance_from_wfo"].loc[row["OBJECTID"]] = location["distance_from_wfo"]
            else:
                print("No WFO in ",location)

        else:
            print("no location found!")

def parse_date(date_str):
    date_str = date_str.strip()

    # Case 1: Matches "X days ago"
    match = re.match(r"(\d+)\s+days?\s+ago", date_str, re.IGNORECASE)
    if match:
        days_ago = int(match.group(1))
        return datetime.now() - timedelta(days=days_ago)

    # Case 2: Try parsing with year
    try:
        return datetime.strptime(date_str, '%b %d, %Y')
    except ValueError:
        pass

    # Case 3: Try parsing without year, assume current year
    try:
        current_year = datetime.now().year
        return datetime.strptime(f"{date_str}, {current_year}", '%b %d, %Y')
    except ValueError:
        return pd.NaT  # invalid date format

def parse_args():
    # Create an ArgumentParser object
    parser = argparse.ArgumentParser(description="")

    # Add arguments
    parser.add_argument("-d", "--data", type=str, help="The input data file")

    parser.add_argument("-q", "--questions", type=str, help="The questions to ask of the data")

    parser.add_argument("-f", "--function", type=str, help="function to call")

    parser.add_argument("-r", "--row", type=int, help="row to run")

    parser.add_argument("-k", "--key", help="key", type=str )

    parser.add_argument("-s", "--search_string", help="The string you'd like to use when searching Google News ", default='"rip current" OR "rip current drowning"', type=str )

    parser.add_argument("-start", "--start_date", help="The string format MM/DD/YYYY to determine the start date of the news search", type=str)

    parser.add_argument("-end", "--end_date", help="The string format MM/DD/YYYY to determine the end date of the news search", type=str )

    parser.add_argument("-m", "--model", type=str,
                        help="If using a different model than 'gemma3:1b'", )

    parser.add_argument("-c", "--clean",
                        help="Pass the AI responses through a cleaning function",action="store_true" )

    parser.add_argument("-o", "--output", type=str, help="The output vector data file")

    return parser.parse_args()

if __name__ == "__main__":

    main(parse_args())