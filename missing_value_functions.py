from sklearn.model_selection import train_test_split
from sklearn import linear_model
import numpy as np
from sklearn.metrics import r2_score
import math
from basic_functions import read_csv

###Income Dataset

# getting the share of columns
def get_share_cols(df_income):
    return [col for col in df_income.columns if df_income[col].dtypes != "O" and col not in "Year"]


# finding the which columns are not null when wanted column is null
# If the wanted column nan and one of the columns nan it will not take that column as a feature
# Because we cant give model nan values when we are predicting 
def get_x_cols(df_income,y_col):
    share_cols = get_share_cols(df_income)
    return df_income[share_cols].columns[~df_income[share_cols][(df_income[y_col].isna())].isnull().any()].to_list()

# Training the regression model for filling the null values
def predict_income(df_income,y_col):
    try:
        # getting x_cols
        x_cols = get_x_cols(df_income,y_col)
        # Getting the training dataset
        # After finding x_cols find the data which x_cols and y_col is not nan 
        df_income_train = df_income[df_income[x_cols + [y_col]].notna().all(axis=1)][x_cols + [y_col]]
        # Splitting the data
        X_train, X_test, y_train, y_test=train_test_split(df_income_train[x_cols],df_income_train[y_col], test_size=0.2)
        # Initilazing regression model
        regr = linear_model.LinearRegression()
        # Transforming data to numpy arrays
        X_train = np.asanyarray(X_train[x_cols])
        y_train = np.asanyarray(y_train)
        X_test = np.asanyarray(X_test[x_cols])
        y_test = np.asanyarray(y_test)
        # Training the model
        regr.fit(X_train,y_train)
        # Predicting test data
        pred = regr.predict(X_test)
        # Evaulating models
        print(f'MAE = {np.mean(abs(y_test - pred))}')
        print(f'MSE = {np.mean(np.square(y_test - pred))}')
        print(f'RMSE = {np.sqrt(np.mean((y_test - pred) ** 2))}')
        print("Training score: ", r2_score(y_test, pred))
    except:
            return 'No null value found'
    return regr

# Getting the null values and filling them with regression model
def fill_income(df_income,y_col,regr):
    try : 
        # Getting the same x_cols
        x_cols = get_x_cols(df_income,y_col)
        # Getting the null data indexes
        null_index = df_income[((df_income[x_cols].notna().all(axis=1)) \
        & (df_income[y_col].isna()))].index
        # Predicting the null share_of value
        for index in null_index:
            x=np.asanyarray(df_income.loc[index,x_cols])
            y=regr.predict(x.reshape(-1,len(x)))
            df_income.loc[index,y_col]= round(y[0])
    except:
        return 'No null value found'

####################################################################

# Fertility-labor force

# Filling Labor_force_participation_rate in fertilty data
# Getting the data from Labor_force_participation_rate dataset
def fill_fertility(df_fertility):
    
    df_labor_force = read_csv('data\labor_force.csv')
    null_index=df_fertility[df_fertility['Labor_force_participation_rate'].isnull()].index
    for index in null_index:
        # Getting the null data
        Entity =df_fertility.loc[index,'Entity']
        Year=df_fertility.loc[index,'Year']
        # Fertility data year starts at 1980 and labor force starts 1990
        if (Year<1990):
            Year=1990
        # Getting the labor force participation from continent, gender, year 
        new_value =df_labor_force.query('Gender == "F" & Country == @Entity & \
                            Year == @Year ')['Labour_force_participation_rate']
        # If the value not exist on labor force dataset calculate that country's average of labor participation rate in existing years 
        if len(new_value) == 0:
            new_value = df_fertility[['Entity','Labor_force_participation_rate']].query('Entity == @Entity').\
            groupby('Entity').mean()['Labor_force_participation_rate'].iloc[0]
        else:
            new_value = new_value.values[0]
        df_fertility.loc[index,'Labor_force_participation_rate']=round(new_value,2)

###########################################################################################

# Labor Force Participation

# function for filling labor_force_participation values
# Null values filled with their continent mean values for that year and gender
def fill_labor_force_participation(df_labor_force,df_labor_force_by_continent):
    # get null values index
    null_index=df_labor_force[df_labor_force['Labour_force_participation_rate'].isnull()].index
    for index in null_index:
        # Getting the null data
        Continent=df_labor_force.loc[index,'Continent']
        Year=df_labor_force.loc[index,'Year']
        Gender=df_labor_force.loc[index,'Gender']
        # Getting the labor force participation from continent, gender, year 
        new_value =df_labor_force_by_continent.query('Continent == @Continent & \
                            Year == @Year & \
                            Gender == @Gender' )['Labour_force_participation_rate']
       # Filling null value with new value
        df_labor_force.loc[index,'Labour_force_participation_rate']=round(new_value.values[0],2)
   
#####################################################################################################

## Share of Employment

# Filling null values in the employment_percentage
# If the country has other data in years we fill with the average of the country
# If country has no data we get the that year average percentage
def fill_employment_percentage(df_share_of_male_female_employment):
    null_index=df_share_of_male_female_employment[df_share_of_male_female_employment['employement_percentage_male'].isnull()][['Entity','Year']].index
    for index in null_index:
        # Getting the null data
        Country=df_share_of_male_female_employment.loc[index,'Entity']
        Year=df_share_of_male_female_employment.loc[index,'Year']

       # Getting that countries average
        new_value_male =df_share_of_male_female_employment[['Entity','employement_percentage_male','employement_percentage_female']].query('Entity == @Country')\
            .groupby(['Entity']).mean()['employement_percentage_male'].iloc[0]
        new_value_female =df_share_of_male_female_employment[['Entity','employement_percentage_male','employement_percentage_female']].query('Entity == @Country')\
            .groupby(['Entity']).mean()['employement_percentage_female'].iloc[0]
        # Adding or substracting from year to be more realistic year affects the percentage
        if (Year<1990):
            new_value_male-=3
            new_value_female-=3
        elif(Year>2000):
            new_value_male+=3
            new_value_female+=3
        # If null getting that year's average
        if math.isnan(new_value_male):
            new_value_male =df_share_of_male_female_employment[['Year','employement_percentage_male','employement_percentage_female']].query('Year ==@Year').\
            groupby('Year').mean()['employement_percentage_male'].iloc[0]
            new_value_female = df_share_of_male_female_employment[['Year','employement_percentage_male','employement_percentage_female']].query('Year ==@Year').\
            groupby('Year').mean()['employement_percentage_female'].iloc[0]
        
        #Filling the null values
        df_share_of_male_female_employment.loc[index,'employement_percentage_male']=round(new_value_male,2)
        df_share_of_male_female_employment.loc[index,'employement_percentage_female']=round(new_value_female,2)

