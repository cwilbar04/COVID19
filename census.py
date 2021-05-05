"""
This module is used to load census data from the local filepath after cloning the repository
in to a pandas dataframe that can be used for futher analysis.

More info on the source data can be found here:
    https://www.census.gov/data/datasets/time-series/demo/popest/2010s-counties-total.html

A standardized 'FIPS' column is added that can be joined to COVID-19 data.
    FIPS = 2-digit State Code with zero padding + 3-digit County Code with zero padding
"""

# Import packages
import pandas as pd

def load_census_data():
    """
    Parameters
    ----------
    No input parameters

    Returns
    -------
    Transformed dataframe based on raw census data from the United States Census Bureau.

    File downloaded locally to repository.
    Function must be run from cloned repository to work correctly.

    See https://www.census.gov/data/datasets/time-series/demo/popest/2010s-counties-total.html
    for more info on dataset.
    """

    # Import Census data from local file using relative path
    # Load only relevant columns to speed up performance
    filepath = './data/co-est2019-alldata.csv'
    columns = ['STATE', 'COUNTY', 'STNAME',
       'CTYNAME', 'CENSUS2010POP', 'POPESTIMATE2019']
    census = pd.read_csv(filepath, sep = ',', compression=None, usecols = columns )

    # Create FIPS column in Census data
    # FIPS = 2-digit State Code with zero padding + 3-digit County Code with zero padding
    census['FIPS'] = census['STATE'].astype(str).str.zfill(2) + \
                        census['COUNTY'].astype(str).str.zfill(3)

    return census

if __name__ == '__main__':
    census_data = load_census_data()
    print(census_data.head())
