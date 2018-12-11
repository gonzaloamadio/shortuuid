from shortuuid.main import ShortUUID as _su
from shortuuid.main import uuid, encode, decode

def foo():
    s = _su()
    print(s.uuid())

def foo2():
    print(_su().uuid())

def foo3():
    print(uuid())

foo()
foo2()
foo3()
