import re 
import csv
import json 
import os
import requests
import sys

url = 'https://www.basketball-reference.com/leagues/NBA_2019_advanced.html'

#################################################################################################################
def pripravi_imenik(ime_datoteke):
    '''Če še ne obstaja, pripravi prazen imenik za dano datoteko.'''
    imenik = os.path.dirname(ime_datoteke)
    if imenik:
        os.makedirs(imenik, exist_ok=True)

def shrani_spletno_stran(url, ime_datoteke, vsili_prenos=False):
    '''Vsebino strani na danem naslovu shrani v datoteko z danim imenom.'''
    try:
        print('Shranjujem {} ...'.format(url), end='')
        sys.stdout.flush()
        if os.path.isfile(ime_datoteke) and not vsili_prenos:
            print('shranjeno že od prej!')
            return
        r = requests.get(url)
    except requests.exceptions.ConnectionError:
        print('stran ne obstaja!')
    else:
        pripravi_imenik(ime_datoteke)
        with open(ime_datoteke, 'w', encoding='utf-8') as datoteka:
            datoteka.write(r.text)
            print('shranjeno!')

def vsebina_datoteke(ime_datoteke):
    '''Vrne niz z vsebino datoteke z danim imenom.'''
    with open(ime_datoteke, encoding='utf-8') as datoteka:
        return datoteka.read()

def zapisi_csv(slovarji, imena_polj, ime_datoteke):
    '''Iz seznama slovarjev ustvari CSV datoteko z glavo.'''
    pripravi_imenik(ime_datoteke)
    with open(ime_datoteke, 'w', encoding='utf-8') as csv_datoteka:
        writer = csv.DictWriter(csv_datoteka, fieldnames=imena_polj)
        writer.writeheader()
        for slovar in slovarji:
            writer.writerow(slovar)

def zapisi_json(objekt, ime_datoteke):
    '''Iz danega objekta ustvari JSON datoteko.'''
    pripravi_imenik(ime_datoteke)
    with open(ime_datoteke, 'w', encoding='utf-8') as json_datoteka:
        json.dump(objekt, json_datoteka, indent=4, ensure_ascii=False)

###################################################################################################################

def shrani_statistiko_vseh(url):
    ime_datoteke = 'statistika_nba.html'
    shrani_spletno_stran(url, 'html_datoteke/statistika_vseh.html')

#shrani_statistiko_vseh(url)

vzorec_vseh = re.compile(
    r'<tr class="full_table" >.*?'
    r'data-append-csv="(?P<ID>.*?)" data-stat="player" '     #ID
    r'csk=".*?" ><a href="/players/(?P<geslo>.*?).html">'   #geslo
    r'(?P<ime_priimek>.*?)</a></td>'     #ime in priimek
    )

def seznam_skupaj(imenik, vzorec):            
    a=0
    sez=[]
    for ime_datoteke in os.listdir(imenik):
        pot = os.path.join(imenik, ime_datoteke)
        with open(pot, encoding = 'utf-8') as datoteka:
            vsebina = datoteka.read()
        for ujemanje in vzorec.finditer(vsebina):
            podatki = ujemanje.groupdict()
            sez.append(podatki)
            a+=1
        print(a)
    return sez

seznam_podatkov = seznam_skupaj('html_datoteke', vzorec_vseh)   
#print(seznam_podatkov) 

def shrani_statistiko_igralec(podatki):
    dolzina = len(podatki)
    for i in range(0, dolzina):
        geslo=podatki[i]['geslo']
        ID=podatki[i]['ID']
        igralec_url = 'https://www.basketball-reference.com/players/{}.html'.format(str(geslo))
        datoteka_ime = 'html_datoteke/igralec_{}.html'.format(str(ID))
        shrani_spletno_stran(igralec_url, datoteka_ime)
    return None

#shrani_statistiko_igralec(seznam_podatkov)

vzorec_info = re.compile(
    r'<h1 itemprop="name">\s*?'
    r'<span>(?P<ime_priimek>.*?)</span>\s*?'   #ime in priimek
    r'</h1>.*?'
    r'<span itemprop="weight">.*?</span>&nbsp;'
    r'\((?P<višina>.*?)cm,&nbsp;(?P<teža>.*?)kg\) </p>.*?'      #višina in teža
    r'<span itemprop="birthDate" id="necro-birth" data-birth="(?P<rojstvo>.*?)-\d{2}-\d{2}">.*?'    #letnica rojstva
    r'<span itemprop="birthPlace">\s*?'
    r'in&nbsp;.*?,&nbsp;<a .*?>(?P<država>.*?)</a></span>',     #država
    flags=re.DOTALL
    )

vzorec_stat = re.compile(
    r'<tr id="per_game.2019" class="full_table" ><th scope="row" class="left " data-stat="season" >'
    r'<a href="/players/(?P<geslo>.*?)/gamelog/2019/">2018-19</a>.*?'        #geslo
    r'<td class="left " data-stat="team_id" >(<a href="/teams/.{3}/2019.html">|)(?P<ekipa>.*?)(</a></td>|</td>).*?' #ekipa
    r'<td class="center " data-stat="pos" >(<strong>|)(?P<pozicija>.*?)(</strong>|)</td>'         #pozicija
    r'<td class="right " data-stat="g" >(<strong>|)(?P<GP>.*?)(</strong>|)</td>.*?'            #igranih tekem
    r'<td class="right " data-stat="mp_per_g" >(<strong>|)(?P<MP_game>.*?)(</strong>|)</td>.*?'  #minute na tekmo
    r'<td class="right " data-stat="fg3_per_g" >(<strong>|)(?P<Tri_FG>.*?)(</strong>|)</td>.*?'   #zadete 3 na tekmo
    r'<td class="right .{0,2}" data-stat="fg3_pct" >(<strong>|)(?P<Tri_pct>.*?)(</strong>|)</td>.*?'      #procent meta za 3
    r'<td class="right " data-stat="ft_per_g" >(<strong>|)(?P<FT_game>.*?)(</strong>|)</td>.*?'     #prosti meti na tekmo    
    r'<td class="right .{0,2}" data-stat="ft_pct" >(<strong>|)(?P<FT_pct>.*?)(</strong>|)</td>.*?'     #prosti meti procent
    r'<td class="right " data-stat="trb_per_g" >(<strong>|)(?P<RPG>.*?)(</strong>|)</td>'      #skoki
    r'<td class="right " data-stat="ast_per_g" >(<strong>|)(?P<APG>.*?)(</strong>|)</td>.*?'      #asistence 
    r'<td class="right " data-stat="pts_per_g" >(<strong>|)(?P<PPG>.*?)(</strong>|)</td></tr>'   #točke
    )



seznam_igralci = seznam_skupaj('html_datoteke', vzorec_info)
#print(seznam_igralci)
seznam_statistika = seznam_skupaj('html_datoteke', vzorec_stat)
#print(seznam_statistika)

def merge_lists(slovar1, slovar2, key):
    merged = {}
    for item in slovar1+slovar2:
        if item[key] in merged:
            merged[item[key]].update(item)
        else:
            merged[item[key]] = item
    return [val for (_, val) in merged.items()]

zdruzen_seznam = merge_lists(seznam_podatkov, seznam_igralci, 'ime_priimek')
print(zdruzen_seznam)

zdruzen_seznam_koncno = merge_lists(zdruzen_seznam, seznam_statistika, 'geslo')
print(zdruzen_seznam_koncno)


zapisi_json(zdruzen_seznam_koncno, 'urejeni_podatki.json')    

zapisi_csv(zdruzen_seznam_koncno,
    ['ID', 'geslo', 'ime_priimek', 'višina', 'teža', 'rojstvo', 'država', 'ekipa', 'pozicija', 'GP', 'MP_game',
    'Tri_FG', 'Tri_pct', 'FT_game', 'FT_pct', 'RPG', 'APG', 'PPG'], 
    'urejeni_podatki.csv'
)

