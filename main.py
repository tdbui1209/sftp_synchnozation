import pysftp
import os


# take list files with modified timestamp in local directory
def take_file_timestamps_of_local(local_directory):
    local_directory_files = {}
    for file in os.listdir(local_directory):
        local_file_path = os.path.join(local_directory, file)
        local_modified_timestamp = os.path.getmtime(local_file_path)  # Local time GTM+7
        local_modified_timestamp = int(local_modified_timestamp) - (7*60*60)  # minus 7 hours to match time with remote
        local_directory_files[file] = local_modified_timestamp
    return local_directory_files


# take list files with modified timestamp in remote directory
def take_file_timestamps_of_remote(remote_directory, sftp):
    remote_directory_files = {}
    for attr in sftp.listdir_attr():
        name = attr.filename
        remote_modified_timestamp = int(attr.st_mtime)
        remote_directory_files[name] = remote_modified_timestamp  # UTC
    return remote_directory_files


# synchronize
def sync():
    local_directory_files = take_file_timestamps_of_local(LOCAL_DIRECTORY)
    with pysftp.Connection(host=SFTP_IP, username=SFTP_USR, password=SFTP_PWD, cnopts=cnopts) as sftp:
        remote_directory_files = take_file_timestamps_of_remote(REMOTE_DIRECTORY, sftp)
        for file_name, timestamp in remote_directory_files.items():
            local_file_path = os.path.join(LOCAL_DIRECTORY, file_name)
            if file_name in local_directory_files.keys():
                if timestamp > local_directory_files[file_name]:
                    # remove older file at local directory, download newest file from remote directory
                    os.remove(local_file_path)
                    print('Removed:', file_name)

                    sftp.get(file_name, local_file_path, preserve_mtime=True)
                    print('Downloaded:', file_name)
            else:
                # download newest file from remote directory
                sftp.get(file_name, local_file_path, preserve_mtime=True)
                print('Downloaded:', file_name)

        for file_name in local_directory_files.keys():
            if file_name not in remote_directory_files.keys():
                local_file_path = os.path.join(LOCAL_DIRECTORY, file_name)
                # remove file if not in remote directory
                os.remove(local_file_path)
                print('Removed:', file_name)


if __name__ == '__main__':
    LOCAL_DIRECTORY = r'D:\sftp_project\local_directory'
    REMOTE_DIRECTORY = r'/'
    KNOWNHOSTS_PATH = r'C:\Users\ivan_bui\.ssh\known_hosts.txt'
    SFTP_IP = '10.52.0.123'
    SFTP_USR = 'test'
    SFTP_PWD = '1234567890'

    cnopts = pysftp.CnOpts(knownhosts=KNOWNHOSTS_PATH)
    cnopts.hostkeys = None
    sync()