#----------------------------------
#Functions 
#----------------------------------
import pandas as pd

def read_csv(csv_url):
    return pd.read_csv(csv_url)

def is_null(df):
    return df.isnull().sum().sort_values(ascending=False)

def outlier_thresholds(df, col_name, q1 = 0.05, q3 = 0.95 ):
    quartile1 = df[col_name].quantile(q1)
    quartile3 = df[col_name].quantile(q3)
    interquantile_range = quartile3 - quartile1
    upper_limit = quartile3 + 1.5 * interquantile_range
    lower_limit = quartile1- 1.5 * interquantile_range
    return lower_limit,upper_limit

def get_outliers(df, col_name):
    # get outlier thresholds
    low, up = outlier_thresholds(df, col_name)
    # Return the outliers
    return df.loc[((df[col_name] < low) | (df[col_name] > up)), col_name]

def column_name_replace_space(columns):
    return [col.replace(' ','_') for col in columns]

def constrain_dataset(df,selected_countries):
    try:
        return  df[df.Entity.isin(selected_countries)].query('Year>=1980').reset_index(drop=True)
    except:
        return  df[df.Country.isin(selected_countries)].query('Year>=1980').reset_index(drop=True)

