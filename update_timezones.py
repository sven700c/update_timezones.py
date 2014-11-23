# update_timezones.py
# forked from Aleksandr Pasechnik
# updates by Sven Simon
#
# Goes through the Day One journal and sets the Time Zone of each entry that
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
from pytz import country_names, country_timezones


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


def get_tzdict():
    tz_dict = {}
    for country_code in country_names:
        if country_timezones.has_key(country_code):
            tz_dict[country_names[country_code]] = country_timezones[country_code]
    return tz_dict


def check_timezone(entry, location):
    tz_dict = get_tzdict()
    timezone = tz_dict[location][0]
    tz = entry['Time Zone']
    country = entry['Location']['Country']
    if country == location and tz != timezone:
        print 'Wrong timezone %s for location %s in entry %s' % (tz, country, entry['UUID'])
        entry['Time Zone'] = timezone
        entry['Starred'] = 'true'
        return entry


def default_dir():
    config_path = '~/Library/Group Containers/*.dayoneapp/data/Preferences/dayone.plist'
    dayone_conf = plistlib.readPlist(glob.glob(path.expanduser(config_path))[0])
    return str(dayone_conf['JournalPackageURL'] + '/entries')


def main(argv):
    args = argparse.ArgumentParser()
    args.add_argument('-w', '--write', action='store_true', help='write changes to files')
    args.add_argument('-p', '--path', help='override default journal entries path')
    args.add_argument('-l', '--location', help='country for which to check timezone entries', default='Japan')
    args.add_argument('-e', '--entry', help='print out single entry')
    flag = args.parse_args()

    base_dir = default_dir()

    if flag.path:
        if path.exists(flag.path):
            base_dir = path.expanduser(flag.path)
        else:
            print("path does not exist")
            exit()

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
            if update and flag.write:
                write_file(filename, update)

    print 'Done.'


if __name__ == "__main__":
    main(argv)