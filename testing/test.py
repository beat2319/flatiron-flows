import shutil

def backup_data():
    src = '../data/bike_logs.db'
    dst = '../data/bike_logs2.db'

    shutil.copy(src, dst)

if __name__ == '__main__':
        backup_data()