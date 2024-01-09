import unittest 
import main
import os
import pysftp
class TestSFTP(unittest.TestCase):  
    # def test_wrong_ip(self):
    #     SFTP_IP = '10.52.0.100'
    #     SFTP_USR = 'test'
    #     SFTP_PWD = '1234567890'
    #     cnopts = pysftp.CnOpts(knownhosts=KNOWNHOSTS_PATH)
    #     cnopts.hostkeys = None
    #     with self.assertRaises(pysftp.ConnectionException):  
    #         with pysftp.Connection(host=SFTP_IP, username=SFTP_USR, password=SFTP_PWD, cnopts=cnopts) as sftp:
    #             pass
    
    # def test_wrong_username(self):
    #     SFTP_IP = '10.52.0.123'
    #     SFTP_USR = 'wrong_username'
    #     SFTP_PWD = '1234567890'
    #     cnopts = pysftp.CnOpts(knownhosts=KNOWNHOSTS_PATH)
    #     cnopts.hostkeys = None
    #     with self.assertRaises(pysftp.AuthenticationException):  
    #         with pysftp.Connection(host=SFTP_IP, username=SFTP_USR, password=SFTP_PWD, cnopts=cnopts) as sftp:
    #             pass
    
    # def test_wrong_password(self):
    #     SFTP_IP = '10.52.0.123'
    #     SFTP_USR = 'test'
    #     SFTP_PWD = 'wrong_password'  
    #     cnopts = pysftp.CnOpts(knownhosts=KNOWNHOSTS_PATH)
    #     cnopts.hostkeys = None
    #     # Kiểm tra xem liệu một ngoại lệ AuthenticationException có được ném ra không
    #     with self.assertRaises(pysftp.AuthenticationException):  
    #         with pysftp.Connection(host=SFTP_IP, username=SFTP_USR, password=SFTP_PWD, cnopts=cnopts) as sftp:
    #             pass  
    
    def test_take_file_timestamps_of_local(self):
        local_directory = r'D:\sftp_synchnozation\local_dir_test'
        result = main.take_file_timestamps_of_local(local_directory)
        # Create a dictionary with the current timestamps of the files
        expected_result = {}
        for file in os.listdir(local_directory):
            local_file_path = os.path.join(local_directory, file)
            local_modified_timestamp = os.path.getmtime(local_file_path)  
            local_modified_timestamp = int(local_modified_timestamp) - (7*60*60)  
            expected_result[file] = local_modified_timestamp
        self.assertEqual(result, expected_result)
    
    def test_take_file_timestamps_of_remote(self):
        remote_directory = r'/'
        SFTP_IP = '10.52.0.123'
        SFTP_USR = 'test'
        SFTP_PWD = '1234567890'
        cnopts = pysftp.CnOpts(knownhosts=KNOWNHOSTS_PATH)
        cnopts.hostkeys = None
        result = main.take_file_timestamps_of_remote(remote_directory, pysftp.Connection(
            host=SFTP_IP, username=SFTP_USR, password=SFTP_PWD, cnopts=cnopts))
        expected_result = {}
        with pysftp.Connection(host=SFTP_IP, username=SFTP_USR, password=SFTP_PWD, cnopts=cnopts) as sftp:
            for attr in sftp.listdir_attr():
                name = attr.filename
                remote_modified_timestamp = int(attr.st_mtime)
                expected_result[name] = remote_modified_timestamp
        self.assertEqual(result, expected_result)

    def setUp(self):
        self.LOCAL_DIRECTORY = r'D:\sftp_synchnozation\local_dir_test'
        self.REMOTE_DIRECTORY = r'/'
        self.SFTP_IP = '10.52.0.123'
        self.SFTP_USR = 'test'
        self.SFTP_PWD = '1234567890'
        self.cnopts = pysftp.CnOpts(knownhosts=KNOWNHOSTS_PATH)
        self.cnopts.hostkeys = None

    def test_empty_local_directory(self):
        # Setup: Ensure the local directory is empty and the remote directory has files
        os.rmdir(self.LOCAL_DIRECTORY)
        os.mkdir(self.LOCAL_DIRECTORY)
        main.sync(self.LOCAL_DIRECTORY, self.REMOTE_DIRECTORY, self.SFTP_IP, 
                  self.SFTP_USR, self.SFTP_PWD, self.cnopts)
        # Assert: Check that all files from the remote directory are now in the local directory
        with pysftp.Connection(host=self.SFTP_IP, username=self.SFTP_USR, password=self.SFTP_PWD, cnopts=self.cnopts) as sftp:
            remote_files = sftp.listdir(self.REMOTE_DIRECTORY)
        local_files = os.listdir(self.LOCAL_DIRECTORY)
        self.assertCountEqual(local_files, remote_files)
        
    # def test_empty_remote_directory(self):
    #     # Setup: Ensure the local directory has files and the remote directory is empty
    #     # Call the sync function
    #     main.sync(self.LOCAL_DIRECTORY, self.REMOTE_DIRECTORY, self.SFTP_IP, self.SFTP_USR, self.SFTP_PWD, self.cnopts)


if __name__ == '__main__':
    KNOWNHOSTS_PATH = r'C:\Users\tom_pham\.ssh\known_hosts.txt'
    unittest.main(verbosity = 2)