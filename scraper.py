import scraperwiki
import re
from bs4 import BeautifulSoup # BeautifulSoup helps you to find what you want in HTML

scraperwiki.sqlite.execute("drop table if exists swdata")

domain = "http://www.archiv-buergerbewegung.de"
url = "http://www.archiv-buergerbewegung.de/index.php/demonstrationen" # loading your url from the csv/database
html = scraperwiki.scrape(url) # download the html content of the page
soup = BeautifulSoup(html) # load the html into beautifulsoup

bezirke = []
orte = []
for bezirkarea in soup.find_all("area"): # for each 
    url = bezirkarea['href']
    title = bezirkarea['title']
    name = title.replace("Bezirk ", "")
    bezirke.append({"name": name, "url": url}) # put the values extracted into a list
    htmlb = scraperwiki.scrape(domain + url) 
    soupb = BeautifulSoup(htmlb)
    for ortli in soupb.find_all("li"): 
        url = ortli.a['href']
        title = ortli.a.contents[0]
        name = re.sub('\(.*$', '', title)
        count = re.search("\((d+) Eintr\w+\)$", title)
        orte.append({"name": name, "url": url, "count": count}) # put the values extracted into a list

    
scraperwiki.sqlite.save(unique_keys=["name"], data=orte)
