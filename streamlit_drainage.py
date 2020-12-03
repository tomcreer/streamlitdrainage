#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 16 20:29:57 2020

@author: tommo
"""


import streamlit as st
from streamlit_folium import folium_static
import folium
import geopandas as gpd
import pandas as pd

from streamlit_folium import folium_static
import folium
from pyproj import Transformer
transformer = Transformer.from_crs("epsg:27700", "epsg:4326")

st.markdown(
    f'''
        <style>
            .sidebar .sidebar-content {{
                width: 800px;
            }}
        </style>
    ''',
    unsafe_allow_html=True
)

st.write(
     """
#     Drainage Info from SCANNER survey
#     """
)
#with st.echo():

@st.cache
def load_data():
    gdf_gullies = gpd.read_file('Gulleys Nov 2019/gulleys.shp')
    gdf_gullies.crs = "EPSG:27700"
    def transform_coords(X1,Y1):
        return transformer.transform(X1, Y1)
    
    gdf_gullies.loc[:,'X1'] = gdf_gullies.apply(lambda x: transform_coords(x['POINT_X'],x['POINT_Y'])[0], axis=1)
    gdf_gullies.loc[:,'Y1'] = gdf_gullies.apply(lambda x: transform_coords(x['POINT_X'],x['POINT_Y'])[1], axis=1)
    
    
    gdf_gullies.head()
    df = pd.read_parquet('drainage.parquet')
    df.loc[df['LCRV'] > 200,'LCRV'] = 200
    df.loc[df['LCRV'] < -200,'LCRV'] = -200
    return [df, gdf_gullies]

df, gdf_gullies = load_data()

y = st.sidebar.selectbox("Road:", df['roadcode'].unique(), index=42)

df2 = df[df['roadcode']==y]
selected_chainage = st.slider('Chainage in m', int(df2['cumlength'].min()), int(df2['cumlength'].max()), value=(11670,17000), step=10)
st.write('Selected chainage:', selected_chainage)

df3 = df2[(df2['SECTIONLABEL'] == 'CL1') & (df2['cumlength'] >= selected_chainage[0]) & (df2['cumlength'] <= selected_chainage[1])]
df4 = df2[(df2['SECTIONLABEL'] == 'CR1') & (df2['cumlength'] >= selected_chainage[0]) & (df2['cumlength'] <= selected_chainage[1])]

import mplleaflet
import matplotlib.pyplot as plt
fig, ax = plt.subplots()
kw1 = dict(color='blue', alpha=0.4, scale=1)
q1 = ax.quiver(df3['X1'], df3['Y1'], df3['newU'], df3['newV'], **kw1)
gj1 = mplleaflet.fig_to_geojson(fig=fig)
#TODO - u,v needs to be second component relative to first stop



fig, ax = plt.subplots()
kw2 = dict(color='green', alpha=0.4, scale=1)
q2 = ax.quiver(df4['X1'], df4['Y1'], df4['newU'], df4['newV'], **kw2)
gj2 = mplleaflet.fig_to_geojson(fig=fig)

import folium

feature_group0 = folium.FeatureGroup(name='Left lane')
feature_group1 = folium.FeatureGroup(name='Right lane')

new_coords = [(df3.X1.min()+df3.X1.max())/2, (df3.Y1.min()+df3.Y1.max())/2]



#new_coords = transformer.transform((coords[0]+coords[2])/2,  (coords[1]+coords[3])/2)
#def transform_coords(X1,Y1):
#    return transformer.transform(X1, Y1)

mapa = folium.Map(location=new_coords, tiles="Cartodb Positron",
                  zoom_start=12, prefer_canvas=True)

for feature in gj1['features']:
    if feature['geometry']['type'] == 'Point':
        lat, lon = feature['geometry']['coordinates']
        div = feature['properties']['html']

        icon_anchor = (feature['properties']['anchor_x'],
                       feature['properties']['anchor_y'])

        icon = folium.features.DivIcon(html=div,
                                       icon_anchor=icon_anchor)
        marker = folium.Marker([lat, lon], icon=icon)
        feature_group0.add_child(marker)
    else:
        msg = "Unexpected geometry {}".format
        raise ValueError(msg(feature['geometry']))

for feature in gj2['features']:
    if feature['geometry']['type'] == 'Point':
        lat, lon = feature['geometry']['coordinates']
        div = feature['properties']['html']

        icon_anchor = (feature['properties']['anchor_x'],
                       feature['properties']['anchor_y'])

        icon = folium.features.DivIcon(html=div,
                                       icon_anchor=icon_anchor)
        marker = folium.Marker([lat, lon], icon=icon)
        feature_group1.add_child(marker)
    else:
        msg = "Unexpected geometry {}".format
        raise ValueError(msg(feature['geometry']))
        
        
mapa.add_child(feature_group0)
mapa.add_child(feature_group1)

feature_group2 = folium.FeatureGroup(name='Gullies at recommended spacing', show=False)
def plotDot(point):
    '''input: series that contains a numeric named latitude and a numeric named longitude
    this function creates a CircleMarker and adds it to your this_map'''
    #folium.CircleMarker(location=[point.Y1, point.X1],
    #                    radius=3,
    #                    weight=1).add_to(mapa)
    #folium.Marker([point['X1'], point['Y1']],
    #      #Make color/style changes here
    #      icon = folium.simple_marker(color='lightgray', marker_icon='oil'),
    #      ).add_to(mapa)
    color_map = {'CL1':'blue','CR1':'green'}
    
    folium.Circle( [point['X1'], point['Y1']], radius=2
                     , color=color_map[point['SECTIONLABEL']]
                     , fill_color='lightgray'
                     , fill=True
                     ).add_to(feature_group2)
    
feature_group3 = folium.FeatureGroup(name='Actual gullies', show=False)
def plotGul(point):
    folium.Circle( [point['X1'], point['Y1']], radius=2
                     , color='darkgray'
                     , fill_color='black'
                     , fill=True
                     ).add_to(feature_group3)
    
feature_group4 = folium.FeatureGroup(name='Chainages', show=True)
def plotChain(point):
    
    

    #iframe = folium.IFrame(text, width=700, height=450)
    #popup = folium.Popup(iframe, max_width=3000)
    folium.Marker( [point['X1'], point['Y1']], radius=4
                     , color='black'
                     #, fill_color='#808080'
                     #, fill=True
                     , icon=folium.DivIcon(html=str("<p style='font-family:verdana;color:#bbb;font-size:9px;'>%s</p>" % point['cumlength']))
                     #, popup=str(point['cumlength'])
                     ).add_to(feature_group4)
    
#use df.apply(,axis=1) to "iterate" through every row in your dataframe
df2[df2['gullymarker'] ==1].apply(lambda x: plotDot(x), axis = 1)

df2.iloc[1::20].apply(lambda x: plotChain(x), axis = 1)
#if df3.shape[0] > df4.shape[0]:
#    df3.iloc[1::10].apply(lambda x: plotChain(x), axis = 1)
#else:
#    df4.iloc[1::10].apply(lambda x: plotChain(x), axis = 1)

gdf_gullies.apply(lambda x: plotGul(x), axis = 1)

mapa.add_child(feature_group2)
mapa.add_child(feature_group3)
mapa.add_child(feature_group4)
mapa.add_child(folium.map.LayerControl())
folium_static(mapa)

import matplotlib.pyplot as plt
def plotsir(t, S, I, R, add_text):
  f, ax = plt.subplots(1,1,figsize=(10,4))
  ax.plot(t, S, 'b', alpha=0.7, linewidth=2, label='Crossfall')
  ax.plot(t, I, 'y', alpha=0.7, linewidth=2, label='Gradient')
  #ax.plot(t, R, 'g', alpha=0.7, linewidth=2, label='Radius')

  ax.set_xlabel('Chainage  (m) - ' + add_text)
  ax.set_ylabel('%')  # we already handled the x-label with ax1
  ax2 = ax.twinx()
  color = 'tab:blue'
  ax2.set_ylabel('Radius (m)', color=color)  # we already handled the x-label with ax1
  #ax2.set_yscale("log")
  ax2.plot(t, R, alpha=0.4, color=color,label='Radius')
  ax2.tick_params(axis='y', labelcolor=color)

  ax.yaxis.set_tick_params(length=0)
  ax.xaxis.set_tick_params(length=0)
  ax.grid(b=True, which='major', c='w', lw=2, ls='-')
  legend = ax.legend()
  legend.get_frame().set_alpha(0.5)
  for spine in ('top', 'right', 'bottom', 'left'):
      ax.spines[spine].set_visible(False)
  st.sidebar.pyplot(f)

plotsir(df3['cumlength'], df3['LFAL'], df3['LGRD'], df3['LCRV'], "LEFT LANE")
plotsir(df4['cumlength'], df4['LFAL'], df4['LGRD'], df4['LCRV'], "RIGHT LANE")