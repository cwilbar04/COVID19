import pandas as pd
from datetime import datetime
from covid import load_covid_data
from census import load_census_data

def main():
    covid_data = load_covid_data()
    census_data = load_census_data()
    
    output = covid.merge(census, how='left', left_on='fips', right_on='FIPS')
    
    output.to_csv('covid19data_withpopulationdata.csv', sep=',')
    
    
if __name__ == '__main__':
    print(f'Started creating dataset at {datetime.now()}')
    main()
    print(f'Sucessfully output file at {datetime.now()}')