#!/usr/bin/env python3.11

import json
import re
import time
import os
from mysql import connector

class Compiler:
    PATH = './ram/'
    conn = connector.connect(
        user='',
        host='',
        database='BackupManager',
        password='',
        port='',
        connect_timeout=3600,
    )
    cursor = conn.cursor(dictionary=True)
    alert_keys = [
        'Alerts.Main.connect-agent-failed', #0
        'Errors.Main.disksafe-soft-quota-has-been-reached', #1
        'Alerts.Main.one-or-more-selected-devices-not-eligible', #2
        'Alerts.Main.one-or-more-devices-failed-backup', #3
        'Alerts.Main.errors-encountered-during-backup', #4
        'Messages.Main.no-sql-server-databases-found', #5
        'Messages.Main.failed-to-lock-and-flush-one-or-more', #6
        'Alerts.Main.dpp-disabled', #7
        'Messages.Main.disksafe-hard-quota-has-been-reached', #8
        'Messages.socket-timed-out', #9
        'Alerts.Main.one-or-more-partition-table-replications-failed', #10
        'Alerts.Main.one-or-more-database-instances-failed-discovery', #11
        'Messages.Main.failed-to-backup-one-or-more', #12
        'Alerts.Main.disk-safe-closed-alert', #13
        'Errors.Main.unexpected-error-executing-task', #14
        'Alerts.Main.problem-checking-disk-usage', #15
        'Errors.Main.not-all-recovery-points-were-merged-successfully', #16
        'Alerts.Main.one-or-more-files-failed-restore', #17
        'Errors.Main.could-not-verify-recovery-point', #18
        'Alerts.Main.task-interrupted', #19
        'Alerts.Main.failed-to-protect-one-or-more-control-panel-instances', #20
        'Alerts.Main.authenticate-agent-failed', #21
        'Alerts.Main.error-getting-device-list', #22
        'Alerts.Main.no-eligible-devices-found', #23
        'Alerts.Main.one-or-more-databases-failed-to-restore', #24
        'Alerts.Main.could-not-restore-database', #25
        'Messages.Main.unable-to-perform-multi-volume-snapshot', #26
        'Alerts.Main.failed-to-restore-one-or-more-devices', #27
        'Errors.Main.task-interrupted-by-unclean-shutdown', #28
        'Messages.UI.invalid-policy', #29
        'Messages.UI.device-is-below-soft-quota', #30
        'Alerts.Main.errors-encountered-while-merging-recovery-point', #31
    ]
    type_keys = [
        'DATA_PROTECTION_POLICY', #0
        'MERGE_RECOVERY_POINTS', #1
        'FILE_RESTORE' #2
    ]

    agents_data: str = ''
    server_data: str = ''
    report_search: str = ''
    report_data: str = ''

    servers_index = []

    def log_key(self, key):
        with open('/home/abe/logs/compile_keys', 'a') as log:
            log.write(key + '\n')

    def get_agents(self):
        cursor = self.cursor

        cursor.execute("""SELECT RANK() OVER(order by id) - 1 as 'id', server_id, type, description,
            hostname, agent_version, driver_version, os_version, os_type, port, enabled FROM agents;""")
        db_agents = cursor.fetchall()

        cursor.execute(f"SELECT * FROM servers;")
        db_servers = cursor.fetchall()

        cursor.execute("""SELECT RANK() OVER(order by disk_safes.id) - 1 as 'id', i_agents.index as 'aid', i_volumes.index as 'vid',
            description, path, re_points_limit, re_points, latest_rp, size, deltas, soft_quota,
            hard_quota FROM disk_safes LEFT JOIN i_agents on i_agents.id = disk_safes.agent_id
            LEFT JOIN i_volumes on i_volumes.id = disk_safes.volume_id ORDER BY disk_safes.id;""")
        db_ds = cursor.fetchall()

        cursor.execute("""SELECT i_disk_safes.index as 'did', name, cast(last as char), schedule,
        frequency, daily, hourly, minutely, monthly, weekly, yearly FROM policies
        LEFT JOIN i_disk_safes on i_disk_safes.id = policies.disk_safe_id;""")
        db_policies = cursor.fetchall()

        cursor.execute("""SELECT reports_emails.email, i_agents.index FROM reports_emails
        LEFT JOIN reports_agents on reports_agents.report_id = reports_emails.report_id
        LEFT JOIN i_agents on i_agents.id = reports_agents.agent_id WHERE i_agents.id IS NOT NULL
        ORDER BY reports_emails.email;""")
        db_a_emails = cursor.fetchall()

        cursor.execute("""SELECT name, i_agents.index FROM reports LEFT JOIN reports_agents
        ON reports_agents.report_id = reports.id LEFT JOIN i_agents ON i_agents.id =
        reports_agents.agent_id WHERE i_agents.id IS NOT NULL AND name NOT LIKE '%quota%';""")
        db_a_rid = cursor.fetchall()

        cursor.execute("""SELECT RANK() OVER(order by tasks.id) - 1 as 'id', server_id, i_agents.index,
        state, type, completion, execution, schedule FROM tasks LEFT JOIN i_agents on i_agents.id =
        tasks.agent_id ORDER BY i_agents.index, execution;""")
        db_tasks = cursor.fetchall()

        cursor.execute("""SELECT alert_key, i_tasks.index FROM alerts LEFT JOIN i_tasks ON
        alerts.task_id = i_tasks.id WHERE alert_key NOT LIKE '%report%';""")
        db_alerts = cursor.fetchall()

        # Compile active disk safe
        active_ds = []
        gig = 1024 ** 3
        for i in range(len(db_policies)):
            if db_policies[i]['did'] is not None:
                ds = db_ds[db_policies[i]['did']]
                ds['pid'] = i
                ds['size'] = ds['size'] // gig
                ds['deltas'] = ds['deltas'] // gig
                ds['soft_quota'] = ds['soft_quota'] // gig
                ds['hard_quota'] = ds['hard_quota'] // gig
                active_ds.append(ds)

        # Link disk safe data to agents
        for ds in active_ds:
            db_agents[ds['aid']]['did'] = ds['id']
            db_agents[ds['aid']]['size'] = ds['size']
            db_agents[ds['aid']]['soft_quota'] = ds['soft_quota']
            db_agents[ds['aid']]['hard_quota'] = ds['hard_quota']
            if db_agents[ds['aid']]['description'].lower() != ds['description'].lower():
                db_agents[ds['aid']]['ddes'] = ds['description']


        # Link report id to agents
        for rid in db_a_rid:
            if bool(re.search(r'\d', rid['name'])) and 'rapid' not in rid['name'].lower():
                if db_agents[rid['index']]['description'].lower() != rid['name'].lower():
                    db_agents[rid['index']]['rdes'] = rid['name']

        # Link emails to agents
        for email in db_a_emails:
            if 'email' not in db_agents[email['index']]:
                db_agents[email['index']]['email'] = [email['email']]
            else:
                db_agents[email['index']]['email'].append(email['email'])

        task_history = []
        running = []
        last = 3.141 # Throw way away number
        # Compile last backup and current running action
        for task in db_tasks:
            if (task['type'] == 'DATA_PROTECTION_POLICY' and
                task['state'] != 'DUPLICATE' and
                task['state'] != 'RUNNING'):
                if task['index'] == last:
                    if len(task_history) > 0 and task_history[-1]['execution'] < task['execution']:
                        task_history[-1] = task
                else:
                    task_history.append(task)
                last = task['index']
            if (task['index'] != None and
                task['type'] != 'DISK_SAFE_VERIFICATION' and
                task['state'] == 'RUNNING'):
                running.append(task)

        sorted_task = sorted(db_tasks, key=lambda task: task['id'])
        # Link alert keys to tasks
        # Prone to fail if new alert that is not part of alert_keys array
        for alert in db_alerts:
            if alert['alert_key'] in self.alert_keys:
                key = self.alert_keys.index(alert['alert_key'])
            else:
                self.log_key(alert['alert_key'])
                key = 4
            if 'alert_keys' not in sorted_task[alert['index']]:
                sorted_task[alert['index']]['alert_keys'] = [key]
            else:
                sorted_task[alert['index']]['alert_keys'].append(key)

        # Link error state and alert key to agents
        # Shallow copy behavior inherits alert keys from sorted_task
        # Unsafe behavior
        for task in task_history:
            if task['state'] == 'ERROR' and task['index'] != None:
                db_agents[task['index']]['error'] = True
            if 'alert_keys' in task:
                db_agents[task['index']]['alert_keys'] = task['alert_keys']

        # Link running task to agents
        for task in running:
            if 'RESTORE' in task['type']:
                db_agents[task['index']]['rn_type'] = 2
            elif task['type'] in self.type_keys:
                db_agents[task['index']]['rn_type'] = self.type_keys.index(task['type'])

        # Generate Backup Server data
        servers_index = []
        server_data = []
        for server in db_servers:
            s_in = [server['id'], server['hostname'].replace('r1server','').replace('.backup.net','')]
            server_data.append(s_in)
            servers_index.append(server['id'])
        self.servers_index = servers_index

        search_db = []
        # Generate complete agents dataset
        for agent in db_agents:
            flags = 0
            s = {}
            index = agent['id']
            s_index = servers_index.index(agent['server_id'])

            s['d'] = agent['description']
            s['h'] = agent['hostname']
            if 'ddes' in agent:
                s['dd'] = agent['ddes']
            if 'rdes' in agent:
                s['r'] = agent['rdes']
            if 'email' in agent:
                s['e'] = agent['email']
            if 'alert_keys' in agent:
                s['a'] = agent['alert_keys']

            if 'did' not in agent:
                flags = 1
            flags = flags << 1 # 10

            if agent['enabled'] == 0:
                flags += 1
            flags = flags << 2 # 1100

            if agent['type'] == 'PHYSICAL':
                pass
            elif agent['type'] == 'VM':
                flags += 1
            else:
                flags += 2 # 1101
            flags = flags << 1 # 11010
            if 'error' in agent:
                flags += 1
            flags = flags << 2
            if agent['os_type'] == 'WINDOWS':
                pass
            elif agent['os_type'] == 'LINUX':
                flags += 1
            else:
                flags += 2
            flags = flags << 2
            if 'rn_type' in agent:
                flags += agent['rn_type'] + 1

            if 'size' in agent:
                size = agent['size']
            else:
                size = 0
            if 'soft_quota' in agent:
                soft = agent['soft_quota']
            else:
                soft = 0
            if 'hard_quota' in agent:
                hard = agent['hard_quota']
            else:
                hard = 0

            s['n'] = [index, s_index, flags, size, soft, hard]

            search_db.append(s)

        self.agents_data = json.dumps(search_db, separators=(',', ':'))
        self.server_data = json.dumps(server_data, separators=(',', ':'))

    def lazy(self):
        cursor = self.cursor

        cursor.execute("""SELECT i_reports.index, reports.server_id, reports.name, reports.last,
        reports_emails.email, agents.description, reports.info, reports.subject FROM reports JOIN i_reports
        ON i_reports.id = reports.id LEFT JOIN reports_emails ON reports_emails.report_id = reports.id
        LEFT JOIN reports_agents ON reports_agents.report_id = reports.id LEFT JOIN agents
        ON reports_agents.agent_id = agents.id ORDER BY reports.id;""")
        db_reports = cursor.fetchall()

        cursor.execute("""SELECT sendgrid.to_email, sendgrid.status, sendgrid.subject,
        sendgrid.open_count, sendgrid.click_count, sendgrid.last_time, sendgrid.event,
        sendgrid.reason FROM sendgrid INNER JOIN (SELECT to_email, MAX(last_time) AS
        'lt' FROM sendgrid WHERE status not like 'processing' GROUP BY to_email) AS
        sub ON sub.to_email = sendgrid.to_email AND sub.lt = sendgrid.last_time;""")
        db_sendgrid = cursor.fetchall()

        reports_collapsed = []
        last = -1
        for report in db_reports:
            if report['index'] != last:
                if report['email'] == None:
                    report['email'] = []
                else:
                    report['email'] = [report['email']]
                if report['description'] == None:
                    report['description'] = []
                else:
                    report['description'] = [report['description']]
                reports_collapsed.append(report)
            else:
                if report['email'] not in reports_collapsed[-1]['email'] and report['email'] != None:
                    reports_collapsed[-1]['email'].append(report['email'])
                if report['description'] not in reports_collapsed[-1]['description'] and report['description'] != None:
                    reports_collapsed[-1]['description'].append(report['description'])
            last = report['index']

        sendgrid_emails = []
        for sg_email in db_sendgrid:
            sendgrid_emails.append(sg_email['to_email'])

        # 1 ms
        for report in reports_collapsed:
            for email in report['email']:
                try:
                    sg_i = sendgrid_emails.index(email)
                    if db_sendgrid[sg_i]['status'] == 'delivered':
                        report['status'] = 0
                    else:
                        report['status'] = 1
                        if db_sendgrid[sg_i]['reason'] != None:
                            report['reason'] = email + ': ' +  db_sendgrid[sg_i]['reason']
                        else:
                            report['reason'] = ''
                        report['event'] = db_sendgrid[sg_i]['event']
                    report['opened'] = bool(db_sendgrid[sg_i]['open_count'])
                except ValueError:
                    continue

        sorted_reports = sorted(reports_collapsed, key=lambda report: (report['name'], report['server_id']))
        infos = []
        quotas = []
        for report in sorted_reports:
            if report['info'] == 1:
                infos.append(report)
            else:
                quotas.append(report)

        info_pointer = 0
        quota_pointer = 0
        search_criteria = []
        while not (info_pointer >= len(infos) and quota_pointer >= len(quotas)):
            s = {}
            str_size = len(infos[info_pointer]['name'].strip())
            if quota_pointer >= len(quotas) or infos[info_pointer]['name'].strip() < quotas[quota_pointer]['name'].strip()[:str_size]:
                s['n'] = infos[info_pointer]['name']
                s['e'] = infos[info_pointer]['email']
                s['d'] = infos[info_pointer]['description']
                s['i'] = [infos[info_pointer]['index']]
                search_criteria.append(s)
                info_pointer += 1
            elif info_pointer >= len(infos) or infos[info_pointer]['name'].strip() > quotas[quota_pointer]['name'].strip()[:str_size]:
                s['n'] = quotas[quota_pointer]['name']
                s['e'] = quotas[quota_pointer]['email']
                s['d'] = quotas[quota_pointer]['description']
                s['i'] = [quotas[quota_pointer]['index']]
                search_criteria.append(s)
                quota_pointer += 1
            else:
                if infos[info_pointer]['server_id'] == quotas[quota_pointer]['server_id']:
                    s['n'] = infos[info_pointer]['name']
                    s['e'] = infos[info_pointer]['email']
                    s['d'] = infos[info_pointer]['description']
                    s['i'] = [infos[info_pointer]['index'], quotas[quota_pointer]['index']]
                    search_criteria.append(s)
                else:
                    s['n'] = infos[info_pointer]['name']
                    s['e'] = infos[info_pointer]['email']
                    s['d'] = infos[info_pointer]['description']
                    s['i'] = [infos[info_pointer]['index']]
                    search_criteria.append(s)
                    q = {}
                    q['n'] = quotas[quota_pointer]['name']
                    q['e'] = quotas[quota_pointer]['email']
                    q['d'] = quotas[quota_pointer]['description']
                    q['i'] = [quotas[quota_pointer]['index']]
                    search_criteria.append(q)
                info_pointer += 1
                quota_pointer += 1

        reports_data = []
        for report in reports_collapsed:
            r = {}
            r['n'] = report['name']
            r['s'] = self.servers_index.index(report['server_id'])
            r['e'] = report['email']
            if len(report['description']) > 0:
                r['d'] = report['description']
            r['t'] = report['info']
            if 'opened' in report:
                r['o'] = int(report['opened'])
            if 'reason' in report:
                r['r'] = report['reason']
            reports_data.append(r)

        self.report_search = json.dumps(search_criteria, separators=(',', ':'))
        self.report_data = json.dumps(reports_data, separators=(',', ':'))

    def write_out(self):
        time_stamp = str(int(time.time()))
        with open(self.PATH + time_stamp , 'w') as file:
            file.write(self.agents_data + '\n')
            file.write(self.server_data + '\n')
            file.write('//END' + '\n')
            file.write(self.report_search + '\n')
            file.write(self.report_data + '\n')

    def clean(self):
        list_of_files = os.listdir(self.PATH)
        list_of_ints = []
        for file in list_of_files:
            list_of_ints.append(int(file))
        list_of_ints.sort(reverse=True)
        if len(list_of_ints) >= 4:
            for file in list_of_ints[3:]:
                os.unlink(self.PATH + str(file))

if __name__ == '__main__':
    compiler = Compiler()
    compiler.get_agents()
    compiler.lazy()
    compiler.write_out()
    compiler.clean()
