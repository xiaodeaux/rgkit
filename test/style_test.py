import pep8
import unittest
from glob import glob

class TestCodeFormat(unittest.TestCase):
    def test_pep8_conformance(self):
        files = glob('*.py') + glob('test/*.py')

        pep8style = pep8.StyleGuide()
        pep8style.options.ignore += ('E302', 'E501')
        result = pep8style.check_files(files)
        self.assertEqual(result.total_errors, 0, "Found code style errors (and warnings).")
