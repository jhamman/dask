import os
from functools import partial
import re
from operator import add, neg

import numpy as np
import pytest

pytest.importorskip("graphviz")

from dask.dot import dot_graph, label, to_graphviz

# Since graphviz doesn't store a graph, we need to parse the output
label_re = re.compile('.*\[label=(.*?) shape=.*\]')
def get_label(line):
    m = label_re.match(line)
    if m:
        return m.group(1)


dsk = {'a': 1,
       'b': 2,
       'c': (neg, 'a'),
       'd': (neg, 'b'),
       'e': (add, 'c', 'd'),
       'f': (sum, ['a', 'e'])}


def test_label():
    assert label(partial(add, 1)) == 'add'


def test_to_graphviz():
    g = to_graphviz(dsk)
    labels = list(filter(None, map(get_label, g.body)))
    assert len(labels) == 10        # 10 nodes total
    funcs = set(('add', 'sum', 'neg'))
    assert set(labels).difference(dsk) == funcs
    assert set(labels).difference(funcs) == set(dsk)


def test_aliases():
    g = to_graphviz({'x': 1, 'y': 'x'})
    labels = list(filter(None, map(get_label, g.body)))
    assert len(labels) == 2
    assert len(g.body) - len(labels) == 1   # Single edge


def test_dot_graph():
    fn = 'test_dot_graph'
    fns = [fn + ext for ext in ['.png', '.pdf', '.dot']]
    try:
        dot_graph(dsk, filename=fn)
        assert all(os.path.exists(f) for f in fns)
    finally:
        for f in fns:
            if os.path.exists(f):
                os.remove(f)
