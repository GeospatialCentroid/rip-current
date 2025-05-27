## Rip Current

---

## 1 Project Purpose

The documented number of fatalities that have occurred as a result of drownings related to rib currents is not consistent. 
In an effort to better quantify the annual number of these drownings, this project uses news articles and AI to gather details from Google News.
Each article is prompted with series of questions used to populate a spreadsheet.
The location information gathered (Beach, City, State) are geolocated and then used to identify the closest  Weather Forecast Office (WFO).
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
└── rip_current_articles.csv      ← Example final output (path is user‑selectable).
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

### Downloading and setting-up the project
    
1. Clone this repository, and direct your terminal window to the local project folder 
2. Create a virtual environment to install all the required libraries
    ```python3.12 -m venv venv```
3. Activate virtual environment
    ```source venv/bin/activate```
or on Windows: 
    ```.\venv\scripts\Activate.ps1 ```
   
You should see (venv) at the beginning of your Terminal line indicating the virtual environment is activated.

4. Install the required libraries into your virtual environment
```pip install -r requirements.txt```
   
Note: If you add any new python packages, be sure to run 
```pip freeze > requirements.txt``` 
to update the requirements file.

---
## 4 Running the application
Note: Your virtual environment must be activated, before running the application:

### Setting-up the article spreadsheet
The application first needs news articles to read from. Call:
```base
python -m src.main -f get_news -d  "{name of data file}"
```
Replacing {name of data file} with the csv file you'd like to save articles to.

When called for the first time the 'column_names.txt' files is used to set-up the spreadsheet columns.
Each line in the 'column_names.txt' file represents a new column.

## 5 Article information population
The columns in the spreadsheet are as follows:

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

Note: new columns can be added (or deleted) as needed, 
just be sure the columns that are to be populated via the LLM prompts exist.

### Reading articles from spreadsheet

Once you have a list of articles (see Setting-up the article spreadsheet above), you can read them to start populating information in the spreadsheet.
call:
```
python -m src.main -f read_articles -d "{name of data file}" -r {row_number} -q {question file}
```

Replacing:
- {name of data file}: with the csv file you saved your articles to earlier.
- {row_number}: with the row number you'd like to read, starting from 0. Omit this to prompt all news articles in the spreadsheet that have not been 'processed'.
- {question file}: with a csv file containing prompts (*see Article information extraction* below for thee details of this file)

Note: without passing question file, a chat bot is enabled to allow you to ask questions of the article. 
This is useful during the testing of new prompts to be added the question bank.


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
To gain authentication to the feature service, a .env file should be created and saved, 
replacing the {} variables as appropriate:
```
AGOL_URL={https://your-org.maps.arcgis.com}
AGOL_USERNAME={your.username}
AGOL_PASSWORD={your.password}
FEATURE_SERVICE_ITEMID={abcdef1234567890abcdef1234567890}
XY_DECIMALS=6      # precision for rounding X,Y coordinates

```

To Add new points to the feature service,
call:
```bash
python -m src.main -f upload_points -d "{name of data file}"
```