# -*- coding: UTF-8 -*-
import scraperwiki
import re
import urlparse
import datetime
import os
from bs4 import BeautifulSoup # BeautifulSoup helps you to find what you want in HTML

def urlEncodeNonAscii(b):
    return re.sub('[\x80-\xFF]', lambda c: '%%%02x' % ord(c.group(0)), b)

def iriToUri(iri):
    parts= urlparse.urlparse(iri)
    return urlparse.urlunparse(
        part.encode('idna') if parti==1 else urlEncodeNonAscii(part.encode('utf-8'))
        for parti, part in enumerate(parts)
    )

correctionsflag = False
scraperwiki.sqlite.execute("drop table if exists swdata")

if 'MORPH_DOMAIN' in os.environ and 'MORPH_STARTPATH' in os.environ:
    domain = os.environ['MORPH_DOMAIN'] 
    startpath = os.environ['MORPH_STARTPATH']
else:
    print("please define morph.io parameters")
url = domain + startpath
html = scraperwiki.scrape(url) # download the html content of the page
soup = BeautifulSoup(html) # load the html into beautifulsoup

i = 0
bezirke = []
orte = []
events = []
tageins = datetime.datetime(1989, 8, 7)  ## beginn der ersten woche erste monat 7.8.89 relativ zu 13.8.89
for bezirkarea in soup.find_all("area"): # for each 
    url = iriToUri(domain + bezirkarea['href'])
    title = bezirkarea['title']
    bezirk = title.replace("Bezirk ", "")
    bezirke.append({"name": bezirk, "url": url})

for b in bezirke:
    url = b["url"]
    bezirk = b["name"]
    print (url)
    html = scraperwiki.scrape(url) 
    soup = BeautifulSoup(html).find(id="overlay-content")
    for ortli in soup.find_all("li"):
        tmpbezirk = bezirk
        url= iriToUri(domain + ortli.a['href'])
        title = ortli.a.contents[0]
        ort = re.sub(' \(.*$', '', title)
        ## temporary on the fly corrections of known errors
        if (ort == u"Münchenberndsdorf"):
            ort = u"Münchenberndsdorf"
            printstr = u"Korrektur Münchenberndsdorf > Münchenbernsdorf"
            print(printstr.encode('utf-8'))
            correctionsflag = True
        if ((ort == "Gera") and (tmpbezirk == "Erfurt")):
            tmpbezirk = "Gera"
            print("Korrektur Gera, Bezirk Erfurt > Bezirk Gera")
            correctionsflag = True
        ## end corrections
        orte.append({"name": ort, "bezirk": tmpbezirk, "url": url}) # put the values extracted into a list

def parsefield(html, string):
    suffix = ":"
    searchstring = string + suffix
    prefixrepattern = '^[ ]*'  ## select leading spaces
    fieldtitlecontainerelement = 'b'
    fielddata = re.sub(prefixrepattern, '', html.find(fieldtitlecontainerelement, text=searchstring).next_sibling)
    return fielddata

for o in orte:
    ort = o["name"]
    bezirk = o["bezirk"]
    url = o['url']
    html = scraperwiki.scrape(url) 
    soup = BeautifulSoup(html).find(id="overlay-content")
    for ee in soup.find_all("div", class_="entry"): ## ee: event entry
        datum = parsefield(ee, "Datum")
        teilnehmermax = parsefield(ee, "Teilnehmer Max")
        teilnehmermaxka = (teilnehmermax == "keine Angaben")
        teilnehmermax =  0 if teilnehmermaxka else int(teilnehmermax)
        teilnehmermin = parsefield(ee, "Teilnehmer Min")
        teilnehmerminka = (teilnehmermin == "keine Angaben")
        teilnehmermin =  0 if teilnehmerminka else int(teilnehmermin)
        einwohner = int(parsefield(ee, "Einwohner (1989)"))
        ## get relative number of participants as 2 digit precision float
        ## teilnehmerort = 0 if (teilnehmermax == 0 or einwohner == 0) else float("%0.2f" % ((float(teilnehmermax)/einwohner) * 100))
        ttuple = datetime.datetime.strptime(datum, "%d.%m.%Y")
        date = ttuple.date()
        obj = {
            "id" : i,
            "bezirk":  bezirk,
            "ort": ort,
            "datum": datum,

            ## derived from datum
            "jahr":  ttuple.timetuple().tm_year,
            "monat":  ttuple.timetuple().tm_mon,
            "tag":  ttuple.timetuple().tm_mday,
            "yday": ttuple.timetuple().tm_yday,
            "tageseit": (ttuple - tageins).days,
            "isoweekday": date.isoweekday(),
            "isoweek": date.isocalendar()[1],
            
            "teilnehmermax": teilnehmermax,
            "teilnehmermin": teilnehmermin,
            "teilnehmermaxka": teilnehmermaxka,
            "teilnehmerminka": teilnehmerminka,
            "einwohner": einwohner,

             ## daten nicht ausreichend
             ## "teilnehmerrelort":  teilnehmerort,

            "demo": (parsefield(ee, "Demo") == "x"), ## boolean
            "kirche": (parsefield(ee, "Kirche") == "x"),  ## boolean
            "url": url,       
            "beschreibung": parsefield(ee, "Beschreibung"),
            "aufgerufen": parsefield(ee, "Aufgerufen"),
            "thema": parsefield(ee, "Thema"),
            "besonderheiten": parsefield(ee, "Besonderheiten"),
            "bundesland": parsefield(ee, "Bundesland")
        }
        olist = [
            obj["id"],
            obj["bezirk"],
            obj["ort"].encode('utf-8') + " (" + str(obj["einwohner"]) + ")",
            obj["datum"],
            obj["kirche"],
            obj["demo"],
            obj["teilnehmermax"]
        ]
        print('\t'.join(map(str,olist))) ## debug log tab seperated
        events.append(obj)
        i = i + 1;

scraperwiki.sqlite.save(unique_keys=["id"], data=events)
if correctionsflag:
   print("finished with corrections") 
else:
   print("finished without corrections")  
