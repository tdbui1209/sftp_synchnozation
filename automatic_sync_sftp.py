import pysftp
import os
import stat
import time
import shutil

class AutoSynchronize:
    def __init__(self, host, username, password, local_directory, remote_directory, known_hosts):
        '''
        host: sftp ip address
        username: sftp username
        password: sftp password
        local_directory: local directory path
        remote_directory: remote directory path
        known_hosts: known_hosts file path
        '''
        self.HOST = host
        self.USERNAME = username
        self.PASSWORD = password
        self.LOCAL_DIRECTORY = local_directory
        self.REMOTE_DIRECTORY = remote_directory
        self.KNOWNHOSTS_PATH = known_hosts
        self.CNOPTS = pysftp.CnOpts(knownhosts=self.KNOWNHOSTS_PATH)
        self.CNOPTS.hostkeys = None

    def traversal_local_directory(self, local_directory):
        """
        Recursively traverses the specified local directory and returns a dictionary of file attributes.

        Parameters:
        - local_directory (str): The path of the local directory to be traversed.

        Returns:
        dict: A dictionary of file attributes.
        """
        file_attrs = {}
        for file in os.listdir(local_directory):
            file_path = os.path.join(local_directory, file)
            if os.path.isdir(file_path):
                file_attrs[file] = self.traversal_local_directory(file_path)
            else:
                local_modified_timestamp = os.path.getmtime(file_path)
                local_modified_timestamp = int(local_modified_timestamp)
                file_attrs[file] = local_modified_timestamp
        return file_attrs
    
    def traversal_remote_directory(self, sftp, remote_directory):
        """
        Recursively traverses the specified remote directory and returns a dictionary of file attributes.

        Parameters:
        - sftp (pysftp.Connection): The sftp connection object.
        - remote_directory (str): The path of the remote directory to be traversed.

        Returns:
        dict: A dictionary of file attributes.
        """
        file_attrs = {}
        for attr in sftp.listdir_attr(remote_directory):
            if stat.S_ISDIR(attr.st_mode):
                sftp.chdir(remote_directory + '/' + attr.filename)
                file_attrs[attr.filename] = self.traversal_remote_directory(sftp, '.')
                sftp.chdir('..')
            else:
                remote_modified_timestamp = int(attr.st_mtime)
                file_attrs[attr.filename] = remote_modified_timestamp
        return file_attrs
    
    def take_file_timestamps_of_local(self, local_directory):
        """
        Returns a dictionary of file attributes in the specified local directory.

        Parameters:
        - local_directory (str): The path of the local directory.

        Returns:
        dict: A dictionary of file attributes.
        """
        local_directory_files = {}
        local_directory_files = self.traversal_local_directory(local_directory)
        return local_directory_files
    
    def take_file_timestamps_of_remote(self, sftp, remote_directory='/'):
        """
        Returns a dictionary of file attributes in the specified remote directory.

        Parameters:
        - sftp (pysftp.Connection): The sftp connection object.
        - remote_directory (str): The path of the remote directory.

        Returns:
        dict: A dictionary of file attributes.
        """
        remote_directory_files = {}
        sftp.chdir(remote_directory)
        remote_directory_files = self.traversal_remote_directory(sftp, remote_directory)
        return remote_directory_files
    
    def recursive_sync(self, local_directory, local_directory_files, remote_directory_files, sftp):
        """
        Recursively synchronizes the specified local directory and remote directory.

        Parameters:
        - local_directory (str): The path of the local directory.
        - local_directory_files (dict): A dictionary of file attributes in the local directory.
        - remote_directory_files (dict): A dictionary of file attributes in the remote directory.
        - sftp (pysftp.Connection): The sftp connection object.
        """
        os.makedirs(local_directory, exist_ok=True)
        for file_name, timestamp in remote_directory_files.items():
            local_file_path = os.path.join(local_directory, file_name)
            if file_name in local_directory_files.keys():
                if isinstance(timestamp, dict):
                    sftp.chdir(file_name)
                    self.recursive_sync(local_file_path, local_directory_files[file_name], timestamp, sftp)
                    sftp.chdir('..')
                else:
                    if timestamp > local_directory_files[file_name]:
                        # remove older file at local directory, download newest file from remote directory
                        if os.path.isdir(local_file_path):
                            shutil.rmtree(local_file_path)
                        else:
                            os.remove(local_file_path)
                        print('Removed:', local_file_path)

                        sftp.get(file_name, local_file_path, preserve_mtime=True)
                        print('Downloaded:', local_file_path)
            else:
                if isinstance(timestamp, dict):
                    os.makedirs(local_file_path, exist_ok=True)
                    sftp.chdir(file_name)
                    self.recursive_sync(local_file_path, {}, timestamp, sftp)
                    sftp.chdir('..')
                else:
                    # download newest file from remote directory
                    sftp.get(file_name, local_file_path, preserve_mtime=True)
                    print('Downloaded:', local_file_path)

        for file_name in local_directory_files.keys():
            if file_name not in remote_directory_files.keys():
                local_file_path = os.path.join(local_directory, file_name)
                # remove file if not in remote directory
                if os.path.isdir(local_file_path):
                    shutil.rmtree(local_file_path)
                else:
                    os.remove(local_file_path)
                print('Removed:', local_file_path)

    def synchronize(self):
        """
        Synchronizes the specified local directory and remote directory.
        """
        print('Synchronizing...')
        local_directory_files = self.take_file_timestamps_of_local(self.LOCAL_DIRECTORY)
        try:
            sftp = pysftp.Connection(host=self.HOST, username=self.USERNAME, password=self.PASSWORD, cnopts=self.CNOPTS)
        except:
            print('Connection failed!')
        else:
            print('Connection successful!\n')
            t1 = time.time()
            with sftp:
                remote_directory_files = self.take_file_timestamps_of_remote(sftp, self.REMOTE_DIRECTORY)
                self.recursive_sync(self.LOCAL_DIRECTORY, local_directory_files, remote_directory_files, sftp)
            t2 = time.time()
            print('\nSynchronization was completed!')
            print('Synchronization time:', t2 - t1, 'second(s)')


if __name__ == '__main__':
    LOCAL_DIRECTORY = r'D:\sftp_project\local_directory'
    REMOTE_DIRECTORY = r'/'
    KNOWNHOSTS_PATH = r'C:\Users\ivan_bui\.ssh\known_hosts.txt'
    SFTP_IP = '10.52.0.123'
    SFTP_USR = 'test'
    SFTP_PWD = '1234567890'

    cnopts = pysftp.CnOpts(knownhosts=KNOWNHOSTS_PATH)
    cnopts.hostkeys = None
    
    auto_sync = AutoSynchronize(SFTP_IP, SFTP_USR, SFTP_PWD, LOCAL_DIRECTORY, REMOTE_DIRECTORY, KNOWNHOSTS_PATH)
    auto_sync.synchronize()
