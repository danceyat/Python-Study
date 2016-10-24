import json, requests
from bs4 import BeautifulSoup
from prettytable import PrettyTable

URL_5 = "http://10.0.64.29:8080/jenkins/job/gerrit_do_verify_sprdroid5.x/"
URL_6 = "http://10.0.64.29:8080/jenkins/job/gerrit_do_verify_sprdroid6.x/"
URL_N = "http://10.0.64.29:8080/jenkins/job/gerrit_do_verify_sprdroidn/"
URL_E = "http://10.0.64.29:8080/jenkins/ajaxExecutors"
JSON_SUFFIX = "api/json"

def fetchBuildList(u):
    l = {}
    r = requests.get(u + JSON_SUFFIX)
    if r.status_code != requests.codes.ok:
        print("Fetch error.")
        return l
    j = r.json()
    if 'builds' in j:
        for b in j['builds']:
            i = {}
            r = requests.get(b['url'] + JSON_SUFFIX)
            if r.status_code == requests.codes.ok:
                j2 = r.json()
                if not j2['building']:
                    continue
                if j2['description']:
                    d = j2['description'].split()
                    i['gerrit'], i['user'] = d[0], d[1]
                i['time'] = j2['id']
                i['host'] = j2['builtOn']
            l[b['number']] = i
    return l


def fetchExecutorList():
    r = requests.post(URL_E)
    if r.status_code != requests.codes.ok:
        print("Fetch error.")
        return []
    s = BeautifulSoup(r.content, "html5lib")
    tr = s.find('table', class_='pane').tbody.tr
    executors = []
    executor = {}
    while tr is not None:
        if hasattr(tr.th, 'colspan'):
            # it's a header containing or server name or IPv4 address
            # save old executor first
            if len(executor) > 0:
                executors.append(executor)
            executor = {}
            executor['host'] = tr.th.a['href'].split('/')[-2]
            executor['task'] = []
        else:
            # body containing task info
            task = {}
            # first column is index
            td = tr.td
            task['index'] = td.text
            # second column is job name
            td = td.next_sibling
            if td.div is None:
                # this host is idle
                task['job'] = td.text
            else:
                task['job'] = td.div.a['href'].split('/')[-2]
                tips = td.table['tooltip'].split("<br>")
                task['start_time'] = tips[0][8:]
                task['remain_time'] = tips[1][27:]
                task['progress'] = td.tbody.tr.td['style']\
                    .strip(';').split(':')[1]
                # third column is job number
                td = td.next_sibling
                task['job_number'] = td.a['href'].split('/')[-2]
            executor['task'].append(task)
        tr = tr.next_sibling
    executors.append(executor)
    return executors


def prettyPrintExecutorList():
    pt = PrettyTable()
    headers = [
        'host',
        'index',
        'job',
        'number',
        'progress',
        'start',
        'remain'
    ]
    pt._set_field_names(headers)
    for executor in fetchExecutorList():
        host = True
        for task in executor['task']:
            pt.add_row([
                executor['host'] if host else "",
                task['index'],
                task['job'],
                task['job_number'] if 'job_number' in task else "",
                task['progress'] if 'progress' in task else "",
                task['start_time'] if 'start_time' in task else "",
                task['remain_time'] if 'remain_time' in task else "",
            ])
            host = False
    print(pt)


prettyPrintExecutorList()
