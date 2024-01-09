import unittest
import os

class TestSFTP(unittest.TestCase):  
    def test_connection(self):
        local_file_path = r''
        self.assertTrue(os.path.exists(local_file_path))
