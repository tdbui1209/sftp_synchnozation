import pysftp
import os
import stat
import time


# recursive listdir on local directory
def recursive_listdir_local(directory):
    file_attrs = {}
    for file in os.listdir(directory):
        file_path = os.path.join(directory, file)
        if os.path.isdir(file_path):
            file_attrs[file] = recursive_listdir_local(file_path)
        else:
            local_modified_timestamp = os.path.getmtime(file_path)
            local_modified_timestamp = int(local_modified_timestamp)
            file_attrs[file] = local_modified_timestamp
    return file_attrs


# take list files with modified timestamp in local directory
def take_file_timestamps_of_local(local_directory):
    local_directory_files = {}
    local_directory_files = recursive_listdir_local(local_directory)
    return local_directory_files


# recursive listdir on remote directory
def recursive_listdir_remote(sftp, directory):
    file_attrs = {}
    for attr in sftp.listdir_attr(directory):
        if stat.S_ISDIR(attr.st_mode):
            sftp.chdir(directory + '/' + attr.filename)
            file_attrs[attr.filename] = recursive_listdir_remote(sftp, '.')
            sftp.chdir('..')
        else:
            remote_modified_timestamp = int(attr.st_mtime)
            file_attrs[attr.filename] = remote_modified_timestamp
    return file_attrs


# take list files with modified timestamp in remote directory
def take_file_timestamps_of_remote(sftp, remote_directory='/'):
    remote_directory_files = {}
    sftp.chdir(remote_directory)
    remote_directory_files = recursive_listdir_remote(sftp, remote_directory)
    return remote_directory_files


# recursive synchronize
def recursive_sync(local_directory, local_directory_files, remote_directory_files, sftp):
    os.makedirs(local_directory, exist_ok=True)
    for file_name, timestamp in remote_directory_files.items():
        local_file_path = os.path.join(local_directory, file_name)
        if file_name in local_directory_files.keys():
            if isinstance(timestamp, dict):
                sftp.chdir(file_name)
                recursive_sync(local_file_path, local_directory_files[file_name], timestamp, sftp)
                sftp.chdir('..')
            else:
                if timestamp > local_directory_files[file_name]:
                    # remove older file at local directory, download newest file from remote directory
                    os.remove(local_file_path)
                    print('Removed:', local_file_path)

                    sftp.get(file_name, local_file_path, preserve_mtime=True)
                    print('Downloaded:', local_file_path)
        else:
            if isinstance(timestamp, dict):
                os.makedirs(local_file_path, exist_ok=True)
                sftp.chdir(file_name)
                recursive_sync(local_file_path, {}, timestamp, sftp)
                sftp.chdir('..')
            else:
                # download newest file from remote directory
                sftp.get(file_name, local_file_path, preserve_mtime=True)
                print('Downloaded:', local_file_path)

    for file_name in local_directory_files.keys():
        if file_name not in remote_directory_files.keys():
            local_file_path = os.path.join(local_directory, file_name)
            # remove file if not in remote directory
            os.remove(local_file_path)
            print('Removed:', local_file_path)


# synchronize
def sync(sftp_ip, sftp_usr, sftp_pwd, cnopts, local_directory, remote_directory):
    print('Synchronizing...')
    local_directory_files = take_file_timestamps_of_local(local_directory)
    try:
        sftp = pysftp.Connection(host=sftp_ip, username=sftp_usr, password=sftp_pwd, cnopts=cnopts)
    except:
        print('Connection failed!')
    else:
        print('Connection successful!\n')
        t1 = time.time()
        with sftp:
            remote_directory_files = take_file_timestamps_of_remote(sftp, remote_directory)
            recursive_sync(local_directory, local_directory_files, remote_directory_files, sftp)
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
    sync(SFTP_IP, SFTP_USR, SFTP_PWD, cnopts, LOCAL_DIRECTORY, REMOTE_DIRECTORY)
