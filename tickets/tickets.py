import argparse
import json
import os
import requests
import shutil
import time
from functools import reduce
from prettytable import PrettyTable
from requests.packages.urllib3.exceptions import InsecureRequestWarning


requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
DEBUG = False
CITY_FILE = os.path.dirname(os.path.abspath(__file__)) + "/city_code.json"

def validateDate(s):
    try:
        time.strptime(s, "%Y-%m-%d")
    except ValueError:
        msg = "Date not in format 'YYYY-MM-DD': '{0}'".format(s)
        raise argparse.ArgumentTypeError(msg)

    return s


def buildArgParser():
    parser = argparse.ArgumentParser(
        description="A command tool to query tickets from 12306.")
    parser.add_argument("depart", help="where you depart from")
    parser.add_argument("arrive", help="where you arrive at")
    parser.add_argument("date", type=validateDate,
        help="the day you depart(must have format YYYY-MM-DD)")
    parser.add_argument("-z", action="store_true", default=False,
        help="choose trains whose names start with 'Z'")
    parser.add_argument("-k", action="store_true", default=False,
        help="choose trains whose names start with 'K'")
    parser.add_argument("-t", action="store_true", default=False,
        help="choose trains whose names start with 'T'")
    parser.add_argument("-d", action="store_true", default=False,
        help="choose trains whose names start with 'D'")
    parser.add_argument("-g", action="store_true", default=False,
        help="choose trains whose names start with 'G'")
    return parser


def saveCityCode(cityCodes, version):
    try:
        if os.path.isfile(CITY_FILE):
            os.remove(CITY_FILE)
        elif os.path.exists(CITY_FILE):
            shutil.rmtree(CITY_FILE)
    except:
        pass

    try:
        content = {
            'version': version,
            'cities': cityCodes
        }
        with open(CITY_FILE, 'w') as f:
            json.dump(content, f, indent=4)
            if DEBUG:
                print("DEBUG: %d city codes saved to '%s', version: %s"\
                    % (len(cityCodes), CITY_FILE, version))
    except:
        print("Error saving city code file")


def downloadCityCode(version = ""):
    cityCodes = []

    if len(version) == 0:
        url = "https://kyfw.12306.cn/otn/lcxxcx/init"
        versionKey = "station_version="
        r = requests.get(url, verify=False)
        if r.status_code != requests.codes.ok:
            print("Error downloading city code info version")
            return [], ""
        start = r.text.find(versionKey) + len(versionKey)
        stop = r.text.find('"', start)
        newVersion = r.text[start:stop]
        if DEBUG:
            print("DEBUG: fetched city code version: %s" % newVersion)

    if newVersion > version:
        url = "https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=%s" % (newVersion)
        r = requests.get(url, verify=False)
        if r.status_code != requests.codes.ok:
            print("Error downloading version file")
            return [], ""
        start = r.text.find("'") + 1
        stop = r.text.rfind("'")
        # start+1 to ignore first '@'
        for phrase in r.text[start+1:stop].split("@"):
            spl = phrase.split("|")
            cityCodes.append({
                'code': spl[2],
                'cn': spl[1],
                'pinyin': spl[3],
                'abbr': spl[0],
                'abbr2': spl[4]
            })
        print("Update city code version from '%s' to '%s'"\
            % (version, newVersion))
        version = newVersion

        if len(version) > 0:
            saveCityCode(cityCodes, version)

    return cityCodes, version


def loadCityCode():
    cityCodes, version = [], ""
    if os.path.isfile(CITY_FILE):
        try:
            with open(CITY_FILE, 'r') as f:
                content = json.load(f)
                cityCodes, version = content['cities'], content['version']
                if DEBUG:
                    print("DEBUG: loaded %d city codes from '%s', version: %s"\
                        % (len(cityCodes), CITY_FILE, version))
        except json.JSONDecodeError as msg:
            print("Error parsing city code file: " + str(msg))
        except:
            print("Error reading city code file")
            cityCodes, version = [], ""

    if len(cityCodes) == 0 or len(version) == 0:
        cityCodes, version = downloadCityCode()

    return cityCodes, version


def searchCityCode(codes, name):
    matches = {}

    def _addCity(it):
        for city in it:
            if city['code'] not in matches:
                matches[city['code']] = city

    if ord(name[0]) > 255:
        # this is probably a Chinese character
        _addCity(filter(lambda x: x['cn'].startswith(name), codes))
    elif len(name) > 1:
        # at lease 2 chars shall we start searching
        _addCity(filter(lambda x: x['pinyin'].startswith(name), codes))
        _addCity(filter(lambda x: x['abbr'].startswith(name), codes))
        _addCity(filter(lambda x: x['abbr2'].startswith(name), codes))

    return list(matches.values())


def chooseOne(cities, prompt):
    if len(cities) > 1:
        print(prompt)
        count = 1
        for city in cities:
            print("%d. %s" % (count, city['cn']))
            count += 1
        print(">>> ", end="")
        num = input()
        try:
            if 0 < int(num) < count:
                depCity = cities[int(num)-1]
            else:
                raise Exception()
        except:
            print("Invalid input %s" % num)
            depCity = None
    else:
        depCity = cities[0]

    return depCity


def queryTickets(depart, arrive, date):
    if DEBUG:
        print("DEBUG: querying tickets with depart=%s, arrive=%s, date=%s"\
            % (depart, arrive, date))

    trains = []
    url = "https://kyfw.12306.cn/otn/lcxxcx/query?purpose_codes=ADULT&queryDate=%s&from_station=%s&to_station=%s"
    r = requests.get(url % (date, depart, arrive), verify=False)
    if r.status_code != requests.codes.ok:
        print("Error downloading ticket info")
        return trains
    if r.json() == -1 or not r.json()['data']['flag']:
        return trains
    trains = r.json()['data']['datas']

    if DEBUG:
        print("DEBUG: %d trains parsed" % (len(trains)))
    return trains


def showTickets(trains):
    class Column:
        def __init__(self, displayName, valueName, order):
            self.displayName = displayName
            self.valueName = valueName
            self.order = order

        def __hash__(self):
            return self.order.__hash__()

        def __repr__(self):
            return self.displayName

    headers = []
    TICKET_COLUMNS = [
        Column('swz', 'swz_num', 1),
        Column('tdz', 'tz_num', 2),
        Column('ydz', 'zy_num', 3),
        Column('edz', 'ze_num', 4),
        Column('gjrw', 'gr_num', 5),
        Column('rw', 'rw_num', 6),
        Column('yw', 'yw_num', 7),
        Column('rz', 'rz_num', 8),
        Column('yz', 'yz_num', 9),
        Column('wz', 'wz_num', 10),
        Column('qt', 'qt_num', 11)
    ]
    PRE_HEADERS = [
        "Train",
        "From - To",
        "Depart - Arrive",
        "Time Cost"
    ]
    for col in TICKET_COLUMNS:
        for train in trains:
            if train[col.valueName].isnumeric():
                headers.append(col)
                break

    PRE_HEADERS.extend(headers)
    pt = PrettyTable()
    pt._set_field_names(PRE_HEADERS)
    for train in trains:
        row = [
            train['station_train_code'],
            train['from_station_name'] + " - " + train['to_station_name'],
            train['start_time'] + " - " + train['arrive_time'],
            train['lishi']
        ]
        for col in headers:
            row.append(train[col.valueName])
        pt.add_row(row)
    print(pt)


if __name__ == "__main__":
    parser = buildArgParser()
    args = parser.parse_args()
    if DEBUG:
        print("DEBUG: depart=%s, arrive=%s, date=%s"\
            % (args.depart, args.arrive, args.date))

    cityCodes, version = loadCityCode()
    depCity = chooseOne(searchCityCode(cityCodes, args.depart),
        "Which city will your arrive at?")
    arrCity = chooseOne(searchCityCode(cityCodes, args.arrive),
        "Which city will your depart from?")
    date = args.date

    trains = queryTickets(depCity['code'], arrCity['code'], date)

    if len(trains) > 0:
        showTickets(trains)
    else:
        print("No tickets left")
