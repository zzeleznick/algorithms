from __future__ import print_function

class LinkedList(object):
    """docstring for LinkedList"""
    def __init__(self, value, nxt=None):
        self.value = value
        self.nxt = nxt
    def reverse(self):
        prev = None
        cur = self
        while cur:
            tmp = cur.nxt
            cur.nxt = prev
            prev = cur
            cur = tmp
        return LinkedList(prev.value, prev.nxt)
    def __repr__(self):
        name = "LinkedList"
        items = []
        cur = self
        while cur:
            items.append(cur.value)
            cur = cur.nxt
        return "<%s: %s>" % (name, ",".join("%s" % el for el in items))

prev = LinkedList(value=0)
for i in range(1, 10):
    cur = LinkedList(i)
    cur.nxt = prev
    prev = cur

print(prev)
rev = prev.reverse()

print(rev)