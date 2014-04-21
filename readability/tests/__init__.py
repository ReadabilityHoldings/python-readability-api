import os

test_root = os.path.dirname(os.path.realpath(__file__))


def load_test_content(filename):
    """
    Load the contents of the file for use in tests.

    Useful for canned responses / post content
    """
    with open(os.path.join(test_root, filename), 'r') as testfile:
        return testfile.read()
