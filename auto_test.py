import pysftp
import os
import time
import main

def create_file(file_name, remote_directory, sftp):
    # create a file on remote server
    # sftp.open() is used to create a file directly on remote server
    with sftp.open(remote_directory + file_name, 'w') as f:
        f.write("This is a test file.")
    time.sleep(1)

def main_test(LOCAL_DIRECTORY, REMOTE_DIRECTORY, SFTP_IP, SFTP_USR, SFTP_PWD, cnopts):
    file_name = "test_file.txt"
    with pysftp.Connection(host=SFTP_IP, username=SFTP_USR, password=SFTP_PWD, cnopts=cnopts) as sftp:
        create_file(file_name, REMOTE_DIRECTORY, sftp)
    main.sync(SFTP_IP, SFTP_USR, SFTP_PWD, cnopts, LOCAL_DIRECTORY, REMOTE_DIRECTORY)

if __name__ == '__main__':
    LOCAL_DIRECTORY = r'D:\sftp_synchnozation\local_dir_test'
    REMOTE_DIRECTORY = r'/test2/'
    KNOWNHOSTS_PATH = r'C:\Users\tom_pham\.ssh\known_hosts.txt'
    SFTP_IP = '10.52.0.123'
    SFTP_USR = 'test'
    SFTP_PWD = '1234567890'
    cnopts = pysftp.CnOpts(knownhosts=KNOWNHOSTS_PATH)
    cnopts.hostkeys = None
    main_test(LOCAL_DIRECTORY, REMOTE_DIRECTORY, SFTP_IP, SFTP_USR, SFTP_PWD, cnopts)