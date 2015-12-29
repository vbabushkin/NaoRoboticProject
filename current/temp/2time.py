from timer0 import timeout
from position import detectTar
@timeout(5)
def some():
    return detectTar("me.local","LArm")
    
def me():
    try:
        some()
    except Exception, e:
        print "time out"
##c=detectTar("me.local","LArm")
me()
print '1 done to 2'

@timeout(3)
def some1():
    return detectTar("me.local","LArm")
def me1():
    try:
        some1()
    except Exception, e:
        print "time out for 1 also"
me1()
