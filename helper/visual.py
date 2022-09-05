import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import folium
import helper.data as dt


def counter_stat(df):
    '''
    Compute how many counting points were set by road types each year.
    Make a stacked bar plot to show the trend change.
    '''
    majors, minors = dt.road_info(df)  # get road information df
    m_grouped = majors.groupby(['year'])  # major roads df group by year
    n_grouped = minors.groupby(['year'])  # minor roads df group by year
    # compute the number of counting points for different type roads each year
    m_cpnb = m_grouped[['count_point_id']].nunique().transpose().rename(index={'count_point_id': 'Major'})
    n_cpnb = n_grouped[['count_point_id']].nunique().transpose().rename(index={'count_point_id': 'Minor'})
    cpdf = pd.concat([m_cpnb, n_cpnb])  # concatenate the two df
    # make stacked bar plot
    ax = cpdf.transpose().plot.bar(stacked=True, rot=30, color=['skyblue','steelblue'], figsize = [18,5], 
                                   title='How many counting points were set each year?')
    # add annotation
    for p in ax.patches:
        width, height = p.get_width(), p.get_height()
        x, y = p.get_xy() 
        ax.text(x+width/2, 
                y+height/2, 
                '{:.0f}'.format(height), 
                horizontalalignment='center', 
                verticalalignment='center')
    
    return cpdf


def AADN_cat(df):
    '''
    Visualize the annual average daily vehicle number statistics by road categories.
    '''
    plt.figure(figsize = [14,10])  # set figure size
    title = ['M Road','A Road','B Road','C Road','U Road']
    roadls = dt.road_category(df)  # M_road, A_road, B_road, C_road, U_road 
    # subplot 1: statistic for all motor vehicles
    plt.subplot(211)
    i = 0  # iteration counter
    for road in roadls:  # loop over each road category
        i += 1
        # plot the annual daily vehicle number for the current road category
        db = dt.AADN(road)
        plt.plot(db.index, db.values, 'o-', label = title[i-1])
        plt.ylabel('vehicles number')
    # annotate missing values for M-roads between 2009-2014
    plt.annotate('missing values',
                xy=(2012,10**5), xycoords='data',
                xytext=(50, -30), textcoords='offset points',
                arrowprops=dict(facecolor='black', shrink=0.05),
                horizontalalignment='right', verticalalignment='top')
    # plot setting
    plt.xticks(np.arange(2000, 2020, step=2),size='medium')
    plt.yscale('log')
    plt.ylim(10**3,2*10**5)
    plt.legend(loc=2, bbox_to_anchor=(1.05,1.0),borderaxespad = 0.)  # put legend outside plot matplotlib
    plt.title('Annual average daily observed number of all motor vehicles')

    # subplot 2: statistic for pedal cycles
    plt.subplot(212)
    i = 0  # iteration counter
    for road in roadls:
        i += 1
        # plot the annual daily vehicle number for the current road category
        db = dt.AADN(road, vehicle_type = 'pedal_cycles')
        plt.plot(db.index, db.values, 'o-', label = title[i-1])
        plt.ylabel('vehicles number')
    # plot setting
    plt.xticks(np.arange(2000, 2020, step=2),size='medium')
    plt.legend(loc=2, bbox_to_anchor=(1.05,1.0),borderaxespad = 0.)
    plt.title('Annual average daily observed number of pedal cycles')


def AADN_veh(df,logscale=False):
    '''
    Visualize the annual average daily vehicle number statistics by vehicle types.
    '''
    plt.figure(figsize = [14,5])  # set figure size
    title = ['pedal cycles','motor cycles','cars & taxis','buses & coaches','lgvs','hgvs','all motor vehicles']
    vehls = ['pedal_cycles','two_wheeled_motor_vehicles',
             'cars_and_taxis','buses_and_coaches','lgvs','all_hgvs','all_motor_vehicles']
    for i in range(len(title)):  # loop over each road category
        # plot the annual daily vehicle number for the current vehicle type
        db = dt.AADN(df, vehicle_type = vehls[i])
        plt.plot(db.index, db.values, 'o-', label = title[i])
        plt.ylabel('vehicles number')
    # plot setting
    plt.xticks(np.arange(2000, 2020, step=2),size='medium')
    if logscale:
        plt.yscale('log')
    plt.legend(loc=2, bbox_to_anchor=(1.05,1.0),borderaxespad = 0.)
    plt.title('Annual average daily observed number by vehicle type')


def counterloc(df, idls):
    '''
    Draw counters on the map
    '''
    temp = dt.cp_info(df).set_index('count_point_id')

    # create the map
    mpp = folium.Map(location=[55.9,-3.7], zoom_start=9)

    for cpid in idls:
        folium.Marker([temp.loc[cpid,"latitude"],temp.loc[cpid,"longitude"]], 
                    popup=(f'{temp.loc[cpid,"road_name"]}')).add_to(mpp)

    # when clicking on the map, latitude and longitude may show
    mpp.add_child(folium.LatLngPopup())

    return mpp


def TV_stat(df):
    majors = df[df['road_type']=='Major']
    minors = df[df['road_type']=='Minor']
    
    mtemp = dt.TV(majors).apply(lambda col: np.mean(col[~np.isnan(col)]), axis=0)
    ntemp = dt.TV(minors,type='Minor').apply(lambda col: np.mean(col[~np.isnan(col)]), axis=0)

    mtemp.name = 'Major'
    ntemp.name = 'Minor'
    xtk=[int(2000+i) for i in range(20)]
    pd.concat([mtemp,ntemp],axis=1).plot.line(logy=True,rot=30,figsize=[14,5],xticks=xtk,
                                        title='Annual traffic volume estimation')
    
    return mtemp,ntemp


def AADN_veh_pie(df, year):
    '''
    Find out the ditribution of the different types of vehicles on an average day of a certain year.
    Make pie plot to show the proportion of the different types of vehicles.
    '''
    vehls = ['pedal_cycles','two_wheeled_motor_vehicles',
                'cars_and_taxis','buses_and_coaches','lgvs','all_hgvs']
    title = ['pedal cycles','motor cycles','cars & taxis','buses & coaches','lgvs','hgvs']
    perc_yr = dt.AADN(df,vehicle_type=vehls).loc[year,].to_frame()
    ax = perc_yr.plot.pie(y=year, figsize=[6,6],labels=['','','','','',''],fontsize=16)
    plt.legend(loc=2, bbox_to_anchor=(1.05,1.0),borderaxespad = 0.,labels = title)
    plt.show()

    return perc_yr