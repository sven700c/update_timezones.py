# update_timezones.py
# forked from Aleksandr Pasechnik
# updates by Sven Simon
#
# Goes through the Day One jounal and sets the Time Zone of each entry that
# doesn't correspond with the location to the value of the *timezone* variable. 
# Makes a backup copy of each entry it modified by adding a '.tzbak' to the filename.
# Ignores any entry that already has a '.tzbak' version.
#
# NOTE: base_dir may need to be adjusted to the correct Journal_dayone location
# NOTE: It is probably a good idea to have a full journal backup just in case
# something goes wrong

from os import path, listdir
from sys import argv
import argparse
import plistlib
from shutil import move
import glob


def write_file(filename, entry):
    backup_filename = filename + '.tzbak'
    if not path.exists(backup_filename):
        print '	Backing up %s to %s' % (filename, backup_filename)
        move(filename, backup_filename)
        print '	Writing new entry at %s' % filename
        plistlib.writePlist(entry, filename)
    else:
        print '	No write because backup already exists at %s' % backup_filename
    print ''


def check_timezone(entry, location):
    tz_dict = {
        'Japan': 'Asia/Tokyo',
        'Singapore': 'Asia/Singapore',
        'Switzerland': 'Europe/Zurich'
    }

    timezone = tz_dict[location]
    tz = entry['Time Zone']
    country = entry['Location']['Country']
    if country == location and tz != timezone:
        print 'Wrong timezone %s for location %s in entry %s' % (tz, country, entry['UUID'])
        entry['Time Zone'] = timezone
        entry['Starred'] = 'true'
        return entry


def main(argv):
    args = argparse.ArgumentParser()
    args.add_argument('-n', '--nowrite', action='store_true', help='dry run')
    args.add_argument('-p', '--path', help='override default journal entries path')
    args.add_argument('-l', '--location', help='country for which to check timezone entries', default='Japan')
    args.add_argument('-e', '--entry', help='print out single entry')
    flag = args.parse_args()

    if flag.path:
        if path.exists(flag.path):
            base_dir = path.expanduser(flag.path)
        else:
            print("path does not exist")
            exit()
    else:
        config_path = '~/Library/Group Containers/*.dayoneapp/data/Preferences/dayone.plist'
        dayone_conf = plistlib.readPlist(glob.glob(path.expanduser(config_path))[0])
        base_dir = str(dayone_conf['JournalPackageURL'] + '/entries')

    if flag.entry:
        filename = path.join(base_dir, str(flag.entry + '.doentry'))
        print(plistlib.readPlist(filename))

    else:
        files = listdir(base_dir)
        files[:] = [file for file in files if file.endswith('.doentry')]

        for file in files:
            filename = path.join(base_dir, file)
            entry = plistlib.readPlist(filename)
            update = check_timezone(entry, flag.location)
            if update and not flag.nowrite:
                write_file(filename, update)

    print 'Done.'

if __name__ == "__main__":
    main(argv)