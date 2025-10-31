# Create an "Output" Folder with three sub folder as "IDW", "Minus" and "Reclass"

import arcpy
from arcpy.sa import *
import glob
import os

arcpy.env.overwriteOutput = True

# User Input (Point Shape file path)
points_shape_path = r'G:\MJI\SKZ\Script\IDW\shape_file\*.shp'

# User Input (Masking Shape file path)
barrier_shp = r'G:\MJI\SKZ\Script\IDW\Boundary\Polder_boundary.shp'

# User Input (Insert output folder path)
path = r'G:\MJI\SKZ\Script\IDW\test_output'

# User Input (Insert DEM to be subtracted with path and file extension [tif format is preferable])
DEM_raster = r'G:\MJI\SKZ\Script\IDW\Boundary\lddemcc2100.tif'

# Extent of IDW raster (Insert the 4 extreme points just like perfoming IDW manually in ArcMap)
extent = "581004.417807 497245.587088 607359.920697 523226.093088"


IDW_path = os.path.join(path, 'IDW')
# os.mkdir(IDW_path)

minus_path = os.path.join(path, 'Minus')
# os.mkdir(minus_path)

reclass_path = os.path.join(path, 'Reclass')
# os.mkdir(reclass_path)


barrier_lyr = arcpy.MakeFeatureLayer_management(barrier_shp, 'mask_layer')

for shp_file in glob.glob(points_shape_path):

    point_shp = shp_file
    name2 = os.path.split(shp_file)
    name1 = name2[-1].split('.shp')
    name = name1[0]


# IDW Raster

    layer_name = "{}_layer".format(name)
    input_feature = arcpy.MakeFeatureLayer_management(point_shp, layer_name)
    z_field = 'WL_mPWD'
    cell_size = 25
    power = 2

    arcpy.CheckOutExtension("Spatial")

    # Set the extent environment using a keyword
    arcpy.env.extent = "MAXOF"

    # Set the extent environment using a space-delimited string
    arcpy.env.extent = extent

    outIDW = Idw(layer_name, z_field, cell_size, power, 'mask_layer')
    outExtractByMask = ExtractByMask(outIDW, barrier_shp)
    out_file_name = os.path.join(IDW_path, 'IDW_{}.tif'.format(name))
    outExtractByMask.save(out_file_name)


# Raster Minus

    in_raster = arcpy.MakeRasterLayer_management(outExtractByMask, 'in_raster')
    topo_raster = arcpy.MakeRasterLayer_management(DEM_raster, 'DEM')

    outMinus = Minus('in_raster', 'DEM')

    minus_raster_name = os.path.join(minus_path, 'WD_{}.tif'.format(name))

    outMinus.save(minus_raster_name)


# Reclassify Raster

    raster_layer = arcpy.MakeRasterLayer_management(outMinus, 'minus_raster')

    re_class = RemapRange([[-10, 0, 1], [0, 0.3, 2], [0.3, 0.9, 3], [0.9, 1.8, 4], [1.8, 10, 5]])

    outReclass1 = Reclassify('minus_raster', 'Value', re_class)

    reclass_raster_name = os.path.join(reclass_path, 'Reclass_{}.tif'.format(name))
    outReclass1.save(reclass_raster_name)

    print(point_shp)
