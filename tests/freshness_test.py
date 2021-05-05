import pandas as pd
from datetime import datetime, timedelta

def test_date():
    # Test the most recent date is w/in 48 hours
    # Data should be updated daily on NY Times and Locally after run
    # Data should not be more than 48 hours old
    file_path = 'latest_covid19data_withpopulationdata.csv'
    input_data = pd.read_csv(file_path, sep=',')
    today = datetime.now()
    minimum_date = input_data['Date'].max()
    minimum_date = datetime.strptime(minimum_date, '%Y-%m-%d')
    return minimum_date >= today - timedelta(days=2)