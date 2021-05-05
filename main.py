"""
The main module for this repository.

This script calls the covid.py and census,py scripts to load transformed
COVID and Census data in to Pandas Dataframes.

The script then combines these two datasets and renames the columns.

Finally, when called directly an output file is placed in this directory:
covid19data_withpopulationdata.csv
"""

#Import Packages
from datetime import datetime
from covid import load_covid_data
from census import load_census_data

def main():
    """
    Parameters
    ----------
    No input parameters

    Returns
   -------
    Combined COVID19 and Census Population Data in a Pandas Dataframe
    """
    # Load transformed COVID and Census data sets
    covid_data = load_covid_data()
    census_data = load_census_data()

    # Merge COVID and Census data sets
    # Inner join drops non-US State data and Kansas City and Joplin Missouri intentionally
    output = covid_data.merge(census_data, how='inner', left_on='fips', right_on='FIPS')

    # Drop unnecessary columns
    output.drop(columns=['CTYNAME','STNAME', 'STATE', 'COUNTY', 'fips'], inplace=True)

    # Rename columns to be more user friendly
    output.rename(columns={'date':'Date',
                            'county':'County',
                            'state':'State',
                            'cumulative cases to date':'Cumulative Cases to Date',
                            'cumulative deaths to date':'Cumulative Deaths to Date',
                            'daily cases':'Daily Cases',
                            'daily deaths':'Daily Deaths',
                            'CENSUS2010POP':'2010 Census Actual Population',
                            'POPESTIMATE2019':'Estimated 2019 Population'}
                            ,inplace=True)

    return output

if __name__ == '__main__':
    print(f'Started creating dataset at {datetime.now()}')
    output_df = main()
    OUTPUT_FILE = 'covid19data_withpopulationdata.csv'
    output_df.to_csv(OUTPUT_FILE, sep=',', header=True, index=False)
    print(f'''Sucessfully output {len(output_df.index)} rows to
                {OUTPUT_FILE} at {datetime.now()}''')
