import shortuuid.main as _su

def foo():
    s = _su.ShortUUID()
    print(s.uuid())

def foo2():
    print(_su.ShortUUID().uuid())

foo()
foo2()
