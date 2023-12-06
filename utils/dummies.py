import pandas as pd

def __create_dummies(row, unique_features):
    return {element: 1 if element in row else 0 for element in unique_features}

def __dummify_column(df, col_name, unique_features):
    # Check if the specified column contains lists
    if df[col_name].apply(lambda x: isinstance(x, list)).all():
        # If it contains lists, flatten the lists into separate rows
        dummies = df[col_name].apply(lambda x: __create_dummies(x, unique_features)).apply(pd.Series)
    else:
        # Perform one-hot encoding (dummify) on the specified column
        dummies = pd.get_dummies(df[col_name])
        
    dummies.columns = ["F_" + col for col in dummies.columns]
    # Concatenate the dummies with the original DataFrame and drop the original column
    df = pd.concat([df, dummies], axis=1)
    df.drop(columns=[col_name], inplace=True)

    return df

def dummify_columns(df, cols, unique_features):
    df_copy = df
    for col in cols:
        df_copy = __dummify_column(df_copy, col, unique_features)
        
    return df_copy