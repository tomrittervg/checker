
# Enter the following into your cron

First edit the ... to your path

    * * * * * .../checker/main.py -m cron -c minute >/dev/null 2>&1
    0 * * * * .../checker/main.py -m cron -c hour   >/dev/null 2>&1
    0 0 * * * .../checker/main.py -m cron -c day    >/dev/null 2>&1
    0 0 12 * * .../checker/main.py -m cron -c day_noon >/dev/null 2>&1
  
