import pandas as pd
import numpy as np
import folium
from IPython.core.display import HTML

# `helper` module contains all wrapped functions we used to assist our analysis


def view(df,n=5):
    """
    Pretty print pandas dataframe in jupyter notebook.
    """
    tempdf = df.head(n)  # get the first n rows
    display(HTML(tempdf.to_html()))  # display in notebook


def read_data(file_name):
    '''
    Read and preprocess manual count data (drop irrelevant columns and add a new column `name_type`).
    '''
    df = pd.read_csv(file_name,low_memory=False)  # Read the data into a data frame
    # Add a new column: name_type (M,A,B,C,U)
    name_type = list(map(lambda l: l[0],df['road_name']))
    df['name_type'] = name_type
    # drop cols unused in our analysis
    drop_cols = ['region_id','region_name','easting','northing',
             'hgvs_2_rigid_axle','hgvs_3_rigid_axle', 'hgvs_3_or_4_articulated_axle',
             'hgvs_4_or_more_rigid_axle', 'hgvs_5_articulated_axle','hgvs_6_articulated_axle']
    df = df.drop(drop_cols, axis=1)
    return df


def road_info(df):
    '''
    Get columns related to road condition information, dr and seperate them by road types.
    Return major roads data frame and minor roads data frame.
    '''
    road_cols = ['count_point_id','year',
             'road_name','name_type','road_type','local_authority_name',
             'start_junction_road_name','end_junction_road_name',
             'link_length_km','link_length_miles']  # road information cols
    rdf = df[road_cols].drop_duplicates().sort_values(by=['year','count_point_id'])  # all roads data frame
    majors = rdf[rdf['road_type']=='Major'] # major roads data frame
    minors = rdf[rdf['road_type']=='Minor'] # minor roads data frame
    return majors, minors


def road_category(df):
    '''
    Seperate the original dataframe by road categories.
    '''
    # Add new column indicating the road category.
    name_type = list(map(lambda l: l[0],df['road_name']))
    df['name_type'] = name_type

    M_road = df[df['name_type']=='M'] # motorway
    A_road = df[df['name_type']=='A'] # trunk or principal roads
    B_road = df[df['name_type']=='B'] # minor roads
    C_road = df[df['name_type']=='C'] # minor roads, less important than B roads
    U_road = df[df['name_type']=='U'] # unclassified roads

    return M_road, A_road, B_road, C_road, U_road


def cp_info(df):
    '''
    Get columns related to link condition information.
    '''
    cp_cols = ['count_point_id',
             'road_name','name_type',
             'latitude','longitude']  # road information cols
    cpdf = df[cp_cols].drop_duplicates(['count_point_id']).sort_values(by=['count_point_id'])  # all links data frame

    return cpdf


def AADN(df, vehicle_type='all_motor_vehicles', by=None):
    '''
    AADN: annual average daily vehicle number.
    Get the annual average daily observed number of vehicles of certain types vehicles.
    '''

    if by is None:  # sum up directly
        db = df.sort_values(by = 'year').groupby(['year','count_date'])
        db = db[vehicle_type].sum().groupby(['year']).mean()
    
    elif by == 'category':  # sum up by different road categories
        db = df.sort_values(by = 'year').groupby(['year','count_date','name_type'])
        db = db[vehicle_type].sum().groupby(['name_type','year']).mean()

    elif by == 'road':  # sum up by different roads
        db = df.sort_values(by = 'year').groupby(['year','count_date','road_name'])
        db = db[vehicle_type].sum().groupby(['road_name','year']).mean()

    elif by == 'CP':  # sum up by different counting points
        db = df.sort_values(by = 'year').groupby(['year','count_date','count_point_id'])
        db = db[vehicle_type].sum().groupby(['count_point_id','year']).mean()

    return db


def linklen(df,unit='miles'):
    '''
    Caculate the length of all links with data for one certain year.
    '''
    cols = ['count_point_id','year','link_length_km', 'link_length_miles']
    lendf = df[cols].drop_duplicates(['count_point_id','year'])
    if unit == 'miles':
        lendf = lendf.pivot(index='count_point_id',columns='year',values='link_length_miles')
    else:
        lendf = lendf.pivot(index='count_point_id',columns='year',values='link_length_km')
    return lendf


def roadlen(majors,nametype=None):
    '''
    Caculate the length of all roads (of one certain type).
    '''
    df = majors.drop_duplicates(['road_name','count_point_id']).sort_values(by='road_name')
    if nametype is not None:  # if the road category is specified
        df = df[df['name_type']==nametype]  # subset the data for the specified road category
    # compute the road length by summing all of the relevant links
    majorlens = df.groupby(['road_name'])[['link_length_km','link_length_miles']].sum().sort_values(
        by='link_length_km', 
        ascending=False).rename(columns={'link_length_km': 'road_length_km',
                                         'link_length_miles': 'road_length_miles'})
    return majorlens


def TV(df, type='Major'):
    '''
    Calculate the anual traffic volume.
    TV = AADF * link_length * 365
    For major roads, we use AADN to approximate AADF.
    For minor roads (without linklength), we use TV = AADN * 365.
    '''

    if type == 'Major':
        majors = df[df['road_type']=='Major'] # major roads data frame
        aadn_df = AADN(majors,vehicle_type='all_motor_vehicles', by='CP').unstack()
        lendf = linklen(majors, unit='miles')
        merged = pd.concat([aadn_df,lendf])
        tvdf = merged.groupby(['count_point_id']).prod().replace(1,np.nan)*365

    elif type == 'Minor':
        minors = df[df['road_type']=='Minor'] # minor roads data frame
        aadn_df = AADN(minors,vehicle_type='all_motor_vehicles', by='CP').unstack()
        tvdf = aadn_df*365
    
    return tvdf
