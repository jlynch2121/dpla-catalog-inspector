"""
    Creator: Joshua Lynch
    Date: 2018-11
    Description: script designed for metadata retrieval and inspection. Gathers JSON data using the Digital Public Library of America (DPLA) API. This data will be plugged into OpenRefine for inspection
"""

"""
    1) Call DPLA API to get UIUC records. try to call collections at a time. For each record in first page of collection:
        i. save DPLA IDs from JSON
        ii. create and save DPLA links ('https://dp.la/item/' + id) from JSON DPLA IDs
        iii. save the thumbnail URLs provided by IDHH
        iv. use headless browser to get each created url. Pseudocode:
            save img with class="ItemImage__image___2usCc" src attrib
        v. inspect each DPLA item record page for thumbnails
        vi. save thumbnails links
        vii. save each item (DPLA IDs, DPLA links, IDHH thumbnails, DPLA thumbnails) in separate CSVs: one list of items with thumbnails, one list of items missing thumbnails. Pseudocode:
            if img with class="ItemImage__image___2usCc" has src attrib != 'http://dp.la/thumb/' + id: write to CSV for items missing thumbnails
            else: write to list of items with thumbnails
        viii. advance the page
    2) after collecting data for last page of collection, go to the next collection with API. Rinse and repeat
"""
import csv
import requests
import math
from selenium import webdriver
#import time



# variable for API key
apiKey = 'api-key'

# variable for Service Hub name. It is recommended to use plus signs '+' instead of spaces between words in the hub name, as demonstrated below
serviceHub = 'name-of-dpla-partner'

with open('file-name.csv', newline='', encoding='utf-8') as csv_file:
  csv_reader = csv.reader(csv_file)

  # if csv file with collections opens, create CSV for items
  withThumbs = open('withThumbs.csv', 'w', newline='')
  withThumbsWriter = csv.writer(withThumbs)
  columnNames = [['ID','collection','item link','IDHH thumbnail','DPLA thumbnail']]
  withThumbsWriter.writerows(columnNames)
  noThumbs = open('noThumbs.csv', 'w', newline='')
  noThumbsWriter = csv.writer(noThumbs)
  noThumbsWriter.writerows(columnNames)

  # define selenium browser
  driver = webdriver.Firefox()

  # begin a for loop that will grab each row of the CSV and strip its whitespace
  for row in csv_reader:
    # strip row of whitespace
    collection = row[0].strip()

    """
        create API request. Note: it is not necessary to include 'provider.name' but this helps to insure data is from the correct service hub in case there are problems with the collection name. The request below will provide:
        sourceResource.title: the title of the item
        dataProvider: the contributing institution
        sourceResource.collection.title: the title of the collection of which the record is a part
        originalRecord.type: original Type metadata value harvested by the DPLA
        sourceResource.type: Type metadata value created by the DPLA which should appear in DPLA search interfaces
    """
    apiRequest = 'https://api.dp.la/v2/items?api_key=' + apiKey + '&fields=id,object&page_size=500&provider.name=' + serviceHub + '&sourceResource.collection.title=' + '"' + collection + '"'


    # make request
    r = requests.get(apiRequest)

    # read the JSON file and check for the value of 'count':
    requestData = r.json()

    itemCount = requestData['count']
    pages = math.ceil(itemCount / 500)
    """
        loop that iterates for each page of get results. not particularly efficient as this calls page 1 AGAIN, after it was initially called above just to get the count.

        To-do: will need to re-write the 'for i in record' loop below in a function so that it may be called above to loop through a first page of results. the 'for x in range' loop below should only work if there's a page with a count of greater than 500.
    """
    for x in range(1, (pages + 1)):
      apiPages = apiRequest + '&page=' + str(x)
      s = requests.get(apiPages)

      pageData = s.json()

      record = pageData['docs']
      # loop iterates through each record ('doc') on a page
      for i in record:
        id = i['id']
        link = 'https://dp.la/item/' + i['id']
        idhhThumb = i['object']
        driver.get(link)
        #time.sleep(15)
        imgWrapper = driver.find_element_by_class_name('ItemImage__image___2usCc')
        dplaThumbnail = imgWrapper.get_attribute("src")
        thumbsRow = [[id,collection,link,idhhThumb,dplaThumbnail]]
        if 'placeholderImages' in str(dplaThumbnail):
            noThumbsWriter.writerows(thumbsRow)
        else:
            withThumbsWriter.writerows(thumbsRow)
