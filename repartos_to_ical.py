#!/usr/bin/python3
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from datetime import datetime
import re
from icalendar import Calendar, Event

re_fc = re.compile(r"^\d+-\d+-\d+$")
re_carne = re.compile(r"\bcarne\b", re.IGNORECASE)
re_acta = re.compile(r"\bacta\b", re.IGNORECASE)

def get(key):
    cal = Calendar()
    cal.add('version', '2.0')
    cal.add('prodid', '-//'+key.upper()+'//KARAKOLAs//ES')
    cal.add('X-WR-CALNAME', key.title())
    cal.add('x-wr-timezone', 'Europe/Madrid')

    with open(key+'.html') as f:
        soup = BeautifulSoup(f,"lxml")
    return cal, soup

cal, soup = get("pedidos")

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

            title = "Reparto " + ("C" if carne else "V")
            event = Event()
            event.add('summary', title)
            event.add('dtstart', f.replace(hour=18, minute=00))
            event.add('dtend', f.replace(hour=20, minute=00))
            event.add('location', 'Av. de Carabanchel Alto, 64, 28044 Madrid, España')
            if carne:
                event.add('DESCRIPTION', 'Reparto de carne')
            else:
                event.add('DESCRIPTION', 'Reparto principal: Verduras, cosmética, pasta, fruta, pescado, etc')
            event.add('uid', f.strftime("%Y-%m-%d") + "_" + title.replace(" ", "_").lower())

            cal.add_component(event)

    with open("repartos.ics", 'wb') as f:
        f.write(cal.to_ical())

cal, soup = get("actas")

for h in soup.select("h3 a"):
    t = h.get_text().strip()
    if re_acta.search(t):
        print (t)
