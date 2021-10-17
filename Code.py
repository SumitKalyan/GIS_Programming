# Import the required packages and modules
import os
import osgeo.gdal
from qgis.core import *
import processing

# Input the file path for input and output folder along with the shapefile and imagery name
filePathInput = 'C:/Users/sumit/Desktop/Sample_data/'
filePathOutput = 'C:/Users/sumit/Desktop/Sample_data/Output/'
inputRasterName = 'Imagery_Data.tif'
inputVectorName= 'Building_footprint_data.shp'

# First of all, create a new field in attribute table of shapefile and populate it with Unique ID
processing.run("native:addautoincrementalfield", {'INPUT': filePathInput + inputVectorName,'FIELD_NAME':'UniID','START':1,'GROUP_FIELDS':[],'SORT_EXPRESSION':'','SORT_ASCENDING':True,'SORT_NULLS_FIRST':False,'OUTPUT':filePathInput +'Build_ID'})

# Display the output data on the canvas
Building =iface.addVectorLayer(filePathInput+'Build_ID.gpkg','','ogr')

# This bit of code selects each feature in the shapefile and export them in .xml format in the output directory
i = 1
feats_count = Building.featureCount()
for Features in Building.getFeatures():
    if i<=feats_count:
        processing.run("qgis:selectbyattribute", {'INPUT': Building,\
        'FIELD':'UniID','OPERATOR':0,'VALUE':i,'METHOD':0})
        processing.run("native:saveselectedfeatures", {'INPUT':Building,'OUTPUT':filePathOutput +(str(i) + '.xml')})
        i = i + 1
        
# Now, we will clip the imagery for each polygon

# Run the buffer tool by providing the appropriate dictionary 
processing.run("native:buffer", {'INPUT':filePathInput +'Build_ID.gpkg','DISTANCE':15,'SEGMENTS':5,'END_CAP_STYLE':0,'JOIN_STYLE':0,'MITER_LIMIT':2,'DISSOLVE':False,'OUTPUT':filePathInput +'buffer'})

# Run the boundingboxes tool by providing the appropriate dictionary 
processing.run("native:boundingboxes", {'INPUT': filePathInput +'buffer.gpkg' ,'OUTPUT':filePathInput+ 'BuildingExtent'})

# Display the output data on the canvas
BuildingExtent =iface.addVectorLayer(filePathInput+'BuildingExtent.gpkg','','ogr')

# Run a loop to create a saperate vector file for each feature in BuildingExtent layer
suffix = 'temp'
i = 1
for Features in BuildingExtent.getFeatures():
    if i<=feats_count:
        processing.run("qgis:selectbyattribute", {'INPUT': BuildingExtent,\
        'FIELD':'UniID','OPERATOR':0,'VALUE':i,'METHOD':0})
        processing.run("native:saveselectedfeatures", {'INPUT':BuildingExtent,'OUTPUT':filePathInput +(str(i)+suffix)})
        i = i + 1

# Access the input file directory and run a loop to use all the recently created vector files and clip the raster image
for file in os.listdir(filePathInput):
    if file.endswith('temp.gpkg'):
        Output = filePathOutput +(file[:-9] + '.tif')
        processing.run("gdal:cliprasterbymasklayer", {'INPUT':filePathInput+ inputRasterName,'MASK':(filePathInput+file),'SOURCE_CRS':None,'TARGET_CRS':None,'NODATA':None,'ALPHA_BAND':False,'CROP_TO_CUTLINE':True,'KEEP_RESOLUTION':False,'SET_RESOLUTION':False,'X_RESOLUTION':None,'Y_RESOLUTION':None,'MULTITHREADING':False,'OPTIONS':'','DATA_TYPE':0,'EXTRA':'','OUTPUT': Output})

# Remove all the layers from table of content 
root = QgsProject.instance().layerTreeRoot()
root.removeLayer(Building)
root.removeLayer(BuildingExtent)

# Delete all the intermediate layer from the directory
for file in os.listdir(filePathInput):
    if file.endswith('temp.gpkg'):
        os.remove(filePathInput+file)

# Add two samples from the output directory to the canvas
s1 =iface.addRasterLayer(filePathOutput + '1.tif','Output_sample_R1')
s1 =iface.addRasterLayer(filePathOutput + '2.tif','Output_sample_R2')
s2 =iface.addVectorLayer(filePathOutput + '1/1.vrt','Output_sample_V1','ogr')
s2 =iface.addVectorLayer(filePathOutput + '2/2.vrt','Output_sample_V2','ogr')
 
