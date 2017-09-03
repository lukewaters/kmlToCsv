"""
A script to take all of the LineString information out of a very large KML file. It formats it into a CSV file so
that you can import the information into the NDB of Google App Engine using the Python standard library. I ran this
script locally to generate the CSV. It processed a ~70 MB KML down to a ~36 MB CSV in about 8 seconds.
The KML had coordinates ordered by
    [Lon, Lat, Alt, ' ', Lon, Lat, Alt, ' ',...]   (' ' is a space)
The script removes the altitude to put the coordinates in a single CSV row ordered by
    [Lat,Lon,Lat,Lon,...]
Dependencies:
 - Beutiful Soup 4
 - lxml
I found a little bit of help online for using BeautifulSoup to process a KML file. I put this online to serve as
another example. Some things I learned:
 - the BeautifulSoup parser *needs* to be 'xml'. I spent too much time debugging why the default one wasn't working, and
   it was because the default is an HTML parse, not XML.
tl;dr
KML --> CSV so that GAE can go CSV --> NDB
"""

from bs4 import BeautifulSoup
import csv


def process_coordinate_string(str):
    """
    Take the coordinate string from the KML file, and break it up into [Lat,Lon,Lat,Lon...] for a CSV row
    """
    space_splits = str.split(" ")
    ret = []
    # There was a space in between <coordinates>" "-80.123...... hence the [1:]
    for split in space_splits[1:]:
        comma_split = split.split(',')
        ret.append(comma_split[1])    # lat
        ret.append(comma_split[0])    # lng
    return ret

def main():
    """
    Open the KML. Read the KML. Open a CSV file. Process a coordinate string to be a CSV row.
    """
    with open('doc.kml', 'r') as f:
        s = BeautifulSoup(f, 'xml')
        with open('out.csv', 'wb') as csvfile:
            writer = csv.writer(csvfile)
            for coords in s.find_all('coordinates'):
                writer.writerow(process_coordinate_string(coords.string))

if __name__ == "__main__":
    main()