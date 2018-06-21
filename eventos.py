#!/usr/bin/python3
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from datetime import datetime
import re
from icalendar import Calendar, Event
import os

re_fc = re.compile(r"^\d+-\d+-\d+$")
re_carne = re.compile(r"\bcarne\b", re.IGNORECASE)
re_acta = re.compile(r"\bacta\b", re.IGNORECASE)

def get_cal(key):
    cal = Calendar()
    cal.add('version', '2.0')
    cal.add('prodid', '-//'+key.upper()+'//KARAKOLAs//ES')
    cal.add('X-WR-CALNAME', key.title())
    cal.add('x-wr-timezone', 'Europe/Madrid')

    html = key+'.html'
    soup = None
    if os.path.isfile(html):
        with open(html) as f:
            soup = BeautifulSoup(f,"lxml")

    return cal, soup

def get_event(title, description, f, hour, minute=00, duration=2):
    event = Event()
    event.add('summary', title)
    event.add('dtstart', f.replace(hour=hour, minute=minute))
    event.add('dtend', f.replace(hour=hour+duration, minute=minute))
    event.add('location', 'Av. de Carabanchel Alto, 64, 28044 Madrid, España')
    if description:
        event.add('DESCRIPTION', description)
    event.add('uid', f.strftime("%Y-%m-%d") + "_" + title.replace(" ", "_").lower())
    return event

cal, soup = get_cal("pedidos")

for h in soup.findAll("h3"):
    t = h.get_text().strip()
    if re_fc.match(t):
        f = datetime.strptime(t, '%d-%m-%Y')
        if f.weekday() == 1:
            carne = False
            for tr in h.find_parent("div").findAll("tr"):
                td = tr.find("td")
                if td:
                    carne = carne or re_carne.search(td.get_text())

            event = None
            if carne:
                title = "Reparto Carne"
                description = 'Reparto de carne'
                event = get_event(title, description, f, 19, 00, duration=1)
            else:
                title = "Reparto"
                description = 'Reparto principal: Verduras, cosmética, pasta, fruta, pescado, etc'
                event = get_event(title, description, f, 18, 30)
                
            cal.add_component(event)

with open("repartos.ics", 'wb') as f:
    f.write(cal.to_ical())

cal, _ = get_cal("asambleas")

'''
for h in soup.select("h3 a"):
    t = h.get_text().strip()
    if re_acta.search(t):
        print (t)
'''

fechas = [f.strip() for f in '''
26/02/2013
21/05/2013
17/12/2013
09/09/2014
21/10/2014
16/12/2014
07/04/2015
13/10/2015
24/11/2015
19/02/2015
01/03/2016
26/04/2016
07/06/2016
13/09/2016
24/09/2016
11/10/2016
22/11/2016
20/12/2016
31/01/2017
28/02/2017
28/03/2017
23/05/2017
12/09/2017
10/10/2017
27/02/2018
24/03/2018
22/05/2018
19/06/2018
'''.strip().split("\n")]

for f in fechas:
        f = datetime.strptime(f, '%d/%m/%Y')
        event = get_event("Asamblea", None, f, 20, 30)
        cal.add_component(event)


with open("asambleas.ics", 'wb') as f:
    f.write(cal.to_ical())
