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

import os
import plistlib
import shutil
import glob

def write_file(filename, entry):
    backupfilename = filename + '.tzbak'
    if not os.path.exists(backupfilename):
        print '	Backing up %s to %s' % (filename, backupfilename)
        shutil.move(filename, backupfilename)
        print '	Writing new entry at %s' % filename
        plistlib.writePlist(entry, filename)
    else:
        print '	No write because backup already exists at %s' % backupfilename
    print ''

def main():
    config_path = '~/Library/Group Containers/*.dayoneapp/data/Preferences/dayone.plist'
    dayone_conf = plistlib.readPlist(glob.glob(os.path.expanduser(config_path))[0])
    base_dir = str(dayone_conf['JournalPackageURL'] + '/entries')

    timezone = 'Asia/Tokyo'

    files = os.listdir(base_dir)
    files[:] = [file for file in files if file.endswith('.doentry')]

    for file in files:
        filename = os.path.join(base_dir, file)
        entry = plistlib.readPlist(filename)
        tz = entry['Time Zone']
        country = entry['Location']['Country']

        if country == 'Japan':
            if tz != timezone:
                print 'Wrong timezone %s for location %s in entry %s' % (tz, country, entry['UUID'])
                entry['Time Zone'] = timezone
                write_file(filename, entry)

    print 'Done.'

if __name__ == "__main__":
    main()