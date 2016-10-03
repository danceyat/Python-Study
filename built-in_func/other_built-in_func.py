"""
abs(x)
Return the absolute value of a number. The argument may be an integer or a floating point number. If the argument is a complex number, its magnitude is returned.
"""
print(abs(-3.8))
# magnitude of a complex number be returned
print(abs(3 + 4j))


"""
all(iterable)
Return True if all elements of the iterable are true (or if the iterable is empty). Equivalent to:
"""
def all(iterable):
    for element in iterable:
        if not element:
            return False
    return True
# it's just like 'any x in R, ...' in mathematics


"""
any(iterable)¶
Return True if any element of the iterable is true. If the iterable is empty, return False. Equivalent to:
"""
def any(iterable):
    for element in iterable:
        if element:
            return True
    return False
# it's just like 'there exists an x in R, ...' in mathematics


"""
bin(x)
Convert an integer number to a binary string. The result is a valid Python expression. If x is not a Python int object, it has to define an __index__() method that returns an integer.
"""
print(bin(74))
# call object.__index__() if presents, which must return an integer


"""
class bool([x])
Return a Boolean value, i.e. one of True or False. x is converted using the standard truth testing procedure. If x is false or omitted, this returns False; otherwise it returns True. The bool class is a subclass of int (see Numeric Types — int, float, complex). It cannot be subclassed further. Its only instances are False and True (see Boolean Values).
"""
# so when calling bool(x), I am actually constructing an bool object...
# the same as bytearray, bytes(immutable bytearray)


"""
chr(i)
Return the string representing a character whose Unicode code point is the integer i. For example, chr(97) returns the string 'a', while chr(957) returns the string 'ν'. This is the inverse of ord().

The valid range for the argument is from 0 through 1,114,111 (0x10FFFF in base 16). ValueError will be raised if i is outside that range.
"""
print(chr(97))
print(chr(956))
# wonderful!!
print(ord(chr(956)))


"""
class complex([real[, imag]])
Return a complex number with the value real + imag*1j or convert a string or number to a complex number. If the first parameter is a string, it will be interpreted as a complex number and the function must be called without a second parameter. The second parameter can never be a string. Each argument may be any numeric type (including complex). If imag is omitted, it defaults to zero and the constructor serves as a numeric conversion like int and float. If both arguments are omitted, returns 0j.
"""
print(complex())


"""
delattr(object, name)
This is a relative of setattr(). The arguments are an object and a string. The string must be the name of one of the object’s attributes. The function deletes the named attribute, provided the object allows it. For example, delattr(x, 'foobar') is equivalent to del x.foobar.
"""
class DelAttrTest:
    def __init__(self):
        self.member0 = 10
    def foo(self):
        pass
    member1 = 3
delAttrTest = DelAttrTest()
# instance field can be deleted
print(hasattr(delAttrTest, 'member0'))
delattr(delAttrTest, 'member0')
print(hasattr(delAttrTest, 'member0'))
# while static field cannot
print(hasattr(delAttrTest, 'member1'))
# this raises AttributeError
try:
    delattr(delAttrTest, 'member1')
except AttributeError:
    print("cannot delete static field")


"""
dir([object])
Without arguments, return the list of names in the current local scope. With an argument, attempt to return a list of valid attributes for that object.

If the object has a method named __dir__(), this method will be called and must return the list of attributes. This allows objects that implement a custom __getattr__() or __getattribute__() function to customize the way dir() reports their attributes.

If the object does not provide __dir__(), the function tries its best to gather information from the object’s __dict__ attribute, if defined, and from its type object. The resulting list is not necessarily complete, and may be inaccurate when the object has a custom __getattr__().

The default dir() mechanism behaves differently with different types of objects, as it attempts to produce the most relevant, rather than complete, information:

If the object is a module object, the list contains the names of the module’s attributes.
If the object is a type or class object, the list contains the names of its attributes, and recursively of the attributes of its bases.
Otherwise, the list contains the object’s attributes’ names, the names of its class’s attributes, and recursively of the attributes of its class’s base classes.
"""


# divmod returns a tuple of quotient and modulus
print(5 / 3, 5 // 3, 5 % 3)
print(divmod(5, 3))


"""
enumerate(iterable, start=0)
Return an enumerate object. iterable must be a sequence, an iterator, or some other object which supports iteration. The __next__() method of the iterator returned by enumerate() returns a tuple containing a count (from start which defaults to 0) and the values obtained from iterating over iterable.
"""
seasons = ['Spring', 'Summer', 'Fall', 'Winter']
print(list(enumerate(seasons)))
print(list(enumerate(seasons, start=1)))
"""
Equivalent to:

def enumerate(sequence, start=0):
    n = start
    for elem in sequence:
        yield n, elem
        n += 1
"""


"""
filter(function, iterable)
Construct an iterator from those elements of iterable for which function returns true. iterable may be either a sequence, a container which supports iteration, or an iterator. If function is None, the identity function is assumed, that is, all elements of iterable that are false are removed.

Note that filter(function, iterable) is equivalent to the generator expression (item for item in iterable if function(item)) if function is not None and (item for item in iterable if item) if function is None.

See itertools.filterfalse() for the complementary function that returns elements of iterable for which function returns false.
"""


"""
globals()
Return a dictionary representing the current global symbol table. This is always the dictionary of the current module (inside a function or method, this is the module where it is defined, not the module from which it is called).

locals()
Update and return a dictionary representing the current local symbol table. Free variables are returned by locals() when it is called in function blocks, but not in class blocks.
"""


"""
len(s)
Return the length (the number of items) of an object. The argument may be a sequence (such as a string, bytes, tuple, list, or range) or a collection (such as a dictionary, set, or frozen set).
"""


"""
class property(fget=None, fset=None, fdel=None, doc=None)¶
Return a property attribute.

fget is a function for getting an attribute value. fset is a function for setting an attribute value. fdel is a function for deleting an attribute value. And doc creates a docstring for the attribute.

A typical use is to define a managed attribute x:

class C:
    def __init__(self):
        self._x = None

    def getx(self):
        return self._x

    def setx(self, value):
        self._x = value

    def delx(self):
        del self._x

    x = property(getx, setx, delx, "I'm the 'x' property.")

If c is an instance of C, c.x will invoke the getter, c.x = value will invoke the setter and del c.x the deleter.

If given, doc will be the docstring of the property attribute. Otherwise, the property will copy fget‘s docstring (if it exists). This makes it possible to create read-only properties easily using property() as a decorator:

class Parrot:
    def __init__(self):
        self._voltage = 100000

    @property
    def voltage(self):
        """Get the current voltage."""
        return self._voltage

The @property decorator turns the voltage() method into a “getter” for a read-only attribute with the same name, and it sets the docstring for voltage to “Get the current voltage.”

A property object has getter, setter, and deleter methods usable as decorators that create a copy of the property with the corresponding accessor function set to the decorated function. This is best explained with an example:

class C:
    def __init__(self):
        self._x = None

    @property
    def x(self):
        # I'm the 'x' property.
        return self._x

    @x.setter
    def x(self, value):
        self._x = value

    @x.deleter
    def x(self):
        del self._x

This code is exactly equivalent to the first example. Be sure to give the additional functions the same name as the original property (x in this case.)

The returned property object also has the attributes fget, fset, and fdel corresponding to the constructor arguments.

Changed in version 3.5: The docstrings of property objects are now writeable.
"""
