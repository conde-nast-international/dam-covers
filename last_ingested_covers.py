#!/usr/local/bin/python3
# requires Python3+ and requests, python-dateutil libraries

u = 'marco.baldassarre@condenastint.com'
p = 'password'
host = 'https://emea.cnidam.com'
root = '/content/dam/cni-dam/'

num_covers = 100

emea_markets = ['de', 'cnit', 'uk', 'fr', 'ru', 'mx', 'es', 'it']
apac_markets = ['cn', 'in', 'tw', 'jp']

import requests, os.path
import dateutil.parser, datetime
#os, xml, sys, re, urllib, hashlib, datetime, time

def debug(s):
    if True: print(s)

def progress(s):
    if True: print(s)
    
def created_date(url):
    r = requests.get(host + url, auth=(u, p))
    r.raise_for_status()
    return(r.text)

def download(url, filename):
    r = requests.get(host + url, auth=(u, p), cookies={'login-token': '6122cfef-3ffa-41a1-be75-16308cfb9ca3:2e792244-6c6a-494a-90ae-1f86da87070f_7a033443c2438079'})
    r.raise_for_status()
    
    with open(filename, 'wb') as f:
        for chunk in r.iter_content(1024):
            f.write(chunk)
            
def parse_querybuilder(query):
    p = {}
    for line in query.split('\n'):
        if line == '': continue
        eq = line.split('=')
        p[eq[0].strip()] = eq[1].strip()
    return p

def query_latest_covers():
    url = "/bin/querybuilder.json"
    query = '''
_charset_=UTF-8
type=cni:publishedLayoutPage
path=''' + root + '''
1_property=jcr:content/metadata/cni:relationships/cni:rel0/cni:medium/@cni:isCover
1_property.value=true
orderby=@jcr:created
orderby.sort=desc
p.limit=''' + str(num_covers) + '''
p.offset=0
p.guessTotal=true
p.nodepth=6
p.hitwriter=publishedlayoutpage
'''
    payload = parse_querybuilder(query)
    r = requests.get(host + url, params=payload, auth=(u, p))
    r.raise_for_status()
    hits = r.json()['hits']
    return hits



list_to_dedupe = sorted(query_latest_covers(), key=lambda k: k['originMarket']+k['issueTitle']+k['issueName']+k['issuePublishDate'], reverse=True) 

last_created_covers = []
for l in range(len(list_to_dedupe)-1,1,-1):
    c1=list_to_dedupe[l]
    c2=list_to_dedupe[l-1]
    if (c1['originMarket']+c1['issueTitle']+c1['issueName']+c1['issuePublishDate'] !=
        c2['originMarket']+c2['issueTitle']+c2['issueName']+c2['issuePublishDate']):
        c1.update({'createdDate': created_date(c1['path'] + '/jcr:content/renditions/jcr:created')})
        last_created_covers.append(c1)


last_published_covers = sorted(last_created_covers, key=lambda k: dateutil.parser.parse(k['createdDate']), reverse=True) 


print('''
<!doctype html>
<html lang="en">
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
        <style>
            * {
                margin: 0;
                padding: 0;
            }

            body {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol";
                font-size: 14px;
                height: 100vh;
            }

            table {
                width: 100%;
                height: 100%;
                table-layout: fixed;
                border-collapse: collapse;

            }

            th, td {
                padding-left: 10px;
                padding-right: 10px;
                text-align: left;
            }

            td:nth-child(1), th:nth-child(1) { width: 50px; }
            td:nth-child(2), th:nth-child(2) { width: 150px; text-align: center; }
            td:nth-child(3), th:nth-child(3) { width: 100px; }
            td:nth-child(4), th:nth-child(4) { width: 150px; }
            td:nth-child(5), th:nth-child(5) { width: 200px; }
            td:nth-child(6), th:nth-child(6) { width: 200px; }
            td:nth-child(7), th:nth-child(7) { width: 200px; }

            td:nth-child(1) {
                font-weight: 700;
                border-left: none;
            }

            td {
                border-left: 1px solid #f3f3f6;
            }

            th {
                border-left: 1px solid transparent;
            }

            thead {
                background: #4f5764;
                color: #fff;
                display: block;
            }

            thead tr {
                display: block;
                height: 40px;
                position relative;
            }

            thead th {
                height: 40px;
            }

            tbody {
                display: block;
                overflow: auto;
                width: 100%;
                height: calc(100% - 40px);
            }

            tbody tr {
                display: block;
                border-bottom: 1px solid #e2e3e6;
            }

            tbody tr:hover,
            tbody tr:nth-child(even):hover {
                background: #e2e3e6;
                color: #000;
            }

            tbody tr:nth-child(even) {
                background-color:#f7f9fb;
            }

            img {
                box-shadow: 0 4px 2px -2px rgba(0,0,0,0.4);
                max-width: 150px;
            }
        </style>
    </head>
<body>
<table>
        <thead>
            <tr>
                <th>#</th>
                <th>COVER</th>
                <th>MARKET</th>
                <th>TITLE</th>
                <th>ISSUE</th>
                <th>PUBLICATION</th>
                <th>ARCHIVAL</th>
                <th>DIFF (days)</th>
            </tr>
        </thead>
<tbody>
''')

for x in range(len(last_published_covers)):
    rank = x+1
    
    pub_date = dateutil.parser.parse(last_published_covers[x]['issuePublishDate']).date()
    arc_date = dateutil.parser.parse(last_published_covers[x]['createdDate']).date()
    diff_days = (pub_date-arc_date).days
    
#    if arc_date > datetime.date(2016, 8, 15):
    ext = '.jpg'
#    else:
#        ext = '.png'

    img = str(rank) + ext
    try:
        download(last_published_covers[x]['path'] + '.thumb.319.319.jpg', img)#'/jcr:content/renditions/cq5dam.thumbnail.319.319' + ext, img)
    except requests.exceptions.HTTPError:
        img='not_found.jpg'

    print('<tr>')
    print('<td>' + str(rank) + '</td>')
    print('<td><img src="' + img + '"></img></td>')
    print('<td>' + last_published_covers[x]['originMarket'].upper() + '</td>')
    print('<td>' + last_published_covers[x]['issueTitle'].lower() + '</td>')
    print('<td>' + last_published_covers[x]['issueName'].lower() + '</td>')
    print('<td>' + pub_date.strftime('%d/%m/%Y') + '</td>')
    print('<td>' + arc_date.strftime('%d/%m/%Y') + '</td>')
    print('<td align="center">' + ('<font color="green"><b>' if diff_days >= 0 else '<font color="red">') + str(diff_days) + '</b></font></td>')
        
    #print(last_published_covers[x]['path'])
    print('</tr>')
print('<tbody>')
print('</table></body></html>')