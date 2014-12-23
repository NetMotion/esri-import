# convert_netmo_csv_to_esri_shapefile.py
## Overview
This utility converts exported coverage data from NetMotion Wireless' Locality product into an Esri shapefile for importing into Esri products.  General usage steps:

1. Place one or more Coverage Data Export CSV files from a Locality server into a directory on the machine from which you will run this utility
2. Run this utlity, specifying the directory above and a path for the output shapefile
3. Import the resultant shapefile into your Esri document

## About Each Step

### Obtaining the Coverage Data CSV files
In the Locality server console, Coverage Data Export is located under the `System` tab.  Look for the `Coverage Data Export` menu item.

Coverage Data Export must be enabled for the CSV files to be generated.  At the top of the `Coverage Data Export` page there is a `Coverage Data Export Status` section.  Make sure that section reports `Coverage data export is enabled`.  If it does not, click the `Enable` button you will find there.

Coverage data is made available on a nightly basis.  Each day's worth of coverage data is zipped up and place into a file named `LocalityExport.YYYY-MM-dd.zip` where `YYYY-MM-dd` is the date the data was gathered.

Each zip file can be downloaded using the download link next to each file in the `Exported Files` section of the `Coverage Data Export` page.  The files are stored on the Locality server at `D:/Program Data/NetMotion Wireless/Locality Server/Export`.

Unzip the files and place the resultant CSV files into a common directory.

### Running this utility
The simplest way to run is to place this `.py` file into the same directory as the CSV files and execute using Esri's copy of Python:

`c:\Python27\ArcGIS10.2\python.exe convert_netmo_csv_to_esri_shapefile.py`

This will automatically import all CSV files found there and produce a shape file called `NetMotion.shp`.

For help, such as command line options, call the utility with the `--help` option.

### Importing into ESRI products
From your ArcMap project import the resultant SHP file.  The geographic coordinate system is WGS 1984.  This will import the SHP file as a layer.

> Hint: Here's a nice way to view your coverage data.  Change the layer's `Symbology` to `Quantities > Graduated colors` and select `LocalitySQ` as your field.  Set your `Number of classes` to something like 10.

## Now What?
It is recommended you review the utility's code.  It's not that big and (_warning_) it's not very pretty.  Hopefully it will serve as a good starting point if you need to import Locality's data into your Esri project.