import unittest
import os
import pysftp
from automatic_sync_sftp import AutoSynchronize
import hashlib
import shutil


class TestStringMethods(unittest.TestCase):
    def setUp(self):
        self.LOCAL_DIRECTORY = r'D:\sftp_project\local_directory'
        self.REMOTE_DIRECTORY = r'/'
        self.KNOWNHOSTS_PATH = r'C:\Users\ivan_bui\.ssh\known_hosts.txt'
        self.HOST = '10.52.0.123'
        self.USERNAME = 'test'
        self.PASSWORD = '1234567890'
        self.CNOPTS = pysftp.CnOpts(knownhosts=self.KNOWNHOSTS_PATH)
        self.CNOPTS.hostkeys = None

    def test_1(self):
        """
        Trường hợp: local ko có gì, sẽ lấy hết toàn bộ file từ remote về
        """
        folder_name_local = 'test_1'
        folder_name_remote = r'/test_1'
        os.makedirs(folder_name_local, exist_ok=True)

        sftp = pysftp.Connection(host=self.HOST, username=self.USERNAME,
                                    password=self.PASSWORD, cnopts=self.CNOPTS)
        sftp.mkdir(folder_name_remote)
        
        with open('test.txt', 'w') as f:
            f.write('test')
        
        with open('test.txt', 'r') as f:
            original_hash = hashlib.sha3_256(f.read().encode('utf-8')).hexdigest()

        sftp.put('test.txt', folder_name_remote + '/test.txt')

        auto_sync = AutoSynchronize(self.HOST, self.USERNAME, self.PASSWORD, folder_name_local,
                                    folder_name_remote, self.KNOWNHOSTS_PATH)
        auto_sync.synchronize()

        with open(folder_name_local + '/test.txt', 'r') as f:
            synced_hash = hashlib.sha3_256(f.read().encode('utf-8')).hexdigest()

        self.assertTrue(os.path.exists(folder_name_local + '/test.txt'))
        self.assertEqual(original_hash, synced_hash)

        shutil.rmtree(folder_name_local)
        os.remove('test.txt')
        sftp.rmdir(folder_name_remote)


if __name__ == '__main__':
    unittest.main(verbosity=2)