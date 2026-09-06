"""Load and prepare paired nuclear and spheroid feature tables."""

import os

import pandas as pd

from .transforms import (
    drop_high_corr_columns_marker as drop_high_corr_columns,
    drop_low_unique_columns,
    filter_dataframe,
)

def dfs_from_path(path,type='mcf7a',has2d=False):

    if type == 'mcf7a':
        if has2d:
            nuc_file_2d = os.path.join(path, '2d_nuc_data.csv')
            sph_file_2d = os.path.join(path, '2d_spheroid_data.csv')

        nuc_file = os.path.join(path, 'nuc_data.csv')
        sph_file = os.path.join(path, 'spheroid_data.csv')

    elif type == 'mcf10a':
        if has2d:
            nuc_file_2d = os.path.join(path, '2d_nuc_data.csv')
            sph_file_2d = os.path.join(path, '2d_spheroid_data.csv')

        nuc_file = os.path.join(path, 'nuc_data.csv')
        sph_file = os.path.join(path, 'spheroid_data.csv')

    if has2d:
        nuc_df_2d = pd.read_csv(nuc_file_2d)
        sph_df_2d = pd.read_csv(sph_file_2d)
    else:
        nuc_df_2d = pd.DataFrame()
        sph_df_2d = pd.DataFrame()
    nuc_df = pd.read_csv(nuc_file)
    sph_df = pd.read_csv(sph_file)

    print(nuc_df_2d.shape, sph_df_2d.shape)
    print(nuc_df.shape, sph_df.shape)

    meta_cols = [col for col in nuc_df.columns if not col.startswith('DAPI') and not col.startswith('chan')]

    # for col in nuc_df.columns:
        # print(col)

    print(meta_cols)
    meta_cols.extend(['chan1','chan1_type','chan2','chan2_type','chan3','chan3_type'])
    print(len(nuc_df.columns),len(meta_cols))
    print(meta_cols)




    glob_nuc_df, _ = filter_dataframe(nuc_df, None, meta_cols, image_mode='3D',
                                hull_col='DAPI_hull_calc',
                                hull2d_col='DAPI_2dhull_calc',
                                peak_col='DAPI_peak_count')

    # print("all cols",glob_nuc_df.columns)
    print("chan cols",[col for col in glob_nuc_df.columns if col.startswith('chan')])
    feature_cols = [ col for col in glob_nuc_df.columns if col.startswith('DAPI_') or col.startswith('chan') and
                    col not in ['DAPI_hull_calc', 'DAPI_2dhull_calc', 'DAPI_peak_count'] and col not in meta_cols]
    print("original feature cols:", feature_cols)
    dapi_cols = [col for col in feature_cols if col.startswith('DAPI_')]
    print(feature_cols)
    glob_nuc_df = drop_high_corr_columns(glob_nuc_df, dapi_cols, 0.95)
    print(glob_nuc_df)
    feature_cols = [ col for col in glob_nuc_df.columns if col.startswith('DAPI_') or col.startswith('chan') and
                    col not in ['DAPI_hull_calc', 'DAPI_2dhull_calc', 'DAPI_peak_count'] and col not in meta_cols]

    glob_nuc_df = drop_low_unique_columns(glob_nuc_df, feature_cols, 10)

    print(feature_cols)
    filt_feature_cols = [col for col in feature_cols if col in glob_nuc_df.columns]

    print(filt_feature_cols)
    print(glob_nuc_df)

    # glob_nuc_df['condition'] = glob_nuc_df['condition'].replace({'Day9': 'Day8', 'Day12GEL': 'Day10(Gel)',
                                                                #   'Day12': 'Day10(Gel)'})



    if has2d:
        glob_nuc_df_2d, _ = filter_dataframe(nuc_df_2d, None, meta_cols, image_mode='2D',
                                hull_col='DAPI_hull_calc',
                                hull2d_col='DAPI_2dhull_calc',
                                peak_col='DAPI_peak_count')


        feature_cols_2d = [ col for col in glob_nuc_df_2d.columns if col.startswith('DAPI_') or col.startswith('chan') and
                    col not in ['DAPI_hull_calc', 'DAPI_2dhull_calc', 'DAPI_peak_count'] and col not in meta_cols]

        dapi_cols_2d = [col for col in feature_cols_2d if col.startswith('DAPI_')]
        print(feature_cols_2d)
        glob_nuc_df_2d = drop_high_corr_columns(glob_nuc_df_2d, dapi_cols_2d, 0.95)
        print(glob_nuc_df_2d)
        feature_cols_2d = [ col for col in glob_nuc_df_2d.columns if col.startswith('DAPI_') or col.startswith('chan') and
                        col not in ['DAPI_hull_calc', 'DAPI_2dhull_calc', 'DAPI_peak_count'] and col not in meta_cols]

        glob_nuc_df_2d = drop_low_unique_columns(glob_nuc_df_2d, feature_cols_2d, 10)


        filt_feature_cols_2d = [col for col in feature_cols_2d if col in glob_nuc_df_2d.columns]
        print(glob_nuc_df_2d)

        glob_nuc_df_2d['condition'] = glob_nuc_df_2d['condition'].replace({'Day9': 'Day8', 'Day12GEL': 'Day10(Gel)'})

    else:
        glob_nuc_df_2d = pd.DataFrame()
        filt_feature_cols_2d = []
        print(glob_nuc_df_2d)

    return meta_cols,glob_nuc_df, glob_nuc_df_2d, filt_feature_cols, filt_feature_cols_2d


__all__ = ["dfs_from_path"]
