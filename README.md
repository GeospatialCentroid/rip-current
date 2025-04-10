# rip-current

## Setup

### Downloading and setting-up
    
1. Clone the project, and direct your terminal window to the project folder 
2. create virtual environment
    ```python3.12 -m venv venv```
3. Activate virtual environment
```source venv/bin/activate```
or on windows: 
```.\venv\scripts\Activate.ps1 ```

4. Install the requirements
With python and git installed
```pip install -r requirements.txt```
Note: if you add any python packages, be sure to run ```pip freeze > requirements.txt```

## Running the application
With the virtual environment activate, from your terminal run:
```
python main.py -d "{name of data file}"
```