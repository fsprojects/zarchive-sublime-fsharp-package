# Copyright (c) 2014, Guillermo López-Anglada. Please see the AUTHORS file for details.
# All rights reserved. Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.)

from collections import deque


class CircularArray(object):

    def __init__(self, initial_data, *args, **kwargs):
        self.data = deque(initial_data)

    def forward(self):
        item = self.data.popleft()
        self.data.append(item)
        return item

    def backward(self):
        item = self.data.pop()
        self.data.appendleft(item)
        return item

    def __len__(self):
        return len(self.data)
