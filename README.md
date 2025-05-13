# Rip Current

This project finds news articles that document fatalities that have occurred as a result of drownings related to rib currents.

## Setup
A Large Language Model (LLM) is used to extract information from news articles. 
Ollama is the application used for running LLMs, and we're currently using the **gemma3:1b** LLM.

### Installing Ollama and the LLM
First download and install Ollama: https://ollama.com/download/
Then from the command line, run: 
```
ollama pull gemma3:1b
```

### Downloading and setting-up the python application
    
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
   
Note: If you add any new python packages, be sure to run ```pip freeze > requirements.txt``` 
to update the requirements file

## Running the application
Note: Your virtual environment must be activated, before running the application:

### Setting-up the article spreadsheet
The application first needs news articles to read from. Call:
```
python main.py -f process_articles -d  "{name of data file}"
```
Replacing {name of data file} with the csv file you'd like to save articles to.

When called for the first time the 'column_names.txt' files is used to setup the spreadsheet columns.
Each line in the column_names.txt file represents a new column.

## Article information population
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

### Reading articles spreadsheet

Once you have a list of articles (see Setting-up the article spreadsheet above), you can read them to start populating information in the spreadsheet.
Call:
```
python main.py -f read_articles -d "{name of data file}" -r {row_number} -q {question file}
```

Replacing:
- {name of data file}: with the csv file you saved your articles to earlier.
- {row_number}: with the row number you'd like to read.
- {question file}: with a csv file containing prompts (*see Article information extraction* below for thee details of this file)

Note: without passing question file, a chat bot is enabled to allow you to ask questions of the article. 
This is useful during the testing of new prompts to be added the question bank.


## Article information extraction
The program extracts information from articles by prompting the LLM with questions.
Each question is linked to a column in the {name of data file} spreadsheet. 
Questions are stored in the {question file} file using the column structure:
* pre: start of question to add context
* question: actual question
* post: how you'd like your response structured
* options: the choices for the response
* column name: the column to be populated in the rip_current_articles.csv spreadsheet

