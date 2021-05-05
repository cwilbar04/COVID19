"""
  This module is used to load the latest COVID19 data from the NY Times github repository
"""

# Import packages
import pandas as pd

def previous_row_value(data,shift_column,sort_column,groupby_column=None, fill_value=pd.NA ):
    """
    Parameters
    ----------
    data:
      Dataframe with a specific column to generate previous rows data
    shift_column:
      Stirng with specific column name to return the previous rows data
    sort_column:
      String with specific column name to sort the data by to insure
      expected previous rows data returned
    groupby_column:
      Optional string used to shift the data based on specific groups.
       The df will also be sorted by this column if it is passed to function.
    fill_vale:
      Option value used to fill the first row. Defaults to pandas "NA" if not passed to function.

    Returns
   -------
    df_with_shift:
        The original dataframe with a new column
        `previous_[shift_column]` containing the previous rows data
        based on the sort_column and optional groupby_column
    """

    if groupby_column is None:
        data.sort_values(by=[sort_column], inplace=True, ascending = True)
        df_with_shift = data.reset_index(drop=True)
        df_with_shift[f'previous {shift_column}'] = df_with_shift[shift_column].shift(1,
                                                                  fill_value=fill_value)
        return df_with_shift

    data.sort_values(by=[groupby_column,sort_column], inplace=True, ascending = True)
    df_with_shift = data.reset_index(drop=True)
    df_with_shift[f'previous {shift_column}'] = \
            df_with_shift.groupby(groupby_column)[shift_column].shift(1, fill_value=fill_value)
    return df_with_shift

def load_covid_data():
    """
    Parameters
    ----------
    No input parameters

    Returns
   -------
    Transformed dataframe based on county level data
    Loaded from https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv

    See https://github.com/nytimes/covid-19-data/blob/master/README.md for more info on source.
    """

    # Import COVID data from github in to pandas data frame
    url = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv'
    covid = pd.read_csv(url,
                        sep=',',
                        compression=None,
                        dtype={'fips':str},
                        parse_dates=['date'],
                        cache_dates = True)

    # Create "county,state" column as unique identifier
    covid['county,state'] = covid.county + ',' + covid.state

    # Replace any NULLS in cases and deaths with 0
    int_cols = ['cases','deaths']
    covid.fillna(value={col:0 for col in int_cols}, axis=0, inplace=True)
    for col in int_cols:
        covid[col] = covid[col].astype(pd.Int64Dtype())

    # Load file from census data with state level fips codes.
    # This will allow us to replace the Unknown County data with FIPS codes at the state level.
    # This will allow us to not lose this data when doing full aggregation across all states
    # and gives easy access to the state population
    state_level_data = pd.read_csv('./data/state_level_fips_codes.csv', sep='|')

    # Merge the State Level Data with the Covid data
    # Apply the state level FIPS code to the Unknown Counties
    covid = covid.merge(state_level_data, how='left', left_on='state', right_on='STNAME')
    covid.loc[covid['county']=='Unknown','fips'] = covid.loc[covid['county']=='Unknown','FIPS']
    covid.drop(columns=['STNAME','FIPS'], inplace=True)

    # Load file with relative population size of counties for cities with missing fips codes
    # Data for the cities is broken in to the respective counties with a column indicating
    # the relative size of the county compared to other counties in the same city
    # This is still inaccurate but at least it does not eliminate the data from these
    # large cities when looking at fips level data
    # This data is rounded down to minimize the impact
    population_df = pd.read_csv('./data/missing_fips_population_proportion.csv',
                                 sep='|',
                                 dtype={'FIPS':str})

    # Merge population proportions to main dataframe on FIPS to attach population proportion amounts
    # to Missouri Counties that are part of a city reported separately
    covid = covid.merge(population_df[['City,State','FIPS','County Population Proportion']],
                           how='left', left_on='fips', right_on='FIPS')

    # Merge covid dataframe to itself on "City,State" to "county,state" and date
    # to add the cases and deaths for the cities in Missouri
    # reported separately on to the appropiate county level data
    covid = covid.merge(covid[['date','county,state','cases','deaths']],
                        how='left', left_on=['City,State','date'],right_on=['county,state','date'],
                        suffixes=[None,'_city'])

    # Add the city cases and deaths to the county cases and deaths
    # Based on the relative size of the counties
    # Round down to insure integer number of cases
    filter_cond = ~covid['cases_city'].isna()
    covid.loc[filter_cond,'cases'] += (covid.loc[filter_cond,'County Population Proportion']*\
                                              covid.loc[filter_cond,'cases_city']).astype(int)
    covid.loc[filter_cond,'deaths'] += (covid.loc[filter_cond,'County Population Proportion']*\
                                              covid.loc[filter_cond,'deaths_city']).astype(int)

    # Remove columns only added for calculations
    covid.drop(labels=['City,State',
                        'FIPS',
                        'County Population Proportion',
                        'county,state_city',
                        'cases_city',
                        'deaths_city'],
                         axis = 1, inplace=True)

    # For New York City, merge population dataframe on "county,state" to "City,State"
    # to add new rows for each county in New York City
    # Only merge population dataframe for the New York City entries

    covid = covid.merge(population_df.loc[population_df['City,State'] == 'New York City,New York',
                                            ['City,State'
                                            ,'FIPS'
                                            ,'County'
                                            ,'County Population Proportion']
                                            ],
                          how = 'left', left_on='county,state', right_on='City,State')

    # Multiply total cases and deaths in New York City by the Population Proportion and round down.
    # Cases/deaths will be lost but not as many as if we did not perform any transformation
    filter_condition = ~covid['City,State'].isna()
    covid.loc[filter_condition,'county'] = covid.loc[filter_condition,'County']
    covid.loc[filter_condition,'fips'] = covid.loc[filter_condition,'FIPS']
    covid.loc[filter_condition,'cases'] = (covid.loc[filter_condition,'cases']*\
                    covid.loc[filter_condition,'County Population Proportion']).astype(int)
    covid.loc[filter_condition,'deaths'] = (covid.loc[filter_condition,'deaths']*\
                    covid.loc[filter_condition,'County Population Proportion']).astype(int)

    # Remove columns only added for calculations
    covid.drop(labels=['City,State','FIPS','County Population Proportion', 'County'],
                axis = 1, inplace=True)

    # Cases and deaths are reported as cumulative totals
    # We take the difference from the previous days record for each FIPS code to get daily totals
    # First rename columns to be cumulative columns
    covid.rename(columns={'cases':'cumulative cases to date',
                          'deaths':'cumulative deaths to date'},inplace=True)

    # Apply function to get the previous days cumulative cases and deaths
    # for each each fips with a default value of 0 if no previous value
    covid = previous_row_value(covid,
                              shift_column='cumulative cases to date',
                              sort_column='date',
                              groupby_column='fips',
                              fill_value=0)

    covid = previous_row_value(covid,
                              shift_column='cumulative deaths to date',
                              sort_column='date',
                              groupby_column='fips',
                              fill_value=0)

    # Calculate daily cases and deaths as todays cumulative total - yesterdays cumulative total
    covid.loc[:,'daily cases'] = covid.loc[:,'cumulative cases to date'] - \
                                    covid.loc[:,'previous cumulative cases to date']
    covid.loc[:,'daily deaths'] = covid.loc[:,'cumulative deaths to date'] - \
                                    covid.loc[:,'previous cumulative deaths to date']

    # Note there is a known inconsistency in data that cumulative totals do not always increase
    # if data is updated on a previous date.
    # This can result is negative values for daily cases or deaths.
    # These have been left as is so changes can be understand and aggregations will be consistent
    # Consider changing this logic to set these values to 0 instead of negative values
    # depending on use case and target audience

    # Drop previous columns and no longer needed county,state column
    covid.drop(columns=['previous cumulative cases to date',
                        'previous cumulative deaths to date',
                        'county,state'], inplace=True)

    return covid

if __name__ == '__main__':
    covid_data = load_covid_data()
    print(covid_data.head())
