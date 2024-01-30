import configparser
import logging
import logging.handlers
import os
from _datetime import datetime
import shutil
import threading
import rcon_handler


config = configparser.ConfigParser()
config.read('settings.cfg')

copy_directory = config.get('Directories', 'COPY_DIRECTORY')
backup_directory = config.get('Directories', 'BACKUP_DIRECTORY')
windows_cfg = True if config.get('OS', 'WINDOWS').lower() == "true" else False
backup_interval = int(config.get('Settings', 'BACKUP_INTERVAL_MINUTES'))*60
online_players_backup_interval = int(config.get('Settings', 'ONLINE_PLAYER_BACKUP_INTERVAL_MINUTES'))*60
is_game = True if config.get('Game','GAME') else False

if windows_cfg:
    dir_seperator = "\\"
else:
    dir_seperator = "/"


def logging_setup():
    app_log_directory = './app_logs/'
    if not os.path.exists(app_log_directory):
        os.makedirs(app_log_directory)
    log_file = 'app_logs/auto_backup.log'
    should_roll_over = os.path.isfile(log_file)
    handler = logging.handlers.RotatingFileHandler(log_file, mode='w', backupCount=5, delay=True)
    if should_roll_over:
        handler.doRollover()
    logging.basicConfig(filename=log_file,
                        filemode='a',
                        format='[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d}\n%(levelname)s - %(message)s',
                        level=logging.INFO)
    logging.info(f"""
Initialize config files from settings.cfg
copy_directory = {copy_directory}
backup_directory = {backup_directory}
windows_cfg = {windows_cfg}
backup_interval = {backup_interval}
online_players_backup_interval = {online_players_backup_interval}
is_game = {is_game}
rcon_host_address = {rcon_handler.rcon_host_address}
rcon_port = {rcon_handler.rcon_port}
rcon_password = {bool(rcon_handler.rcon_password)}
""")
    logging.info(f"Application started")


def get_time():
    now = datetime.now()
    formatted_now = now.strftime("%Y-%m-%d_%H-%M-%S")
    return formatted_now


def run_backup():
    print(f"[{datetime.now()}] Running backup ... ")
    logging.info(f"[{datetime.now()}] Running backup ... ")
    check_config()
    backup_destination_folder_name = get_time()
    backup_destination_directory_path = backup_directory + dir_seperator + backup_destination_folder_name
    shutil.copytree(copy_directory, backup_destination_directory_path)
    if os.path.exists(backup_destination_directory_path):
        print(f"Backup to {backup_destination_directory_path} complete")
        logging.info(f"Backup to {backup_destination_directory_path} complete")
    else:
        print(f"Error creating {backup_destination_directory_path}, exiting.")
        logging.error(f"Error creating {backup_destination_directory_path}, exiting.")
        exit(0)


def check_config():
    if not os.path.exists(copy_directory):
        print(f"Copy directory {copy_directory} doesn't exist. Exiting.")
        logging.error(f"Copy directory {copy_directory} doesn't exist. Exiting.")
        exit(0)
    if not os.path.exists(backup_directory):
        print(f"Backup directory {backup_directory} doesn't exist. Exiting.")
        logging.error(f"Backup directory {backup_directory} doesn't exist. Exiting.")
        exit(0)


def normal_backups():
    logging.info(f"run_schedule task started, backup process is not handling game data")
    while not exit_event.is_set():
        logging.info(f"Backup interval is backup_interval {backup_interval}")
        run_backup()
        exit_event.wait(backup_interval)


def game_backups():
    logging.info(f"game_backups thread started, backup process is handling game data")
    while not exit_event.is_set():
        logging.info(f"Checking {rcon_handler.game} server for players ... ")
        this_backup_interval = check_for_players_and_set_backup_interval()
        logging.info(f"Backup interval is this_backup_interval {this_backup_interval}")
        run_backup()
        exit_event.wait(this_backup_interval)


def check_for_players_and_set_backup_interval():
    list_of_players = rcon_handler.query_game_server("ShowPlayers")
    logging.info(f"list_of_players: {list_of_players}")
    if list_of_players[1]:
        this_backup_interval = online_players_backup_interval
        logging.info(f"There are players online, backup interval set to {this_backup_interval} seconds")
        print(f"There are players online, backup interval set to {this_backup_interval} seconds")
    else:
        this_backup_interval = backup_interval
        print(f"There are no players online, backup interval set to {this_backup_interval} seconds")
    return this_backup_interval


def help_message():
    print("Usage: ")
    print("     Type 'backup' to run backup immediately")
    print("     Type 'quit' or press CTRL-C to exit")
    if is_game:
        print("     Type 'rcon' to enter rcon mode")


def user_input():
    try:
        while not exit_event.is_set():
            user_keyboard_input = input()
            if user_keyboard_input.lower() == 'quit':
                break
            elif user_keyboard_input.lower() == 'backup':
                run_backup()
            elif user_keyboard_input.lower() == 'rcon' and is_game:
                logging.info("User entered rcon mode")
                print("rcon mode enabled, type command to submit to server, "
                      "type 'stop' to end rcon mode or type 'help'.")
                rcon_handler.game_commmands()
                while True:
                    rcon_command = input()
                    if rcon_command.lower() == 'stop':
                        print("Exited rcon mode")
                        logging.info('User exited rcon mode')
                        break
                    if rcon_command.lower() == 'help':
                        rcon_handler.game_commmands()
                        print("Type 'stop' to end rcon mode\n")
                    else:
                        query = rcon_handler.query_game_server(*rcon_command.split())
                        print(query)
                        logging.info(f'rcon query executed: {rcon_command}')
                        logging.info(f"Response from game server: {query}")
            else:
                print(f"Input not recognized")
                help_message()
    except UnicodeDecodeError:
        pass


exit_event = threading.Event()
normal_backups_thread = threading.Thread(target=normal_backups)
game_backup_thread = threading.Thread(target=game_backups)
user_input_thread = threading.Thread(target=user_input)


def run():
    logging_setup()
    print(f"""
----------------------------------------------------
Backing up files from: {copy_directory}
Backup directory: {backup_directory}
----------------------------------------------------
""")

    help_message()

    try:
        if is_game:
            game_backup_thread.start()
        else:
            normal_backups_thread.start()

        user_input_thread.start()
        user_input_thread.join()

    except KeyboardInterrupt:
        print(f"Shutting down ... ")
    finally:
        exit_event.set()
        if is_game:
            game_backup_thread.join()
        else:
            normal_backups_thread.join()
        print("Done!")


if __name__ == '__main__':
    run()
