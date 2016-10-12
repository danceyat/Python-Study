import argparse
import json
import os
import requests
import shutil
import time
from prettytable import PrettyTable
from requests.packages.urllib3.exceptions import InsecureRequestWarning


DEBUG = False
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class City:
    def __init__(self, code, cn, pinyin="", abbr="", abbr2=""):
        self.code = code
        self.cn = cn
        self.pinyin = pinyin
        self.abbr = abbr
        self.abbr2 = abbr2


    # it's a workaround, use this to identify different cities...
    def __hash__(self):
        return self.code.__hash__()


    def __str__(self):
        return "%s %s %s %s %s" % (self.code,
            self.cn, self.pinyin, self.abbr, self.abbr2)


class Train:
    def __init__(self, name, startCity, stopCity,
        fromCity, toCity, depTime, arrTime, timeCost):
        self.name = name
        self.startCity = startCity
        self.stopCity = stopCity
        self.fromCity = fromCity
        self.toCity = toCity
        self.depTime = depTime
        self.arrTime = arrTime
        self.timeCost = timeCost
        # ticket count followed by price
        self.swz = (0, 0)
        self.tdz = (0, 0)
        self.ydz = (0, 0)
        self.edz = (0, 0)
        self.rz = (0, 0)
        self.yz = (0, 0)
        self.wz = (0, 0)
        self.gjrw = (0, 0)
        self.rw = (0, 0)
        self.yw = (0, 0)
        self.qt = (0, 0)


    def fromTrainInfo(info):
        train = Train(info["station_train_code"],
            City(info["start_station_telecode"], info["start_station_name"]),
            City(info["end_station_telecode"], info["end_station_name"]),
            City(info["from_station_telecode"], info["from_station_name"]),
            City(info["to_station_telecode"], info["to_station_name"]),
            info["start_time"],
            info["arrive_time"],
            info["lishi"])
        # TODO add ticket price
        """
        yp_ex = info["yp_ex"]
        yp_info = info["yp_info"]
        """
        train.swz = (info["swz_num"], 0)
        train.tdz = (info["tz_num"], 0)
        train.ydz = (info["zy_num"], 0)
        train.edz = (info["ze_num"], 0)
        train.rz = (info["rz_num"], 0)
        train.yz = (info["yz_num"], 0)
        train.wz = (info["wz_num"], 0)
        train.gjrw = (info["gr_num"], 0)
        train.rw = (info["rw_num"], 0)
        train.yw = (info["yw_num"], 0)
        train.qt = (info["qt_num"], 0)
        train.add1 = info["controlled_train_message"]

        return train

    def getRow(self, headers):
        row = [
            self.name,
            self.startCity.cn + " - " + self.stopCity.cn,
            self.depTime + " - " + self.arrTime,
            self.timeCost
        ]
        for header in headers:
            row.append(eval("self.%s[0]" % (header)))

        return row


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
    codeFile = os.path.dirname(os.path.abspath(__file__)) + "/city_code.txt"
    try:
        if os.path.isfile(codeFile):
            os.remove(codeFile)
        elif os.path.exists(codeFile):
            shutil.rmtree(codeFile)
    except:
        pass

    try:
        with open(codeFile, 'w') as f:
            f.write("version=%s\n" % (version))
            for item in cityCodes:
                f.write("%s|%s|%s|%s|%s\n"\
                    % (item.abbr, item.cn, item.code, item.pinyin, item.abbr2))
            if DEBUG:
                print("DEBUG: %d city codes saved to '%s', version: %s"\
                    % (len(cityCodes), codeFile, version))
    except:
        print("Error saving city code file")


def downloadCityCode(version = ""):
    cityCodes = []

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
            cityCodes.append(City(spl[2], spl[1], spl[3], spl[0], spl[4]))
        print("Update city code version from '%s' to '%s'"\
            % (version, newVersion))
        version = newVersion

    if len(version) > 0:
        saveCityCode(cityCodes, version)

    return cityCodes, version


def loadCityCode():
    cityCodes = []
    version = ""
    codeFile = os.path.dirname(os.path.abspath(__file__)) + "/city_code.txt"
    if os.path.isfile(codeFile):
        try:
            with open(codeFile, 'r') as f:
                versionLine = f.readline()
                version = versionLine[versionLine.find("=")+1:-1]
                for line in f:
                    spl = line[:-1].split("|")
                    cityCodes.append(City(spl[2],
                        spl[1], spl[3], spl[0], spl[4]))
                if DEBUG:
                    print("DEBUG: loaded %d city codes from '%s', version: %s"\
                        % (len(cityCodes), codeFile, version))
        except:
            print("Error reading city code file")
            cityCodes.clear()

    if len(cityCodes) == 0 or len(version) == 0:
        cityCodes, version = downloadCityCode()

    return cityCodes, version


def searchCityCode(codes, name):
    matches = []
    if ord(name[0]) > 255:
        # this is probably a Chinese character
        matches.extend(filter(lambda x: x.cn.startswith(name), codes))
    elif len(name) > 1:
        # at lease 2 chars shall we start searching
        matches.extend(filter(lambda x: x.pinyin.startswith(name), codes))
        matches.extend(filter(lambda x: x.abbr.startswith(name), codes))
        matches.extend(filter(lambda x: x.abbr2.startswith(name), codes))

    return list(set(matches))


def chooseOne(cities, prompt):
    if len(cities) > 1:
        print(prompt)
        count = 1
        for city in cities:
            print("%d. %s" % (count, city.cn))
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
    if r.json() == -1:
        return trains
    for trainInfo in r.json()["data"]["datas"]:
        trains.append(Train.fromTrainInfo(trainInfo))

    if DEBUG:
        print("DEBUG: %d trains parsed" % (len(trains)))
    return trains


def showTickets(trains):
    headers = set()
    HEADERS = {
        "swz": (1, "swz"),
        "tdz": (2, "tdz"),
        "ydz": (3, "ydz"),
        "edz": (4, "edz"),
        "rz": (8, "rz"),
        "yz": (9, "yz"),
        "wz": (10, "wz"),
        "gjrw": (5, "gjrw"),
        "rw": (6, "rw"),
        "yw": (7, "yw"),
        "qt": (11, "qt"),
    }
    PRE_HEADERS = [
        "train",
        "depart/arrive",
        "time",
        "time cost"
    ]
    for train in trains:
        if train.swz[0].isnumeric():
            headers.add(HEADERS["swz"][1])
        if train.tdz[0].isnumeric():
            headers.add(HEADERS["tdz"][1])
        if train.ydz[0].isnumeric():
            headers.add(HEADERS["ydz"][1])
        if train.edz[0].isnumeric():
            headers.add(HEADERS["edz"][1])
        if train.rz[0].isnumeric():
            headers.add(HEADERS["rz"][1])
        if train.yz[0].isnumeric():
            headers.add(HEADERS["yz"][1])
        if train.wz[0].isnumeric():
            headers.add(HEADERS["wz"][1])
        if train.gjrw[0].isnumeric():
            headers.add(HEADERS["gjrw"][1])
        if train.rw[0].isnumeric():
            headers.add(HEADERS["rw"][1])
        if train.yw[0].isnumeric():
            headers.add(HEADERS["yw"][1])
        if train.qt[0].isnumeric():
            headers.add(HEADERS["qt"][1])
    sortedHeaders = sorted(list(headers), key=lambda x: HEADERS[x][0])
    PRE_HEADERS.extend(sortedHeaders)
    pt = PrettyTable()
    pt._set_field_names(PRE_HEADERS)
    headerNames = []
    for displayName in sortedHeaders:
        for name in HEADERS:
            if HEADERS[name][1] == displayName:
                headerNames.append(name)
                break
    for train in trains:
        pt.add_row(train.getRow(headerNames))
    print(pt)


if __name__ == "__main__":
    parser = buildArgParser()
    args = parser.parse_args()
    if DEBUG:
        print("DEBUG: depart=%s, arrive=%s, date=%s"\
            % (args.depart, args.arrive, args.date))

    cityCodes, version = loadCityCode()
    depCity = chooseOne(searchCityCode(cityCodes, args.depart),
        "Which city is your destination?")
    arrCity = chooseOne(searchCityCode(cityCodes, args.arrive),
        "Which city is your departure?")
    date = args.date

    trains = queryTickets(depCity.code, arrCity.code, date)
    showTickets(trains)

