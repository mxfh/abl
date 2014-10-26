import scraperwiki
import re
import urlparse
import time
from bs4 import BeautifulSoup # BeautifulSoup helps you to find what you want in HTML

def urlEncodeNonAscii(b):
    return re.sub('[\x80-\xFF]', lambda c: '%%%02x' % ord(c.group(0)), b)

def iriToUri(iri):
    parts= urlparse.urlparse(iri)
    return urlparse.urlunparse(
        part.encode('idna') if parti==1 else urlEncodeNonAscii(part.encode('utf-8'))
        for parti, part in enumerate(parts)
    )

scraperwiki.sqlite.execute("drop table if exists swdata")

domain = "http://www.archiv-buergerbewegung.de"
url = "http://www.archiv-buergerbewegung.de/index.php/demonstrationen" # loading your url from the csv/database
html = scraperwiki.scrape(url) # download the html content of the page
soup = BeautifulSoup(html) # load the html into beautifulsoup

bezirke = []
orte = []
events = []
for bezirkarea in soup.find_all("area"): # for each 
    url = iriToUri(domain + bezirkarea['href'])
    title = bezirkarea['title']
    bezirk = title.replace("Bezirk ", "")
    bezirke.append({"name": bezirk, "url": url}) # put the values extracted into a list
    html = scraperwiki.scrape(url) 
    soup = BeautifulSoup(html).find(id="overlay-content")
    for ortli in soup.find_all("li"): 
        url=  iriToUri(domain + ortli.a['href'])
        title = ortli.a.contents[0]
        ort = re.sub(' \(.*$', '', title)
        orte.append({"name": ort, "url": url}) # put the values extracted into a list
        html = scraperwiki.scrape(url) 
        soup = BeautifulSoup(html).find(id="overlay-content")
        for evententries in soup.find_all("div", class_="entry"): 
            datum = re.sub('^[ ]*', '', evententries.find('b', text="Datum:").next_sibling) ## remove leading spaces
            teilnehmermax =  re.sub('^[ ]*', '', evententries.find('b', text="Teilnehmer Max:").next_sibling).replace("keine Angaben", "0")
            teilnehmermin =  re.sub('^[ ]*', '', evententries.find('b', text="Teilnehmer Min:").next_sibling).replace("keine Angaben", "0")
            einwohner = re.sub('^[ ]*', '', evententries.find('b', text="Einwohner (1989):").next_sibling)
            kirche = (evententries.find('b', text="Kirche:").next_sibling == " x")  ## boolean
            demo = (evententries.find('b', text="Demo:").next_sibling == " x")
            print(bezirk, ort, datum, teilnehmermax, einwohner, kirche, demo, url)
            events.append({
                "key" : datum + ort,
                "bezirk": bezirk,
                "ort": ort,
                "datum": datum,
                "ts" : time.strptime(datum, "%d.%m.%Y"),
                "teilnehmermax" : int(teilnehmermax.replace("keine Angaben", 0)),
                "teilnehmermin" : int(teilnehmermin.replace("keine Angaben", 0)),
                "einwohner" : int(einwohner),
                "demo" : demo,
                "kirche" : kirche
                })

    scraperwiki.sqlite.save(unique_keys=["key"], data=evententries)
