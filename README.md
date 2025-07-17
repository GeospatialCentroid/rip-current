## Rip Current

---

## 1 Project Purpose

The documented number of fatalities that have occurred as a result of drownings related to rip currents is not consistent. 
In an effort to better quantify the annual number of these drownings, this project uses news articles and AI to gather details from these news articles.
Each article is prompted with a series of questions used to populate a spreadsheet.
The location information gathered (Beach, City, State) are geolocated and then used to identify the closest Weather Forecast Office (WFO).
These geolocated points are then uploaded to an ArcGIS Online Feature Service for public access.
Before the results are added to the Feature Service, the spreadsheet must be used with values in both the 'approved' and 'approved_by' columns, 
typically a 'y' and the initials of the approver respectively.

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
│   ├── compare_models.py       ← Compare the outputs of vector files
│   ├── create_vector_file.py   ← Create a vector file of the geolocated results
│   ├── get_location.py         ← Geolocation and WFO identifyer
│   ├── get_news.py             ← Google News accesser
│   ├── main.py                 ← Command‑line driver
│   ├── read_news.py            ← News article reader using AI and offline‑article manager
│   └── upload_points.py        ← Uploader of unique points to ArcGIS Online Feature Service
│
├── column_names.txt      ← The header columns
├── questions.csv         ← The questions used to prompt each news article
└── rip_current_articles.csv      ← Example file output, this one has old data appended (path is user‑selectable).
```

---

## 3 Setup
A Large Language Model (LLM) is used to extract information from news articles. 
Ollama is the application used for running LLMs, we tested with several  LLms.
 **gemma3:1b** is the default LLM used by the program.

### Installing Ollama and the LLM
First download and install Ollama: https://ollama.com/download/

Then from the command line, run: 
```bash
ollama pull gemma3:1b
```

#### Using other LLMs
There are many LLM options to choose from and other LLMs may be useful. If you'd like to use another LLM, 
please first check if it's Ollama compatible by going to https://ollama.com/library. 
With the LLM of your choosing, get the model name you desire by navigating to the details page, then run:
```bash
ollama pull {model_name}
```
replacing ```{model_name}``` with the model name.


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
## 4 Quickly running the application and technical overview
*Note: Your virtual environment must be activated, before running the application.*
The application has many smaller programs it can run, though the most common two are 'get_news' and 'read_news'.
Calling the following is a good first step:

```
python -m src.main -f all -d "output.csv" -s 'rip current, rip current drowning, rip currents, sneaker waves, sneaker wave drowning' -m llama3.2:3b  -q questions.csv -c -k AIzaSyCdnWn8Kanu6NMDvQNggPC_rjYJfdWL_ko -start 'last'

```
This will:
1. Create a CSV file (if it doesn't exist) using "output.csv"
   The CSV file will have the columns listed in the 'column_names.txt' file
2. The CSV file will then be filled with news articles that have been searched for using the -s parameter
   The commas in this string are used to separate the searches to increase the resulting news article results. Duplicates are removed.
3. The news articles are then downloaded, the text is extracted, and these files are saved into the 'articles folder'
    The -m parameter (model), is then used with the -q parameter ('questions.csv') to prompt the LLM and collect information from the article
4. The extracted information also includes a location which is geolocated using the Google Maps API and the -k paramter is the 'key' to using this API 
    
The above code can be called on a routine bases as the date of the last collected news articles will be used as the start date for subsequent searches.
A 'y' flag is also added in the 'processed' column to rows in the spreadsheet to prevent the LLM from trying to prompt them again.
   
### Running smaller application programs separately

#### Setting-up the article spreadsheet
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
Running the ```get_news``` script should be called multiple times with different search terms to help increase the pool of search results.

Optional ```-start {MM/DD/YYYY} -end {MM/DD/YYYY}```
Though a check is done on retrieved news articles to remove duplicates, it may be beneficial to constrain the date range of articles.
Or simply use the -start value of ```-start 'last'```


Putting it all together a search for news articles could be:
```base
python -m src.main -f get_news -d  output.csv -s 'rip current drowning' -start '06/01/2025' -end '06/06/2025'
```

### Article information population
When ```get_news``` is called for the first time the 'column_names.txt' files is used to set up the spreadsheet columns.
Each line in the 'column_names.txt' file represents a new column.


*Note: new columns can be added (or deleted) as needed, 
just be sure the columns that are to be populated via the LLM prompts exist.*

### 5 Reading articles from the spreadsheet

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
   
Putting it all together

```
python -m src.main -f read_news -d "output.csv" -m llama3.2:3b  -q questions.csv -c -k AIzaSyCdnWn8Kanu6NMDvQNggPC_rjYJfdWL_ko

```

## 6 Article Information Extraction
The program extracts information from articles by prompting a LLM with questions.
Each question is linked to a column in the {name of data file} spreadsheet. 
Questions are stored in the {question file} file using the column structure:
This {question file} is often saved as questions.csv.

* pre: start of question to add context
* question: actual question
* post: how you'd like your response structured
* options: the choices for the response
* column name: the column to be populated in the rip_current_articles.csv spreadsheet

Note: The questions are asked in the order that they are listed in the {question file} and the constraint on response does impact other questions asked.
For example, the question 
```"In this article,",how did the person drown?,Structure your response as only,"""Rip Current"", ""High Surf"", ""Sneaker Wave"", ""Other"" or ""Unknown"".",cause_of_drowning,```
Actually gives the AI permission to respond "Unknown" is later questions. This is helpful in preventing the AI from giving a 'yes' or 'no' answer. 

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

## 8 Create Shapefile of Locations
To create a shapefile (or other standard geospatial data output [e.g geojson, KML, geodatabase]), please call the following
```
python -m src.main -f create_shapefile -o "{name of shape file}"
```
Replacing {name of shape file} with the name of shapefile you'd like to create, and using the 3 letter extension to define the file type.

## Comparing LLM outputs
While trying to access which model was most accurate, a 'source_of_truth.csv' file was created with know news articles where victims have drowned.
This file was stripped of its answers and ran through the 'read_news.py' program, producing files:
- llama_model_output.csv
- gemma_model_output.csv

A 'model' column was created in each of the files using:
- 'manual' for the 'source of truth', 
- llama for 'llama3.2:3b' LLM and
- 'gemma' for  'gemma3:1b' LLM.

Note: deepseek-r1:1.5b was also tested but the results we not constrained as the questions prompted, making the results unusable. deepseek-r1:1.5b was also really slow to run.

These files were then combined and a program was created using ChatGPT to compare the results.
This program call be called using:

```
python src/compare_models.py \
  --file combined_output.csv \
  --objectid_col OBJECTID \
  --model_col model \
  --manual_value manual \
  --value_cols age gender WFO

```

Model Comparison Results:

| Model   | Total Accuracy   | age    | gender   | WFO    |
|---------|------------------|--------|----------|--------|
| llama   | 58.38%           | 52.63% | 46.55%   | 75.86% |
| gemma   | 46.24%           | 42.11% | 20.69%   | 75.86% |




## References  
OpenAI. (2025). ChatGPT (July 14th version) [Large language model]. https://chat.openai.com/chat