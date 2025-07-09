## Rip Current

---

## 1 Project Purpose

The documented number of fatalities that have occurred as a result of drownings related to rip currents is not consistent. 
In an effort to better quantify the annual number of these drownings, this project uses news articles and AI to gather details from Google News.
Each article is prompted with series of questions used to populate a spreadsheet.
The location information gathered (Beach, City, State) are geolocated and then used to identify the closest Weather Forecast Office (WFO).
These geolocated points are then uploaded to an ArcGIS Online Feature Service for public access.

---

## 2 Directory layout

```
project‑root/
│
├── articles/             ← Stores a local copy of news article text. 
│                           Articles are saved using the format {title}+{media outlet}+_+reporter
├── locations/
│   └── w_10se24.zip      ← A zipped shape file with the Weather Forecast Office (WFO) polygons

├── src/
│   ├── get_location.py   ← Geolocation and WFO identifyer
│   ├── get_news.py       ← Google News accesser
│   ├── main.py           ← Command‑line driver
│   ├── read_news.py      ← News article reader using AI and offline‑article manager
│   └── upload_points.py  ← Uploader of unique points to ArcGIS Online Feature Service
│
├── column_names.txt      ← The header columns
├── questions.csv         ← The questions used to prompt each news article
└── rip_current_articles.csv      ← Example file output, this one has old data appended (path is user‑selectable).
```

---

## 3 Setup
A Large Language Model (LLM) is used to extract information from news articles. 
Ollama is the application used for running LLMs, and we're currently using the **gemma3:1b** LLM.

### Installing Ollama and the LLM
First download and install Ollama: https://ollama.com/download/

Then from the command line, run: 
```bash
ollama pull gemma3:1b
```

#### Using other LLMs
There are many LLM options to choose from and other LLMs may be useful. If you'd like to use another LLM, 
please first check if it's Ollama compatible by going to https://ollama.com/library. 
With the LLM of your choosing, get the model name you desire by navigating to the details page. The run:
```bash
ollama pull {model_name}
```
replacing ```{model_name}``` with the model name


### Downloading and setting-up the project
    
1. Clone this repository, and direct your terminal window to the local project folder 
2. Create a virtual environment to install all the required libraries. 
   *Note python version 3.12 has been used for stability. You can download/install this version  from https://www.python.org/downloads/*
   
    ```python3.12 -m venv venv```
3. Activate virtual environment
    ```source venv/bin/activate```
or on Windows: 
    ```.\venv\scripts\Activate.ps1 ``` or ```.\venv\scripts\Activate.ps1 ```
   
You should see (venv) at the beginning of your Terminal line indicating the virtual environment is activated.

4. Install the required libraries into your virtual environment
```pip install -r requirements.txt```
   
*Note: If you add any new python packages, be sure to run*
```pip freeze > requirements.txt``` 
to update the requirements file.

---
## 4 Running the application
*Note: Your virtual environment must be activated, before running the application.*

### Setting-up the article spreadsheet
The application first needs news articles to read from. Call:
```base
python -m src.main -f get_news -d  "{name of data file}"
```
Replacing {name of data file} with the csv file you'd like to save articles to.

Optional ```-s {search string}```
The default search string is '"rip current" OR "rip current drowning"' 
though many more search terms have been used in the past to find articles from drownings resulting from rip currents.
These terms are as follows:
'rip current, rip current drowning, rip currents, sneaker waves, sneaker wave drowning'
Running the ```get_news``` script could be called multiple times with different search terms to help increase the pool of search results.

Optional ```-start {MM/DD/YYYY} -end {MM/DD/YYYY}```
Though a check is done on retrieved news articles to remove duplicates, it may be beneficial to constrain the date range of articles.



Putting it all together a search for news articles could be:
```base
python -m src.main -f get_news -d  output.csv -s 'rip current drowning' -start '06/01/2025' -end '06/06/2025'
```

## 5 Article information population
When ```get_news``` is called for the first time the 'column_names.txt' files is used to set up the spreadsheet columns.
Each line in the 'column_names.txt' file represents a new column.

The columns in the spreadsheet are as follows:

* index
* link: The URL of the source article
* drowning: Y or N – All articles that are asked additional questions of will have a ‘Y’
* cause of drowning: "Rip Current", "High Surf", "Sneaker Wave", "Other" or "Unknown"
* city
* state
* beach
* gender: M or F
* age: Number
* month
* day
* year
* time of occurrence: AM or PM
* resident or tourist
* lat
* lng
* WFO

*Note: new columns can be added (or deleted) as needed, 
just be sure the columns that are to be populated via the LLM prompts exist.*

### Reading articles from the spreadsheet

Once you have a list of articles (see Setting-up the article spreadsheet above), you can read them to start populating additional column information into the spreadsheet.
call:
```
python -m src.main -f read_news -d "{name of data file}" -r {row_number} -q {question file} -k {google_maps_api_key} -m {model_name} -c
```

Replacing:
- {name of data file}: with the csv file you saved your articles to earlier.
- {row_number}: with the index number you'd like to read. Omit this to prompt all news articles in the spreadsheet that have not been 'processed'.
- {question file}: with a csv file containing prompts (*see Article information extraction* below for thee details of this file).
    Without passing a question file, a chatbot is enabled to allow you to ask questions of the article. 
    This is useful during the testing of new prompts to be added the question bank.
- {google_maps_api_key}: To use the Google Maps API to geolocation the beach from the article. This key can be obtained at https://developers.google.com/maps/documentation/javascript/get-api-key. For test purposes, the following key can be used 
  *AIzaSyCdnWn8Kanu6NMDvQNggPC_rjYJfdWL_ko*. Omitting this key will default the geolocation search to use OpenStreetMaps, which isn't as useful.

 - {model_name}: If you've downloaded a different LLM model and want to test it out, please replace '{model_name}' with its name
 -c (optional): If you want to clean the AI response (ie. exclude '</think>' from deep-seek and '`' from gemma. mit to see the full response

Putting it all together 'reading' a news article could be performed by calling:
```base
python -m src.main -f read_news -d  output.csv -q questions.csv -k AIzaSyCdnWn8Kanu6NMDvQNggPC_rjYJfdWL_ko -r 15 -m deepseek-r1:1.5b
```

## 6 Article Information Extraction
The program extracts information from articles by prompting a LLM with questions.
Each question is linked to a column in the {name of data file} spreadsheet. 
Questions are stored in the {question file} file using the column structure:
* pre: start of question to add context
* question: actual question
* post: how you'd like your response structured
* options: the choices for the response
* column name: the column to be populated in the rip_current_articles.csv spreadsheet

## 7 Uploading New Points
A feature service can be used to share information with the public. 
This feature service will need to be created in ArcGIS Online.
Edit permissions to this feature service should be restricted. 
To gain authentication to the feature service, a .env file should be created and saved with the text below, 
replacing the {} variables as appropriate:
```
AGOL_URL={https://your-org.maps.arcgis.com}
AGOL_USERNAME={your.username}
AGOL_PASSWORD={your.password}
FEATURE_SERVICE_ITEMID={abcdef1234567890abcdef1234567890}
XY_DECIMALS=6      # precision for rounding X,Y coordinates

```
*Note:* Only articles that have both lat and lng values, 
plus, an 'approved' value of 'y' and a value for the 'approved_by' column will be added to the feature service.

To Add new points to the feature service, call:
```bash
python -m src.main -f upload_points -d "{name of data file}"
```