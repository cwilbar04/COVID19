# COVID-19 Cases and Deaths in the United States with Population Data

## Overview
This repository uses python scripts to combine and enhance the latest county level COVID-19 cases and deaths data at the county level (using [FIPS](https://en.wikipedia.org/wiki/FIPS_county_code) codes) from the [NY Times Github Repository](https://github.com/nytimes/covid-19-data) with population data from the [2010 Census](https://www.census.gov/data/datasets/time-series/demo/popest/2010s-counties-total.html) from the US Census Bureau downloaded from the US Census Bureau website.

The latest combined output dataset can be found in the [latest_covid19data_withpopulationdata.csv](latest_covid19data_withpopulationdata.csv) file in the top-level directory. You can also find files loaded on previous days in the [/data/history](/data/history) folder to identify any changes made to historical data in the NY Times dataset.

For every FIPS code and Date the data contains:
- State Name
- County Name
- Cumulative COVID-19 Cases to Date
- Cumulative COVID-19 Deaths to Date
- Daily Cases
- Daily Deaths
- 2010 Population
- Estimated 2019 Population. 

**Note that the population values for "Unknown" counties are the population totals for the entire state but the cases and deaths are those where the correct county is unknown.** 

**Also note there will be some cases where the Daily count is a negative number. This occurs when the cumulative data is updated in the NY Times repository for one month but not all historical data is updated. I have chosen to leave the negative values in the data set to identify when this has occurred but you many want to set these values to 0 depending on your use case.**

The repeatble data pipeline is stored in the top-level directory and broken in to three micro-services: covid.py, census.py, and main.py:  
- **[covid.py](/covid.py)** downloads and transforms the latest county level data from the NY Times Github repository and outputs a pandas dataframe
- **[census.py](/census.py)** downloads and transforms the 2010 census data stored in the /data folder downloaded from the US Census Bureau and outputs a pandas dataframe
- **[main.py](/main.py)** calls the load functions in the covid.py and census.py modules to get and merge the pandas dataframes in to one pandas dataframe and output and overwrite the latest csv file in the top-level directory and also upload a dated copy to the /data/history folder

A daily schedule can be created that executes the main.py file directly from the top-level directory.

This repository also includes:
- A heavily commented ["EDA"](/notebooks/EDA.ipynb) jupyter notebook in the [notebooks](/notebooks) folder used to initally test loading the data and identify data issues that are addressed in the transformation portion of the data pipelines. 
- Lookup tables created using the EDA notebook stored in the [/data](/data) directory. See [Data Sources](#data-sources) section for more info.
- A [unique](/tests/unique_test.py) and [freshness](/tests/freshness_test.py) test script used with pytest to check the data loaded contains no duplicate entries and data was loaded from within the past 48 hours.
- A [Makefile](/Makefile) for repeatable programatic executions.
- A [requirements.txt](/requirements.txt) file with all python packages used in the code in this notebook.

## Getting Started
### Pre-requisites  
You must have a workstation with Git and Python 3 installed and in your class path.   
Optionally, install Make (See [best answer on StackOverflow](https://stackoverflow.com/questions/32127524/how-to-install-and-use-make-in-windows) for installing Make on Windows).

### Create your Own Pipeline

#### 1. Clone Git Repository
To get started, clone the repository to your local drive (follow prompts to authenticate to GitHub if requested) and navigate to top level directory:
```cmd
git clone https://github.com/cwilbar04/COVID19.git
cd COVID19
```

#### 2. Create and Activate Python Virtual Environment
Next, create and activate a [python virtual environment](https://docs.python.org/3/tutorial/venv.html).  
Below commands create and activate virtual environment in directory above the current working directory.  
If desired to create virtual environment in a different location please change directory back to top level github directory after creating and activating viruatl environment.  

**Windows**
```cmd
python -m venv ..\.venv
.\..\.venv\Scripts\activate.bat
```  

**Mac\Linux**
```cmd
python3 -m venv ..\.venv
source /../.venv/bin/activate
```

#### 3. Install Required Python Packages

If you have Make:
```cmd
make install
```

else, execute:
```cmd
pip install -r requirements.txt
```

#### 4. Execute Main Script
```cmd
python main.py
```

#### 5. Test Uniqueness and Freshness
Here we use pytest to execute the test scripts in the tests directory.
The unique_test.py script tests that there are no duplicate combinations of FIPS and date.
The freshness_test.py script tests that maximum date is within 48 hours.
Should see both tests pass. If not, further investigation is needed to understand what went wrong.

If you have Make:
```cmd
make test
```

else, execute:
```cmd
python -m pytest -vv
```


## Data Sources

### COVID-19 Data
Cumulative Cases and Deaths of Coronavirus (Covid-19) Data in the United States is dowloaded directly from the [NY Times Github Repository](https://github.com/nytimes/covid-19-data).

In particular, the raw CSV for [U.S. County-Level Data](https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv) is loaded in to a pandas datafram in the covid.py script.

According to the [Github README.md](https://github.com/nytimes/covid-19-data/blob/master/README.md) this data is compiled time series data from state and local governments and health departments collected in an attempt to provide a complete record of the ongoing outbreak. Currently, this pipeline pulls the "historical" data that contain data up to, but not including the current day, representing the final counts at the end of each day. Future considerations could incorporate the "live" data as well but this data changes throughout the day so would be volatile for most reporting needs.

The data reported by the NY Times is cumulative totals. In order to calculate the daily totals, I have taken the current days cummulative total - the previous days cummulative total. In some cases, the cummulative total decreases when there are corrections made. In this case, there will be "negative" daily totals. I have decided to allow negative daily totals to persist to identify these cases. It is advised that care be taken with these values and they be changed to 0 when appropriate.

This data is mostly clean, however, there are some instances where there is a NULL or missing entry for cases or deaths. In this pipeline I have replaced NULLs/missing data with 0.

Additionally, there are a few ["geographic exceptions"](https://github.com/nytimes/covid-19-data/blob/master/README.md#geographic-exceptions) in the data that result in missing FIPS codes. In order to present the most accurate aggregated data as possible, I have chosen to address the missingness in the following ways:
- **Missing FIPS Code for New York City** 
  - The NY Times reports all cases and deaths for NYC in one line item, but NYC actually consists of 5 separate counties with their own FIPS codes. In order to not lose this data, I have decided to assign the total cases and deaths for NYC proportionally to the 5 distinct counties based on their relative estimated 2019 population. Using the 2010 Census data, I have created a dataset in the data foloder: [missing_fips_population_proportion.csv](/data/missing_fips_population_proportion.csv). This dataset contains the 5 NYC boroughs and their "population proportion" representing the county's population/total NYC population. In the pipeline, I then create entries for all 5 boroughs and multiple the listed number of cases and deaths for NYC by the population proportion of each county (and round down because you can't have a proportion of a person). Thus, the data for the 5 New York counties is estimated proportionally based on the total NYC cases and deaths for a given day.
- **Missing FIPS Code for Kansas City, Missouri and Joplin, Missouri**
  - Similar to NYC, total cases for Kansas City and Joplin are reported at the city level instead of the county level and there is not FIPS code for these cities. In these cases, however, the counties have borders that extend outside of the city limits and there is data for these FIPS codes that represent cases/deaths that occurred oustide of the city limits. In this case, I have again chosen to proportionally break the cases for the two cities in to their respective counties based on population size and in this case I have added the proportionate amount to the already existing rows. The [missing_fips_population_proportion.csv](/data/missing_fips_population_proportion.csv) file contains the proprortions for these counties as well and I have again chosen to round down. Ultimately, this means the data for these counties are rough estimates but the total cases/deaths more accurately reflects the true total because I have not discarded the data for these three cities.
- **"Unknown" Counties**
  - 





## Output Data

## Future Considerations



