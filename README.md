# COVID-19 Cases and Deaths in the United States with Population Data

## Overview
This repository uses python scripts to combine and enhance the latest county level COVID-19 cases and deaths data at the county level (using [FIPS](https://en.wikipedia.org/wiki/FIPS_county_code) codes) from the [NY Times Github Repository](https://github.com/nytimes/covid-19-data) with population data from the [2010 Census](https://www.census.gov/data/datasets/time-series/demo/popest/2010s-counties-total.html) from the US Census Bureau downloaded from the US Census Bureau website.

The latest combined output dataset can be found in the [latest_covid19data_withpopulationdata.csv](latest_covid19data_withpopulationdata.csv) file in the top-level directory. You can also find files loaded on previous days in the [/data/history](/data/history) folder to identify any changes made to historical data in the NY Times dataset.

For every FIPS code and Date the data contains State Name, County Name, Cumulative COVID-19 Cases to Date, Cumulative COVID-19 Deaths to Date, Daily Cases, Daily Deaths, 2010 Population, and Esitmated 2019 Population. 

**Note that the population values for "Unknown" counties are the population totals for the entire state but the cases and deaths are those where the correct county is unknown.** 

The repeatble data pipeline is stored in the top-level directory and broken in to three micro-services: covid.py, census.py, and main.py:  
- **[covid.py](/covid.py)** downloads and transforms the latest county level data from the NY Times Github repository and outputs a pandas dataframe
- **[census.py](/census.py)** downloads and transforms the 2010 census data stored in the /data folder downloaded from the US Census Bureau and outputs a pandas dataframe
- **[main.py](/main.py)** calls the load functions in the covid.py and census.py modules to get and merge the pandas dataframes in to one pandas dataframe and output and overwrite the latest csv file in the top-level directory and also upload a dated copy to the /data/history folder

A daily schedule can be created that execute the main.py file directly from the top-level directory.

This repository also includes:
- A heavily commented ["EDA"](/notebooks/EDA.ipynb) jupyter notebook in the [notebooks](/notebooks) folder used to initally test loading the data and identify data issues that are addressed in the transformation portion of the data pipelines. 
- Lookup tables created using the EDA notebook stored in the [/data](/data) directory. See [Data Sources](#data-sources) section for more info.
- A [Makefile](/Makefile) for repeatable programatic executions
- A [requirements.txt](/requirements.txt) file with all python packages used in the code in this notebook.

## Getting Started
### Pre-requisites
    You muts have a workstation with Git and Python 3 installed. 
    Optionally, install Make (See [best answer on StackOverflow](https://stackoverflow.com/questions/32127524/how-to-install-and-use-make-in-windows) for installing Make on Windows).

### Create your Own Pipeline


## Data Sources

## Output Data

## Future Considerations


https://portal.311.nyc.gov/article/?kanumber=KA-02877
