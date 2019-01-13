# Motorized Stage to Montage (TrackEM)

The stage the 2P rig uses was reverse-engineered to be controlled (and read from) using Python. This allows image captures to occur and filenames to be saved which contain X/Y coordinates in microns. Reading a list of filenames, this script will create a TrackEM montage XML file which, when loaded, loads all the scanned images and places them in the X/Y position they were scanned in according to the location of the motorized stage.

TrackEM2 is available with FIJI: https://imagej.net/TrakEM2
