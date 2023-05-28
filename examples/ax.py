import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import matplotlib.ticker as mticker
import cartopy.io.shapereader as shpreader
import cartopy.feature as cfeature
import numpy as np
import geopandas as gpd
import copy
from scipy.stats import mannwhitneyu
import string
letters = string.ascii_lowercase

projection = ccrs.LambertConformal(central_longitude=-96, central_latitude=37.5, standard_parallels=(29.5, 45.5))

extents = {'ECONUS': [-108, -73.5, 24.5, 52]}

long_range = {'ECONUS': [-110, -100, -90, -80, -70]}


def draw_geography(ax):
        
    countries_shp = shpreader.natural_earth(resolution='50m',
                                     category='cultural',
                                     name='admin_0_countries')
    
    for country, info in zip(shpreader.Reader(countries_shp).geometries(), 
                             shpreader.Reader(countries_shp).records()):
        if info.attributes['NAME_LONG'] != 'United States':

            ax.add_geometries([country], ccrs.PlateCarree(),
                             facecolor='Grey', edgecolor='k', zorder=6)
            
    lakes_shp = shpreader.natural_earth(resolution='50m',
                                     category='physical',
                                     name='lakes')
    
    for lake, info in zip(shpreader.Reader(lakes_shp).geometries(), 
                             shpreader.Reader(lakes_shp).records()):

        name = info.attributes['name']
        if name == 'Lake Superior' or name == 'Lake Michigan' or \
           name == 'Lake Huron' or name == 'Lake Erie' or name == 'Lake Ontario':
            
            ax.add_geometries([lake], ccrs.PlateCarree(),
                              facecolor='lightsteelblue', edgecolor='k', zorder=6)
            
    ax.add_feature(cfeature.NaturalEarthFeature('physical', 'ocean', '50m', edgecolor='face', 
                                                facecolor='lightsteelblue'), zorder=6)

    ax.add_feature(cfeature.NaturalEarthFeature('physical', 'coastline', '50m', edgecolor='face', 
                                                facecolor='None'), zorder=6) 
    
    shapename = 'admin_1_states_provinces_lakes'
    states_shp = shpreader.natural_earth(resolution='50m',
                                     category='cultural', name=shapename)
                                     
    for state, info in zip(shpreader.Reader(states_shp).geometries(), shpreader.Reader(states_shp).records()):
        if info.attributes['admin'] == 'United States of America':

            ax.add_geometries([state], ccrs.PlateCarree(),
                              facecolor='grey', edgecolor='k')
            
    for state, info in zip(shpreader.Reader(states_shp).geometries(), shpreader.Reader(states_shp).records()):
        if info.attributes['admin'] == 'United States of America':

            ax.add_geometries([state], ccrs.PlateCarree(),
                              facecolor='None', edgecolor='k', zorder=6)

    return ax


def setup_map(num, rows, cols, label_num, extent='ECONUS', longitudes='ECONUS', panel_label=True):
    
    #figure_idx = col_idx + (row_idx * cols)
    
    ax = plt.subplot(rows, cols, num, projection=projection)

    ax.set_extent(extents[extent])

    ax = draw_geography(ax)

    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, dms=True, x_inline=False, y_inline=False, zorder=10,
                      color='k', alpha=0.5)

    gl.top_labels = False

    gl.right_labels = False

    gl.xlocator = mticker.FixedLocator(long_range[longitudes])

    gl.xlabel_style = {'size': 20, 'color': 'k', 'rotation': 0.01}
    gl.ylabel_style = {'size': 20, 'color': 'k'}
    
    if panel_label:
    
        ax.annotate("{})".format(letters[label_num-1]), (-.06,1), xycoords='axes fraction',
                    fontsize=26, bbox=dict(boxstyle='round', facecolor='w', alpha=1), 
                    color='k', zorder=25)

    return ax
    
def draw_outlines(ax):
    
    usa = gpd.read_file("../data/CONUS.shp")
    
    quadrants = {'NP': {'states': ['NE', 'SD', 'ND'], 
                    'ax_label': 'i.'},
                 'SP': {'states': ['TX', 'OK', 'KS'], 
                        'ax_label': 'ii.'},
                 'MW': {'states': ['WI', 'MI', 'OH', 
                                   'IL', 'IN', 'MN', 
                                   'IA', 'MO', 'KY'], 
                        'ax_label': 'iii.'},
                 'SE': {'states': ['AR', 'LA', 'TN', 
                                   'MS', 'AL', 'SC', 
                                   'NC', 'FL', 'GA'], 
                        'ax_label': 'iv.'},
                 'NE': {'states': ['NJ', 'PA', 'NY', 
                                   'VT', 'NH', 'CT', 
                                   'VA', 'WV', 'MD', 
                                   'DC', 'DE', 'RI', 
                                   'MA', 'ME'], 
                        'ax_label': 'v.'}}

    for qid, quad_info in quadrants.items():

        usa_dis = usa[usa.STUSPS.isin(quad_info['states'])]
        usa_dis = copy.deepcopy(usa_dis.dissolve())

        ctr = usa_dis.to_crs('ESRI:102004').centroid.to_crs('EPSG:4269')

        ax.add_geometries(usa_dis.geometry.values, crs=ccrs.PlateCarree(), 
                          linewidths=5, facecolor='None', zorder=15)

        ax.text(float(ctr.x)-2.5, float(ctr.y), quad_info['ax_label'], 
                transform=ccrs.PlateCarree(), fontsize=25, zorder=15)
                
                
def grid_significance(ds1, ds2, expected_dims=(15, 44, 69)):
    r"""Performs a grid-to-grid significance test on ds1 and ds2.
    Returns a grid of the same size with p-values from the Mann
    Whitney U test.
    
    Parameters
    ----------
    ds1: (t, y, x) ndarray
        An ndarray in the format of (time, y, x) and shape of expected_dims. 
    ds2: (t, y, x) ndarray
        An ndarray in the format of (time, y, x) and shape of expected_dims.  
    expected_dims: tuple
        The expected shape of ds1 and ds2. Default is (15, 44, 69).
    Returns
    -------
    results: (y, x) ndarray
        Results of significance testing in the form of p-values.
    """    
    
    if ds1.shape == expected_dims and ds2.shape == expected_dims:
        #Since zeros would be < 0.05
        results = np.ones(shape=(ds1.shape[1], ds1.shape[2]), dtype=float)

        for i in range(ds1.shape[1]):
            for j in range(ds1.shape[2]):

                ds1_dist = ds1[:, i, j]
                ds2_dist = ds2[:, i, j]

                if np.mean(ds1_dist > 0) or np.mean(ds2_dist > 0):

                    s, p = mannwhitneyu(ds1_dist, ds2_dist)
                    results[i, j] = p

        return results
    
    else:
        
        raise ValueError("Dimensions are not as expected, given", ds1.shape, "expected", expected_dims)