import json
from json import JSONEncoder, JSONDecoder


class MyObject:
    def __init__(self, intAttr=0, strAttr=""):
        self.intAttr = intAttr
        self.strAttr = strAttr


class MyDerivedObject(MyObject):
    def __init__(self, intAttr=0, strAttr="", listAttr=[]):
        self.intAttr = intAttr
        self.strAttr = strAttr
        self.listAttr = listAttr


    def __repr__(self):
        l = [self.intAttr, self.strAttr]
        l.extend(self.listAttr)
        return str(l)


"""
    type() checks type only
    isinstance() also checks inheriting tree
"""
def type_isinstance_test():
    obj1 = MyObject()
    obj2 = MyDerivedObject()
    print("type(obj1) is MyObject: {}".format(type(obj1) is MyObject))
    print("isinstance(obj1, MyObject): {}".format(isinstance(obj1, MyObject)))
    print("type(obj2) is MyObject: {}".format(type(obj2) is MyObject))
    print("isinstance(obj2, MyObject): {}".format(isinstance(obj2, MyObject)))


"""
    this checks JSON serializablility
    use JSONEncoder to convert an obj to a serializable object
    use JSONDecoder or object_hook to convert a JSON object to an obj
        if object_hook is used, list object [] will be ignored
        if JSONDecoder is used, the entire JSON string is passed to it
"""
def json_test():
    # dump JSON object
    obj = ['elem1', 100, { "name2": "value2", "name1": "value1" }]
    print(json.dumps(obj, indent=4, sort_keys=True))

    # after overriding __repr__(), we can print this object
    obj2 = MyDerivedObject(300, "obj2", ["Mon", "Tue", "Wed"])
    print(obj2)

    # but still cannot serialize this object
    obj.append(obj2)
    try:
        print(json.dumps(obj, indent=4, sort_keys=True))
    except Exception as msg:
        print("dumps() failed: " + str(msg))

    # but we can use JSONEncoder
    class MyEncoder(JSONEncoder):
        def default(self, o):
            if type(o) is MyObject:
                return o.__dict__
            elif type(o) is MyDerivedObject:
                l = [o.intAttr, o.strAttr]
                l.extend(o.listAttr)
                return l
            else:
                return o
    obj3 = MyObject(500, "obj3")
    obj.append(obj3)
    jsonStr = json.dumps(obj, cls=MyEncoder, indent=4, sort_keys=True)
    print(jsonStr)

    # we can use a function hook to get these things
    def fromJson(obj):
        print("parsing obj: {}".format(str(obj)))
        if "intAttr" in obj and "strAttr" in obj:
            return MyObject(obj["intAttr"], obj["strAttr"])
        else:
            return obj
    jsonObj1 = json.loads(jsonStr, object_hook=fromJson)
    print(jsonObj1)
    class MyDecoder(JSONDecoder):
        def decode(self, s):
            # JSON passes the entire string...
            print(s)
            return s
    jsonObj2 = json.loads(jsonStr, cls=MyDecoder)
    #print(jsonObj2)


#type_isinstance_test()
json_test()

