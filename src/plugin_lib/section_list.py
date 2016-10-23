# from typing import List


class Node:

    def __init__(self):
        self.prev = None
        self.next = None
        self.value = None


class SectionInfo:

    def __init__(self):
        self.name = None
        self.first = None
        self.last = None


class SectionList:

    def __init__(self, sections):
        self.head = Node()
        self.tail = self.head
        self.sections = dict()
        for section in sections:
            self.sections[section] = SectionInfo()

    def add(self, section, data):
        try:
            node = Node()
            node.value = data

            sec = self.sections[section]
            if not sec.first:
                self.tail.next = node
                node.previous = self.tail
                self.tail = node
                sec.first = node
                sec.last = node
            else:
                if not sec.last.next:
                    sec.last.next = node
                    sec.last = node
                    self.tail = node
                else:
                    n = sec.last.next
                    sec.last.next = node
                    sec.last = node
                    sec.last.next = n

        except KeyError:
            KeyError("can only contain predefined keys, not:", section)

    def clear(self):
        self.head = Node()
        self.tail = self.head

    def remove(self, node):
        raise Exception("operation not supported")
