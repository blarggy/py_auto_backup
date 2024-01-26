import configparser
import os
from _datetime import datetime
import shutil
import threading


config = configparser.ConfigParser()
config.read('settings.cfg')

copy_directory = config.get('Directories', 'COPY_DIRECTORY')
backup_directory = config.get('Directories', 'BACKUP_DIRECTORY')
windows_cfg = config.get('OS', 'WINDOWS')
backup_interval = int(config.get('Settings', 'BACKUP_INTERVAL_MINUTES'))*60

if windows_cfg:
    dir_seperator = "\\"
else:
    dir_seperator = "/"


def get_time():
    now = datetime.now()
    formatted_now = now.strftime("%Y-%m-%d_%H-%M-%S")
    return formatted_now


def run_backup():
    print(f"[{datetime.now()}] Running backup ... ")
    check_config()
    backup_destination_folder_name = get_time()
    backup_destination_directory_path = backup_directory + dir_seperator + backup_destination_folder_name
    shutil.copytree(copy_directory, backup_destination_directory_path)
    if os.path.exists(backup_destination_directory_path):
        print(f"Backup to {backup_destination_directory_path} complete")
    else:
        print(f"Error creating {backup_destination_directory_path}, exiting.")
        exit(0)


def check_config():
    if not os.path.exists(copy_directory):
        print(f"Copy directory {copy_directory} doesn't exist. Exiting.")
        exit(0)
    if not os.path.exists(backup_directory):
        print(f"Backup directory {backup_directory} doesn't exist. Exiting.")
        exit(0)


def run_schedule():
    while not exit_event.is_set():
        run_backup()
        exit_event.wait(backup_interval)


exit_event = threading.Event()
schedule_thread = threading.Thread(target=run_schedule)


def run():
    print(f'Backing up files from: {copy_directory}')
    print(f'Backup directory: {backup_directory}')
    print("*** Press 'esc' key to exit ***")
    try:
        schedule_thread.start()
        while True:
            if input().lower == 'esc':
                break
    except KeyboardInterrupt:
        print(f"Shutting down ... ")
    finally:
        exit_event.set()
        schedule_thread.join()
        print("Done!")


if __name__ == '__main__':
    run()
