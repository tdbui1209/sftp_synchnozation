from ftplib import FTP
import os
from datetime import datetime


LOCAL_DIRECTORY = r'D:\ftp_project\local_directory'
FTP_IP = '10.52.201.58'
FTP_USR = 'duong'
FTP_PWD = 'duong'

ftp_client = FTP(FTP_IP, FTP_USR, FTP_PWD)


# take list files with modified timestamp in local directory
local_directory_files = {}
for file in os.listdir(LOCAL_DIRECTORY):
    local_file_path = os.path.join(LOCAL_DIRECTORY, file)
    local_modified_timestamp = os.path.getmtime(local_file_path)  # Local time GTM+7
    local_modified_timestamp = float(local_modified_timestamp) - (7*60*60)  # minus 7 hours to match time with remote
    local_directory_files[file] = local_modified_timestamp


# take list files with modified timestamp in remote directory
remote_directory_files = {}
files = ftp_client.mlsd()
for file in files:
    name = file[0]
    remote_modified_timestamp = file[1]['modify']

    # timestamp.split('.')[0] for skip .%f
    datetime_str = remote_modified_timestamp.split('.')[0]  # GMT+0
    remote_modified_timestamp = datetime.strptime(datetime_str , '%Y%m%d%H%M%S').timestamp()
    remote_modified_timestamp = float(remote_modified_timestamp)
    remote_directory_files[name] = remote_modified_timestamp


# Synchronize
for file_name, timestamp in remote_directory_files.items():
    local_file_path = os.path.join(LOCAL_DIRECTORY, file_name)
    if file_name in local_directory_files.keys():
        if timestamp > local_directory_files[file_name]:
            # remove older file at local directory, download newest file from remote directory
            os.remove(local_file_path)
            print('Removed:', file_name)

            localfile = open(local_file_path, 'wb')
            ftp_client.retrbinary(f'RETR {file_name}', localfile.write)
            print('Downloaded:', file_name)
            localfile.close()
    else:
        # download newest file from remote directory
        localfile = open(local_file_path, 'wb')
        ftp_client.retrbinary(f'RETR {file_name}', localfile.write)
        print('Downloaded:', file_name)
        localfile.close()

for file_name in local_directory_files.keys():
    if file_name not in remote_directory_files.keys():
        local_file_path = os.path.join(LOCAL_DIRECTORY, file_name)
        # remove file if not in remote directory
        os.remove(local_file_path)
        print('Removed:', file_name)