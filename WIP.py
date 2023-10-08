import pandas as pd

hmf_series = pd.read_csv('spreadsheets/hmf_series.csv')

def calc_intra_annual(hmf_series: pd.Series, hydro_year: str):
    """Calculates the number of HMF events per hydrological year (consecutive days count as one event)"""
    
    # Offsetting dates to make calculations easier (currently HARDCODED)
    date_series = pd.to_datetime(hmf_series['datetime'])        
    date_series = date_series + pd.DateOffset(months=-9)
    
    df = pd.DataFrame(columns=['Year'])
    
    for i in range(len(date_series)):
        if i == 0:   
            df = pd.concat([df, pd.DataFrame({'Year': date_series.iloc[i].year}, index=[i])], ignore_index=True, axis=0)                          
        else:
            if (date_series.iloc[i] - date_series.iloc[i - 1]).days > 1:
                df = pd.concat([df, pd.DataFrame({'Year': date_series.iloc[i].year}, index=[i])], ignore_index=True, axis=0)
    
    df = df.groupby('Year').size().reset_index(name='hmf_events')
    print(df['hmf_events'].sum() / 28)
    print(df)
    return
            

calc_intra_annual(hmf_series, 'AS-OCT')


'''for i in range(len(date_series)):
    if i == 0: # First date
        if (date_series.iloc[i+1] - date_series.iloc[i]).days != 1:
            one_day_peaks.append(date_series.iloc[i])
    elif i == (len(date_series) - 1): # Last date
        if (date_series.iloc[i] - date_series.iloc[i - 1]).days != 1:
            one_day_peaks.append(date_series.iloc[i])
    else: # All other dates
        if ((date_series.iloc[i+1] - date_series.iloc[i]).days != 1 and 
            (date_series.iloc[i] - date_series.iloc[i - 1]).days != 1):
            one_day_peaks.append(date_series.iloc[i])'''
            
'''for i in range(len(date_series)):
    if (date_series.iloc[i] - curr_year)'''