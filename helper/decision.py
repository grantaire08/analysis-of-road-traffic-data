import folium
import pandas as pd

def weighted_average_method(df):
    '''
    Calculate average number of vehicles travelling per day in a given year (aadf) by weighted average method
    Two parts are considered seperately, major roads and minor roads
    The influence of data in the past 20 years are decided by weighted average method 
    and how many data are used can be controled 
    If we choose to use 2-year data, the aadf=1/(1+2)*aadf[2018]+2/(1+2)*aadf[2019]
    If we choose to use 3-year data, the aadf=1/(1+2+3)*aadf[2017]+2/(1+2+3)*aadf[2018]+3/(1+2+3)*aadf[2019]
    ...
    It returns two dataframe, dfmajor_aadf is the aadf calculated on major roads, 
    while dfminor_aadf is the aadf calculated on minor roads
    '''
    df = df[["count_point_id","direction_of_travel","year","count_date","hour",
             "all_motor_vehicles","name_type","road_type","road_name","latitude","longitude"]]

    # consider the major road and minor road respectively
    df_major = df[df["road_type"] == "Major"]
    df_minor = df[df["road_type"] == "Minor"]
    
    # consider different directions, dates, hours
    # df_aadf is average number of vehicles travelling per day in a given year
    dfmajor_direction = df_major.groupby(["count_point_id","year","count_date","hour"])["all_motor_vehicles"].sum()
    dfmajor_hour = dfmajor_direction.groupby(["count_point_id","year","count_date"]).sum()
    dfmajor_aadf = dfmajor_hour.groupby(["count_point_id","year"]).mean()
    dfmajor_aadf = dfmajor_aadf.unstack().fillna(0).astype(int)
    dfmajor_aadf = pd.DataFrame(dfmajor_aadf).reset_index()

    dfminor_direction = df_minor.groupby(["count_point_id","year","count_date","hour"])["all_motor_vehicles"].sum()
    dfminor_hour = dfminor_direction.groupby(["count_point_id","year","count_date"]).sum()
    dfminor_aadf = dfminor_hour.groupby(["count_point_id","year"]).mean()
    dfminor_aadf = dfminor_aadf.unstack().fillna(0).astype(int)
    dfminor_aadf = pd.DataFrame(dfminor_aadf).reset_index()
    
    # add a column to save the aadf calculated
    dfmajor_aadf["inf"]=[0 for index in range(len(dfmajor_aadf))]
    dfminor_aadf["inf"]=[0 for index in range(len(dfminor_aadf))]

    y = int(input("How many years of statistics are taken into consideration (an integer less than or equal to 20): "))
    while y>20 :
        print("Only 20 years of statistics are available, so your input should less than or equal to 20!")
        print("Please input again!")
        y = int(input("How many years of statistics are taken into consideration (an integer less than or equal to 20): "))
    s = 0
    # weighted_average_method
    for n in range(1,y+1):
        s = s + n
    for i in range(1,y+1):
        dfmajor_aadf["inf"] = dfmajor_aadf["inf"] + dfmajor_aadf[2020-i] * (y+1-i)/s
        dfminor_aadf["inf"] = dfminor_aadf["inf"] + dfminor_aadf[2020-i] * (y+1-i)/s

    dfmajor_aadf = dfmajor_aadf[["count_point_id","inf"]].sort_values(by="inf",ascending=False)
    dfminor_aadf = dfminor_aadf[["count_point_id","inf"]].sort_values(by="inf",ascending=False)
    # df_join is used to add nametype,latitude and longitude to dfmajor_aadf and dfminor_aadf 
    # it is helpful when plotting maps
    df_join = df[["count_point_id","name_type","road_name",
                      "latitude","longitude"]].drop_duplicates(["count_point_id"])
    dfmajor_aadf = pd.merge(dfmajor_aadf,df_join,how="left",on="count_point_id")
    dfminor_aadf = pd.merge(dfminor_aadf,df_join,how="left",on="count_point_id")
    
    return dfmajor_aadf, dfminor_aadf

def show_counters(dfmajor_aadf, dfminor_aadf):
    '''
    Shows the locations (latitude and longitude) of the counting points where should be set counters
    How many counters set on major roads and minor roads can be controled manually. 
    '''
    countermajor = int(input("how many counters are set on major road: "))
    counterminor = int(input("how many counters are set on minor road: "))
    
    # the buziest major and minor roads
    cmajor = dfmajor_aadf.iloc[:countermajor]
    cminor = dfminor_aadf.iloc[:counterminor]

    print("the counters on major roads should be set at: ")
    print(cmajor[["latitude","longitude"]])
    print("\n")
    print("the counters on minor roads should be set at: ")
    print(cminor[["latitude","longitude"]])
    
    return cmajor, cminor
        
def plot_map(cmajor, cminor):
    '''
    Plot the counters on the map
    '''
    # create the map
    m = folium.Map(location=[55.9,-3.7],
               zoom_start=9)

    # mark the busiest counting points on major roads
    for i in range(len(cmajor)):
        folium.Marker([cmajor.loc[i,"latitude"],cmajor.loc[i,"longitude"]], popup="road: "+cmajor.loc[i,"road_name"]+"\n"+"latitude: "+str(round(cmajor.loc[i,"latitude"],4))+"\n"+"longitude: "+str(round(cmajor.loc[i,"longitude"],4)),icon=folium.Icon(color='green')).add_to(m)

    # mark the busiest counting points on minor roads
    for i in range(len(cminor)):
        folium.Marker([cminor.loc[i,"latitude"],cminor.loc[i,"longitude"]], popup="road: "+cminor.loc[i,"road_name"]+"\n"+"latitude: "+str(round(cminor.loc[i,"latitude"],4))+"\n"+"longitude: "+str(round(cminor.loc[i,"longitude"],4)),icon=folium.Icon(color='blue')).add_to(m)
    
    # when clicking on the map, latitude and longitude may show
    m.add_child(folium.LatLngPopup())

    return m
    
def show_counters_M8(dfmajor_aadf):
    '''
    Shows the locations (latitude and longitude) of the counting points on road M8 where should be set counters
    How many counters set on road M8 can be controled manually. 
    '''
    # create the map
    m8 = folium.Map(location=[55.86,-4.23],
               zoom_start=10)
    # only consider the road "M8"
    M_8 = dfmajor_aadf[dfmajor_aadf["road_name"] == "M8"].reset_index().drop(columns="index")
    c8 = int(input("how many counters are set on road M8: "))
    c_8 = M_8.iloc[:c8]

    print("The counters on the major roads should be set at:")
    print(c_8[["latitude","longitude"]])

    # mark the busiest counting points on M8 roads
    for i in range(c8):
        folium.Marker([c_8.loc[i,"latitude"],c_8.loc[i,"longitude"]], popup="latitude: "+str(round(c_8.loc[i,"latitude"],4))+"\n"+"longitude: "+str(round(c_8.loc[i,"longitude"],4)),icon=folium.Icon(color='green')).add_to(m8)

    # when clicking on the map, latitude and longitude may show
    m8.add_child(folium.LatLngPopup())

    return m8