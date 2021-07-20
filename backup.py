# Import required python libraries
import os
import time


def backup(
        database,
        host="localhost",
        user="root",
        password="",
        base_directories="backup",
        backup_name=f"backup-{time.strftime('%m-%d-%Y %H-%M-%S')}"

):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    base_path = dir_path + "\\" + base_directories + "\\" + backup_name

    if os.path.exists(dir_path + "\\" + base_directories) is False:
        os.mkdir(base_directories)

    if os.path.exists(base_path) is False:
        os.mkdir(base_directories + "\\" + backup_name)
    os.system(f"mysqldump -u{user} {database} > \"{base_path}\\{database}.sql\"")

# backup("fdr")

