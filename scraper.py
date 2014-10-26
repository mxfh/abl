import scraperwiki
from bs4 import BeautifulSoup # BeautifulSoup helps you to find what you want in HTML

scraperwiki.sqlite.execute("drop table if exists swdata")

url = "http://www.archiv-buergerbewegung.de/index.php/demonstrationen" # loading your url from the csv/database
html = scraperwiki.scrape(url) # download the html content of the page
soup = BeautifulSoup(html) # load the html into beautifulsoup

bezirke = [] # start with an empty list
for bezirkarea in soup.find_all("area"): # for each 
    url = bezirkarea['href']
    name = bezirkarea['title']
    bezirke.append({"proper": name.replace("Bezirk ", "") , "url": url, "name": name}) # put the values extracted into a list

scraperwiki.sqlite.save(unique_keys=["proper"], data=bezirke)
