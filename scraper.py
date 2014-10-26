import scraperwiki
from bs4 import BeautifulSoup # BeautifulSoup helps you to find what you want in HTML

url = "http://www.archiv-buergerbewegung.de/index.php/demonstrationen" # loading your url from the csv/database
html = scraperwiki.scrape(url) # download the html content of the page
#html = ""
soup = BeautifulSoup(html) # load the html into beautifulsoup

bezirke = [] # start with an empty list
for bezirkarea in soup.find_all("area"): # for each 
    url = bezirkarea['href']
    title = bezirkarea['title']
    bezirke.append({"url": url, "bezirk": title}) # put the values extracted into a list

scraperwiki.sqlite.save(unique_keys=["url"], data=bezirkarea) # save the list of cat photos and captions
