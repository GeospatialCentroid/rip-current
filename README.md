# Rip Current

This project finds news articles that document fatalities that have occurred as a result of rip currents.

## Setup
A Large Language Model (LLM) to extract information from news articles. 
Ollama is the application used for running LLMs, and we're currently using the gemma3:1b LLM.

### Installing Ollama and the LLM
First download and install Ollama: https://ollama.com/download/
Then from the commandline, run: 
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
   
You should see (venv) at the beginning of your Terminal line.

4. Install the requirements into your first virtual environment
```pip install -r requirements.txt```
   
Note: If you add any python packages, be sure to run ```pip freeze > requirements.txt```

## Running the application
Note: Your virtual environment must be activated, before running the application:

### Setting up the article spreadsheet
The application first needs news articles to read from. Call:
```
python main.py -f process_articles -d  "{name of data file}"
```
Replacing {name of data file} with the csv file you'd like to save articles to.
e.g 

The above can be called as many times as you like, since only new articles will be added to the
spreadsheet.

### Reading articles spreadsheet.
Once you have a list of articles, you can read them to start populating information in the spreadsheet.
Call:
```
python main.py -f read_articles -d "{name of data file}" -r {row_number}
```

Replacing:
- {name of data file}: with the csv file you saved your articles to earlier.
- {row_number}: with the row number you'd like to read

### putting it all together
``` 
python main.py -f process_articles -d "rip_current_articles.csv"

python main.py -f read_articles -d "rip_current_articles.csv" -r 4
```


