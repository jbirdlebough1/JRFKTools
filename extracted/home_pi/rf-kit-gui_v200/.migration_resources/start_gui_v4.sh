#!/bin/bash
cd /home/pi/rf-kit-statics

if [[ -f rf-kit-gui.log && # logfile exists
      $(stat -c%s rf-kit-gui.log) -gt 0 && # logfile is not empty
      # do not start a new logfile directly after a migration:
      -f .rf-kit-gui.log.ts && # if the file did not exist, this would mean that this script version runs for the first time so we come from a migration
      .migration.json -ot .rf-kit-gui.log.ts ]] # application has already been started since the last migration
then
  mv rf-kit-gui.log rf-kit-gui.log.old
fi


touch .rf-kit-gui.log.ts # this file will be newer than .migration.json until the next migration, so we know that the application has been started already since the last migration
python3 gui_starter.py &>> rf-kit-gui.log