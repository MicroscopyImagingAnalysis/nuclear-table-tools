"""Dataframe transformations for microscopy feature tables."""

import numpy as np
import pandas as pd

def merge_with_VAE_df(df,vae_df):
    """
    Merge the VAE data with the main dataframe
    """
    # Extract the relevant substring from 'key' in vae_df
    vae_df['key_extracted'] = vae_df['key'].str.split('/').str[-1].str.replace(r'_nuc_.*\.tif$', '', regex=True)
    print(vae_df['key_extracted'])

    # Extract the relevant substring from 'file' in df
    df['file_extracted'] = df['file'].str.split('/').str[-1].str.replace(r'\.nd2$', '', regex=True)
    print(df['file_extracted'])

    # Merge the dataframes based on the specified conditions
    df = pd.merge(
        df,
        vae_df,
        how='inner',
        left_on=['condition', 'batch', 'subbatch', 'label-id', 'file_extracted'],
        right_on=['label', 'batch_label', 'subbatch_label', 'nuc_label', 'key_extracted']
    )

    # Drop the temporary columns used for merging
    df = df.drop(columns=['id', 'file_extracted', 'key_extracted'])
    return df


def filter_dataframe(inp_df, second_df, metadata_cols,image_mode='2D',
                     hull_col='DAPI_hull_calc',
                      hull2d_col='DAPI_2dhull_calc',
                        peak_col='DAPI_peak_count'):
    # Separate metadata columns from the rest
    df = inp_df.copy()

    metadata_cols = [col for col in metadata_cols + [hull_col, hull2d_col, peak_col] if col in df.columns]
    df_data = df.drop(columns=metadata_cols)
    df_metadata = df.loc[:, df.columns.intersection(metadata_cols)]

    # print(df_metadata.columns)


    # Drop rows from df_data where either sph_2dhull_calc = 0 (for 2D) or sph_hull_calc = 0 (for 3D)
    if image_mode == '2D':
        df_data = df_data[df_metadata[hull2d_col] == 1]
        df_metadata = df_metadata[df_metadata[hull2d_col] == 1]
    elif image_mode == '3D':
        df_data = df_data[df_metadata[hull_col] == 1]
        df_metadata = df_metadata[df_metadata[hull_col] == 1]

    # Drop hull_col and hull2d_col if they exist in the dataframe
    df = df.drop(columns=[col for col in [hull_col, hull2d_col] if col in df.columns])
    # at least one peak
    df_data = df_data[df_metadata[peak_col] > 0]
    df_metadata = df_metadata[df_metadata.index.isin(df_data.index)]


    # df_data = df_data[(df_data['size'] > 400) & (df_data['size'] < 1000)]
    # df_metadata = df_metadata[df_metadata.index.isin(df_data.index)]


    print("hull and peak filtered",df_data.shape)
    ## removing columns with more than 10% nan values
    # Calculate the threshold for columns
    threshold_col = 0.1 * len(df_data)

    nan_columns = df_data.columns[df_data.isna().any()]
    nan_counts = df_data[nan_columns].isna().sum()

    # Loop over columns in nan_columns
    for col in nan_columns:
        if nan_counts[col] > threshold_col:
            df_data.drop(columns=[col], inplace=True)
        else:
            rows_to_drop = df_data[df_data[col].isna()].index
            df_data.drop(index=rows_to_drop, inplace=True)
            df_metadata.drop(index=rows_to_drop, inplace=True)

    # Check for columns with inf entries
    inf_columns = df_data.columns[np.isinf(df_data).any()]
    inf_counts = df_data[inf_columns].isin([np.inf, -np.inf]).sum()

    # Loop over columns with inf entries
    for col in inf_columns:
        if inf_counts[col] > threshold_col:
            df_data.drop(columns=[col], inplace=True)
        else:
            rows_to_drop = df_data[df_data[col].isin([np.inf, -np.inf])].index
            df_data.drop(index=rows_to_drop, inplace=True)
            df_metadata.drop(index=rows_to_drop, inplace=True)

    # Drop columns with standard deviation = 0
    zero_std_cols = df_data.columns[(df_data.std()/df_data.mean() < 0.05) | (df_data.std() == 0)]
    print("zero std cols",zero_std_cols)
    df_data.drop(columns=zero_std_cols, inplace=True)

    # Ensure crop_df only retains rows matching those in the final df_data
    if second_df is not None:
        crop_df = second_df.copy()
        crop_df = crop_df.loc[df_data.index]


    print("zero std",zero_std_cols)
    df_filtered = pd.concat([df_metadata, df_data], axis=1)
    print(df_filtered.values.shape)


    del df
    if second_df is not None:
        return df_filtered, crop_df
    else:
        return df_filtered, None


def drop_high_corr_columns(df,feature_cols, corr_threshold):
    # Calculate the correlation matrix for feature columns only
    corr_matrix = df[feature_cols].corr().abs()

    # Create a set to hold the columns to drop
    cols_to_drop = set()

    # Iterate over the columns of the correlation matrix
    for i in range(len(corr_matrix.columns)):
        for j in range(i + 1, len(corr_matrix.columns)):
            if corr_matrix.iloc[i, j] > corr_threshold:
                colname = corr_matrix.columns[j]
                print("highly correlated",corr_matrix.columns[i],colname)
                if colname not in cols_to_drop:
                    cols_to_drop.add(colname)

    # Drop the columns from the dataframe
    df.drop(columns=cols_to_drop, inplace=True)

    print(f"Dropped columns due to high correlation: {cols_to_drop}")

    return df


def drop_low_unique_columns(df,feature_cols, unique_threshold):
    # Calculate the number of unique values for each feature column
    unique_counts = df[feature_cols].nunique()

    # Create a set to hold the columns to drop
    cols_to_drop = set()

    # Iterate over the unique counts and check against the threshold
    for col, count in unique_counts.items():
        if count < unique_threshold:
            cols_to_drop.add(col)

    # Drop the columns from the dataframe
    df.drop(columns=cols_to_drop, inplace=True)

    print(f"Dropped columns due to low uniqueness: {cols_to_drop}")

    return df


def drop_high_corr_columns_marker(df,feature_cols, corr_threshold):
    # Calculate the correlation matrix for feature columns only
    corr_matrix = df[feature_cols].corr().abs()

    # Create a set to hold the columns to drop
    cols_to_drop = set()

    # Iterate over the columns of the correlation matrix
    for i in range(len(corr_matrix.columns)):
        for j in range(i + 1, len(corr_matrix.columns)):
            if corr_matrix.iloc[i, j] > corr_threshold:
                colname = corr_matrix.columns[j]
                print("highly correlated",corr_matrix.columns[i],colname)
                if colname not in cols_to_drop and 'mean' not in colname and 'median' not in colname:
                    cols_to_drop.add(colname)

    # Drop the columns from the dataframe
    df.drop(columns=cols_to_drop, inplace=True)

    print(f"Dropped columns due to high correlation: {cols_to_drop}")

    return df


__all__ = [
    "merge_with_VAE_df",
    "filter_dataframe",
    "drop_high_corr_columns",
    "drop_high_corr_columns_marker",
    "drop_low_unique_columns",
]
