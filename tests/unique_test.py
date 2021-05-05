import pandas as pd

def unique_test(data,columns):

    # Get total rows
    total_rows = len(data.index)
    
    # If input is a list, need to create column that is concatenaton of list values
    if isinstance(columns, list):
        new_column = '-'.join(columns)
        columns_new = [f"data.loc[:,'{col}'].astype('str')" for col in columns]
        data.loc[:,new_column] = eval((" + '-' + ").join(columns_new))
    else:
        new_column = columns
        
    # Get count of unique values in the unique tests column(s)
    distinct_rows = len(data[new_column].unique())
    
    #Retrun True if every row is unique, else False
    return total_rows == distinct_rows

def test_latest_data():
    # Test the latest data is unique per date/FIPS
    file_path = 'latest_covid19data_withpopulationdata.csv'
    columns = ['Date','FIPS']
    input_data = pd.read_csv(file_path, sep=',')
    assert unique_test(input_data,columns)

if __name__ == '__main__':
    test_data = pd.read_csv('../latest_covid19data_withpopulationdata.csv', sep=',')
    test = unique_test(test_data,['Date','FIPS'])
    print(test)
    

