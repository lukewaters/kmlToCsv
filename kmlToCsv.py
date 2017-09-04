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
import re


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
    with open('GreenlandCalvingFronts.kml', 'r') as f:
        s = BeautifulSoup(f, 'xml')
        with open('out.csv', 'w', newline='') as csvfile:
            # writer = csv.writer(csvfile)
            fieldnames = ["polygon_id", "polygon", "glacier_name", "date", "sensor", "glacier_id"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            count = 0
            # Write header row, we may want to remove this row
            for placemark in s.find_all('Placemark'):
                # We can continue to parse the placemark object in the same way we would parse the whole document
                element = {}
                element['polygon_id'] = ''
                element['glacier_name'] = placemark.find('name').contents[0]
                try:
                    element['polygon'] = placemark.find('coordinates').contents[0].strip() # using strip to remove extra blank space
                except AttributeError:
                    element['polygon'] = '' # some rows don't have coordinates
                for elem in placemark.find_all('SimpleData'):
                    try: 
                        name = elem['name']
                        if name == 'SENSOR':
                            element['sensor'] = elem.contents[0]
                        elif name == 'DATE_':
                            element['date'] = elem.contents[0]
                        elif name == 'ID':
                            element['glacier_id'] = elem.contents[0]
                    except KeyError:
                        pass
                writer.writerow(element)
                count = count + 1
    print("Count: ", count)

if __name__ == "__main__":
    main()
