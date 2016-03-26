from collections import OrderedDict
from pprint import pprint

from systemd import journal
from datetime import datetime
from datetime import time

j_started = 'Journal started'
j_stopped = 'Journal stopped'
start_date = datetime(2016, 3, 7)

start_journal = journal.Reader()
# end_journal = journal.Reader()
start_journal.seek_realtime(start_date)
start_journal.add_match(MESSAGE=j_started)
start_journal.add_match(MESSAGE=j_stopped)
times = OrderedDict()
# start_journal.get_next(skip=2)

for entry in start_journal:
    boot_id = entry['_BOOT_ID'].hex
    if not times.get(boot_id):
        times[boot_id] = {'skip_boot': False}
        session = times.get(boot_id)
    elif session['skip_boot']:
        continue
    if entry['MESSAGE'] == j_started:
        if time(8, 0) <= entry['__REALTIME_TIMESTAMP'].time() <= time(17, 0):
            session['start_time'] = entry['__REALTIME_TIMESTAMP']
            session['end_time'] = None
        else:
            session['skip_boot'] = True
            continue
    elif session.get('start_time'):
        session['end_time'] = entry['__REALTIME_TIMESTAMP']
        session['working_time'] = session['end_time'] - session['start_time']

current_date = start_date
working_days_list = [[False, False]]
for session in times.items():
    if not session[1]['skip_boot']:
        current_date = session[1]['start_time'].date()
        working_time = session[1]['working_time']
        previous_session = working_days_list[-1]
        if not working_days_list or current_date != previous_session[0]:
            working_days_list.append([current_date, working_time])

        elif current_date == previous_session[0]:
            working_time = previous_session[1] + working_time
            working_days_list[-1] = current_date, working_time

for working_day in working_days_list[1:]:
    print('{}: {}'.format(working_day[0], working_day[1]))
