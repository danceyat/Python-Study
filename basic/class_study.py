# let's study python class
class MyClass:
    staticMember = 0

    def __init__(self):
        pass

    def normalMethod(arg1, arg2):
        print("actually we get arg1 as caller instance, arg2 as the raw arg")

    def classMethod(arg1, arg2):
        print("we get arg1 as a class object 'MyClass', arg2 as the raw arg")

    def staticMethod(arg1, arg2):
        print("we get arg1, arg2 as raw args")

c1 = MyClass()
c2 = MyClass()
assert(hasattr(MyClass, 'staticMember'))
assert(hasattr(c1, 'staticMember'))
assert(hasattr(c2, 'staticMember'))
print(MyClass.staticMember, c1.staticMember, c2.staticMember)
c1.staticMember = 1
c1.fuckMember = 10
print(MyClass.staticMember, c1.staticMember, c2.staticMember)
MyClass.staticMember = 2
print(MyClass.staticMember, c1.staticMember, c2.staticMember)
# The only explanation is that when python tries to interpret 'obj.field = val'
# it checks if obj has attribute field. If not, python will add a field named
# 'val' and assign val to it.
MyClass.staticMember2 = 100
print(MyClass.staticMember2, c1.staticMember2, c2.staticMember2)
MyClass.staticMember2 = 101
print(MyClass.staticMember2, c1.staticMember2, c2.staticMember2)
c1.staticMember2 = 102
print(MyClass.staticMember2, c1.staticMember2, c2.staticMember2)
MyClass.staticMember2 = 103
print(MyClass.staticMember2, c1.staticMember2, c2.staticMember2)
# If an instance has attribute 'attr', then call obj.attr will get the value
# of this instance. But if it has no attribute named 'attr', the call will
# return class.attr if exists.