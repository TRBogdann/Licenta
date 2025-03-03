
def outlier_interval(df,column,k=1.5):
    q1 = df[column].quantile(0.25)
    q3 = df[column].quantile(0.75)
    iqr = q3 - q1
    
    return  q1 - k * iqr, q3 + k * iqr

def remove_outliers(df,column,k=1.5):
    lower_bound, upper_bound = outlier_interval(df,column,k)
    
    return df[(df[column]>=lower_bound) & (df[column]<=upper_bound)]