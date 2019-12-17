import pickle

def dump(obj, file_name, *args, **kwargs):
    """Writes the pickled representation of obj to a file."""
    with open(file_name, "wb") as fp:
        pickle.dump(obj, fp, *args, **kwargs)

def dumps(obj, *args, **kwargs):
    """Alias of pickle.dumps"""
    return pickle.dumps(obj, *args, **kwargs)

def load(file_name, *args, **kwargs):
    """Loads data from file."""
    with open(file_name, 'rb') as fp:
        obj = pickle.load(fp, *args, **kwargs)
    return obj

def loads(bytes_object, *args, **kwargs):
    """Alias of pickle.loads"""
    return pickle.loads(bytes_object, *args, **kwargs)

class Pickable(object):
    def dump(self, file_name, *args, **kwargs):
        """Writes the pickled representation of self to a file."""
        dump(self, file_name, *args, **kwargs)

    def dumps(self, *args, **kwargs):
        """Returns the pickled representation of self."""
        return dumps(self)

    @staticmethod
    def load(file_name, *args, **kwargs):
        """Returns a Pickable object loaded from a file."""
        return load(file_name)

    @staticmethod
    def loads(bytes_object, *args, **kwargs):
        """Returns a Pickable object loaded from bytes."""
        return loads(bytes_object)

# Tests
import unittest
from os import remove
from os.path import isfile

class TestPickable(unittest.TestCase):
    def setUp(self):
        # Before each test
        self.pickable = Pickable()

    def tearDown(self):
        # After each test
        pass

    def test_isinstance(self):
        self.assertTrue(isinstance(self.pickable, Pickable))

    def test_dump_load(self):
        self.pickable.dump('test.pickle')
        pickled = Pickable.load('test.pickle')
        self.assertTrue(isfile('test.pickle'))
        self.assertTrue(isinstance(pickled, Pickable))
        remove('test.pickle')

    def test_dumps_loads(self):
        pickled = Pickable.loads(self.pickable.dumps())
        self.assertTrue(isinstance(pickled, Pickable))

if __name__ == '__main__':
    unittest.main()
