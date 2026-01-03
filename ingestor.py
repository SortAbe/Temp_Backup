#!/usr/bin/env python3.11

import datetime
import json
import requests
import time
import xmltodict
import compile

from datetime import date, timedelta
from mysql import connector

PORT = ''
USER = ''
PASS = ''

if USER == None or PASS == None:
    print('Creds missing!')
    exit(1)

class DiskSafeClosed(Exception):
    pass

conn = connector.connect(
    user='',
    host='localhost',
    database='',
    password='',
    port='3306',
    connect_timeout=3600,
)

with open('/home/abe/data/servers.json', 'r') as file:
    hosts = json.load(file)

compiler = compile.Compiler()
def compile_data():
    compiler.get_agents()
    compiler.lazy()
    compiler.write_out()
    compiler.clean()

def log_error(host, act, error):
    with open('/home/abe/logs/ingestor.log', 'a') as log:
        log.write(f'=========ERROR==========\n')
        log.write(f'{datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}\n')
        log.write(f'{host}\n')
        log.write(f'{act}\n')
        log.write(f'{str(error)[0:150]}\n')
        log.write(f'=====END OF ERROR=====\n')

def check(url):
    requests.packages.urllib3.disable_warnings()
    headers = {"Connection": "close"}
    try:
        response = requests.head('https://' + url, headers=headers, verify=False, allow_redirects=False, timeout=1)
        if response.status_code < 400:
            return True
        else:
            return False
    except requests.exceptions.Timeout:
        return False
    except requests.exceptions.ConnectionError:
        return False

def get_session():
    session = requests.Session()
    session.auth = (USER, PASS)
    session.keep_alive = 2
    session.headers.update({'content-type': 'text/xml'})
    return session

def get_body(service: str, function: str):
    schema_top = '<soap-env:Envelope xmlns:soap-env="http://schemas.xmlsoap.org/soap/envelope/"><soap-env:Body>'
    if service == 'Policy2':
        schema_top += f'<ns0:{function} xmlns:ns0="http://policy.apiV2.server.backup.r1soft.com/">'
    else:
        schema_top += f'<ns0:{function} xmlns:ns0="http://{service.lower()}.api.server.backup.r1soft.com/">'
    schema_bot = f'</ns0:{function}></soap-env:Body></soap-env:Envelope>'
    return (schema_top, schema_bot)

def get_parameter(params: dict):
    parameters = ''
    for key, value in params.items():
        parameters += f'<{key}>{value}</{key}>'
    return parameters

def get_time(date_str: str):
    if date_str.strip() == '':
        return '1970-01-01 00:00:00'
    date_str = date_str.replace('Z', '-00:00')
    utc_time = datetime.datetime.fromisoformat(date_str).astimezone(datetime.timezone.utc)
    return utc_time.strftime("%Y-%m-%d %H:%M:%S")

def get_num(number: str):
    number = number.lower()
    return int(float(number))

def post(host, session, service: str, function: str, parameters: str = ''):
    if service == 'DiskSafe':
        timeout = 60
    else:
        timeout = 10
    body_tuple = get_body(service, function)
    post_body = body_tuple[0] + parameters + body_tuple[1]
    response = session.post(
        f'http://{host}:{PORT}/{service}?wsdl', data=post_body
    , timeout=timeout)
    if b'soap:Fault' in response.content:
        if b'Disk Safe is closed' in response.content:
            raise DiskSafeClosed
        else:
            raise Exception(xmltodict.parse(
                response.content)['soap:Envelope']['soap:Body']['soap:Fault']['faultstring']
            )
    elif b'<return>' not in response.content:
        return {}
    return xmltodict.parse(response.content)['soap:Envelope']['soap:Body'][
        f'ns2:{function}Response'
    ]['return']

def normalize(input: dict, schema: dict):
    for key in schema.keys():
        if key not in input.keys():
            input[key] = schema[key]
    return input

def map_out(input: dict):
    output = {}
    if input is None:
        return None
    for attribute in input['entry']:
        output[attribute['key']] = attribute['value']
    return output

def get_agents(host):
    change = False
    cursor = conn.cursor()
    sql = """
        INSERT INTO agents
        VALUES (UNHEX(%s), %s, %s,
                %s, %s, %s,
                %s, %s, %s,
                %s, %s);
    """
    cursor.execute(f"""
        SELECT
          HEX(id),
          server_id,
          type,
          description,
          hostname,
          agent_version,
          driver_version,
          os_version,
          os_type,
          port,
          enabled
        FROM
          agents
        WHERE server_id = '{host}';
    """)
    db_agents = cursor.fetchall()
    ids = [row[0] for row in db_agents]
    agents = post(host, session, 'Agent', 'getAgents')
    if len(agents) == 0:
        return
    new_ids = []
    for agent in agents:
        agent = normalize(
            agent,
            {
                'id': '00000000-0000-0000-0000-000000000000',
                'agentType': '',
                'description': '',
                'hostname': '',
                'lastKnownAgentVersion': '',
                'lastKnownDriverVersion': '',
                'lastKnownOSVersion': '',
                'osType': '',
                'portNumber': '',
            },
        )
        data = (
            agent['id'].replace('-', '').upper(),
            host,
            agent['agentType'],
            agent['description'],
            agent['hostname'],
            agent['lastKnownAgentVersion'],
            agent['lastKnownDriverVersion'],
            agent['lastKnownOSVersion'],
            agent['osType'],
            int(agent['portNumber']),
            1,
        )
        new_ids.append(data[0])
        if data not in db_agents:
            if data[0] in ids:
                cursor.execute('DELETE FROM agents WHERE id = UNHEX(%s);', [data[0]])
            cursor.execute(sql, data)
            change = True
    for id in ids:
        if id not in new_ids:
            cursor.execute('''
               UPDATE agents
               SET enabled = 0
               WHERE id = UNHEX(%s) ;''', [id])
            change = True
    conn.commit()
    cursor.close()
    if change:
        compile_data()

def get_volumes(host):
    change = False
    cursor = conn.cursor()
    sql = """
        INSERT INTO volumes
        VALUES (UNHEX(%s), %s, %s,
                %s, %s, %s,
                %s, %s);
    """
    cursor.execute(f"""
        SELECT
          HEX(id),
          server_id,
          name,
          description,
          path,
          file_exclude ,
          database_enabled,
          control_enabled
        FROM
          volumes
        WHERE server_id = '{host}';
    """)
    db_volumes = cursor.fetchall()
    ids = [row[0] for row in db_volumes]
    volumes = post(host, session, 'Volume', 'getVolumes')
    if len(volumes) == 0:
        return
    for volume in volumes:
        volume = normalize(
            volume,
            {
                'id': '00000000-0000-0000-0000-000000000000',
                'name': '',
                'description': '',
                'path': '',
            },
        )
        map = map_out(volume['volumeAttributeMap'])
        if map is not None and map['FILE_EXCLUDES_ENABLED'] == 'true':
            file_exclude = 1
        else:
            file_exclude = 0
        if map is not None and map['DATABASE_BACKUPS_ENABLED'] == 'true':
            data_exclude = 1
        else:
            data_exclude = 0
        if map is not None and map['CONTROLPANELS_ENABLED'] == 'true':
            control_exclude = 1
        else:
            control_exclude = 0
        data = (
            volume['id'].replace('-', '').upper(),
            host,
            volume['name'],
            volume['description'],
            volume['path'],
            file_exclude,
            data_exclude,
            control_exclude,
        )
        if data not in db_volumes:
            if data[0] in ids:
                cursor.execute('DELETE FROM volumes WHERE id = UNHEX(%s);', [data[0]])
                change = True
            cursor.execute(sql, data)
            change = True
    conn.commit()
    cursor.close()
    if change:
        compile_data()

def get_reports(host):
    change = False
    cursor = conn.cursor()
    sql = """
        INSERT INTO reports
        VALUES (UNHEX(%s), %s, %s,
                %s, %s, %s,
                %s, %s);
    """
    sql2 = """
        INSERT INTO reports_agents
        VALUES (UNHEX(%s),
                UNHEX(%s));
    """
    sql3 = """
        INSERT INTO reports_emails
        VALUES (UNHEX(%s),
                %s);
    """
    cursor.execute(f"""
        SELECT
          HEX(id),
          server_id,
          name,
          subject,
          DATE_FORMAT(last, '%Y-%m-%d %H:%i:%S'),
          DATE_FORMAT(schedule, '%Y-%m-%d %H:%i:%S'),
          frequency
        FROM
          reports
        WHERE server_id = '{host}';
    """)
    db_reports = cursor.fetchall()
    ids = [row[0] for row in db_reports]
    cursor.execute('SELECT HEX(report_id), HEX(agent_id) FROM reports_agents;')
    db_re_ag = cursor.fetchall()
    cursor.execute('SELECT HEX(report_id), email FROM reports_emails;')
    db_re_em = cursor.fetchall()
    reports = post(host, session, 'Reporting', 'getReports')
    if len(reports) == 0:
        return
    new_ids = []
    for report in reports:
        if 'enabled' not in report or report['enabled'] != 'true':
            continue
        if 'includeFullAlertDetails' in report:
            info = 1
        else:
            info = 0
        report = normalize(
            report,
            {
                'id': '00000000-0000-0000-0000-000000000000',
                'name': '',
                'subject': '',
                'lastExecutionTime': '',
                'nextExecutionTime': '',
                'reportFrequencyType': '',
            },
        )
        data = (
            report['id'].replace('-', '').upper(),
            host,
            report['name'],
            report['subject'],
            get_time(report['lastExecutionTime']),
            get_time(report['nextExecutionTime']),
            report['reportFrequencyType'],
            info
        )
        report_changed = False
        new_ids.append(data[0])
        if data not in db_reports:
            report_changed = True
            if data[0] in ids:
                cursor.execute('DELETE FROM reports WHERE id = UNHEX(%s);', [data[0]])
            cursor.execute(sql, data)
            change = True
        if 'agentIDsFilterList' in report.keys():
            if not isinstance(report['agentIDsFilterList'], list):
                report['agentIDsFilterList'] = [report['agentIDsFilterList']]
            for agent in report['agentIDsFilterList']:
                if agent == '':
                    continue
                data2 = (report['id'].replace('-', '').upper(), agent.replace('-', '').upper())
                if data2 not in db_re_ag or report_changed:
                    cursor.execute(sql2, data2)
                    change = True
        if 'emailAddresses' in report.keys():
            if not isinstance(report['emailAddresses'], list):
                report['emailAddresses'] = [report['emailAddresses']]
            for email in report['emailAddresses']:
                if email == '':
                    continue
                data3 = (report['id'].replace('-', '').upper(), email)
                if data3 not in db_re_em or report_changed:
                    cursor.execute(sql3, data3)
                    change = True
    for id in ids:
        if id not in new_ids:
            cursor.execute('DELETE FROM reports WHERE id = UNHEX(%s) ;', [id])
            change = True
    conn.commit()
    cursor.close()
    if change:
        compile_data()

def get_disk_safes(host):
    change = False
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT
          HEX(id),
          server_id,
          HEX(agent_id),
          HEX(volume_id),
          description,
          path,
          re_points_limit,
          re_points,
          latest_rp,
          size,
          deltas,
          soft_quota,
          hard_quota
        FROM
          disk_safes
        WHERE server_id = '{host}';
    """)
    db_safes = cursor.fetchall()
    ids = [row[0] for row in db_safes]
    cursor.execute(f"""
        SELECT
          HEX(disk_safe_id),
          safes_devices.id,
          alloc_blocks,
          block_size,
          total_blocks,
          capacity,
          type,
          safes_devices.path,
          mount,
          enabled
        FROM
          safes_devices
        JOIN disk_safes
        ON safes_devices.disk_safe_id = disk_safes.id
        WHERE disk_safes.server_id = '{host}';
    """)
    db_devices = cursor.fetchall()
    device_ids = [(row[0], row[1]) for row in db_devices]
    sql = """
        INSERT INTO disk_safes
        VALUES (UNHEX(%s), %s, UNHEX(%s),
                UNHEX(%s), %s, %s,
                %s, %s, %s,
                %s, %s, %s,
                %s);
    """
    sql2 = """
        INSERT INTO safes_devices
        VALUES (UNHEX(%s), %s, %s,
                %s, %s, %s,
                %s, %s, %s,
                %s);
    """
    disk_safes = post(host, session, 'DiskSafe', 'getDiskSafes')
    if len(disk_safes) == 0:
        return
    for disk_safe in disk_safes:
        disk_safe = normalize(
            disk_safe,
            {
                'id': '00000000-0000-0000-0000-000000000000',
                'agentID': '00000000-0000-0000-0000-000000000000',
                'volumeID': '00000000-0000-0000-0000-000000000000',
                'description': '',
                'path': '',
                'recoveryPointCount': '0',
                'latestRecoveryPointId': '0',
                'size': '0',
                'sizeOfDeltasInDiskSafe': '0',
            },
        )
        map = map_out(disk_safe['diskSafeAttributeMap'])
        if map == None:
            re_point_limit = '0'
            soft_quota = '0'
            hard_quota = '0'
        else:
            if map['RECOVERY_POINT_LIMIT'] == '-1':
                re_point_limit = '0'
            else:
                re_point_limit = map['RECOVERY_POINT_LIMIT']
            soft_quota = map['SOFT_QUOTA_VALUE']
            hard_quota = map['HARD_QUOTA_VALUE']

        data = (
            disk_safe['id'].replace('-', '').upper(),
            host,
            disk_safe['agentID'].replace('-', '').upper(),
            disk_safe['volumeID'].replace('-', '').upper(),
            disk_safe['description'],
            disk_safe['path'],
            get_num(re_point_limit),
            get_num(disk_safe['recoveryPointCount']),
            get_num(disk_safe['latestRecoveryPointId']),
            get_num(disk_safe['size']),
            get_num(disk_safe['sizeOfDeltasInDiskSafe']),
            get_num(soft_quota),
            get_num(hard_quota),
        )
        ds_changed = False
        if data not in db_safes:
            ds_changed = True
            if data[0] in ids:
                cursor.execute('DELETE FROM disk_safes WHERE id = UNHEX(%s);', [data[0]])
            cursor.execute(sql, data)
            change = True
        if 'deviceList' not in disk_safe.keys():
            continue
        if not isinstance(disk_safe['deviceList'], list):
            disk_safe['deviceList'] = [disk_safe['deviceList']]
        for drive in disk_safe['deviceList']:
            drive = normalize(
                drive,
                {
                    'contentID': '',
                    'allocatedBlocks': '0',
                    'blockSize': '0',
                    'totalBlocks': '0',
                    'capacity': '0',
                    'deviceContentType': '',
                    'devicePath': '',
                    'mountPoint': '',
                    'enabled': '0',
                },
            )
            if drive['enabled'] == 'true':
                enabled = 1
            else:
                enabled = 0
            data2 = (
                disk_safe['id'].replace('-', '').upper(),
                drive['contentID'],
                get_num(drive['allocatedBlocks']),
                get_num(drive['blockSize']),
                get_num(drive['totalBlocks']),
                get_num(drive['capacity']),
                drive['deviceContentType'],
                drive['devicePath'],
                drive['mountPoint'],
                enabled,
            )
            if data2 not in db_devices or ds_changed:
                if (data2[0], data2[1]) in device_ids:
                    cursor.execute('DELETE FROM safes_devices WHERE disk_safe_id = UNHEX(%s) AND id = %s;',
                           (data2[0], data2[1]))
                cursor.execute(sql2, data2)
                change = True
    conn.commit()
    cursor.close()
    if change:
        compile_data()

def get_policies_by_id(host):
    policy_ids = post(host, session, 'Policy2', 'getPolicyIDs')
    policies = []
    for id in policy_ids:
        params = get_parameter({'id': id})
        try:
            policy = post(host, session, 'Policy2', 'getPolicyById', params)
        except DiskSafeClosed:
            continue
        if 'name' in policy:
            policies.append(policy)
    return policies

def get_policies(host):
    change = False
    whole = True
    try:
        policies = post(host, session, 'Policy2', 'getPolicies')
    except DiskSafeClosed:
        policies = get_policies_by_id(host)
        whole = False
    if len(policies) == 0:
        return False
    cursor = conn.cursor()
    sql = """
        INSERT INTO policies
        VALUES (UNHEX(%s), %s, UNHEX(%s),
                %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s,
                %s, %s);
    """
    cursor.execute(f"""
        SELECT
          HEX(id),
          server_id,
          HEX(disk_safe_id),
          name,
          DATE_FORMAT(last, '%Y-%m-%d %H:%i:%S'),
          schedule,
          frequency,
          daily,
          hourly,
          minutely,
          monthly,
          weekly,
          yearly,
          state
        FROM
          policies
        WHERE server_id = '{host}';
    """)
    db_policies = cursor.fetchall()
    ids = [row[0] for row in db_policies]
    new_ids = []
    for policy in policies:
        if policy['localRetentionSettings'] == None:
            policy['localRetentionSettings'] = {}
            policy['localRetentionSettings']['dailyLimit'] = ''
            policy['localRetentionSettings']['hourlyLimit'] = ''
            policy['localRetentionSettings']['minutelyLimit'] = ''
            policy['localRetentionSettings']['monthlyLimit'] = ''
            policy['localRetentionSettings']['weeklyLimit'] = ''
            policy['localRetentionSettings']['yearlyLimit'] = ''
        if (
            policy['replicationScheduleFrequencyValues'] == None
            or policy['replicationScheduleFrequencyType'] == 'HOURLY'
        ):
            schedule = ''
        else:
            schedule = (
                policy['replicationScheduleFrequencyValues']['startingHour']
                + ':'
                + policy['replicationScheduleFrequencyValues']['startingMinute']
            )
        policy = normalize(
            policy,
            {
                'id': '00000000-0000-0000-0000-000000000000',
                'diskSafeID': '00000000-0000-0000-0000-000000000000',
                'lastReplicationRunTime': '',
                'lastReplicationRunTime': '',
                'state': '',
            },
        )
        data = (
            policy['id'].replace('-', '').upper(),
            host,
            policy['diskSafeID'].replace('-', '').upper(),
            policy['name'],
            get_time(policy['lastReplicationRunTime']),
            schedule,
            policy['replicationScheduleFrequencyType'],
            get_num(policy['localRetentionSettings']['dailyLimit']),
            get_num(policy['localRetentionSettings']['hourlyLimit']),
            get_num(policy['localRetentionSettings']['minutelyLimit']),
            get_num(policy['localRetentionSettings']['monthlyLimit']),
            get_num(policy['localRetentionSettings']['weeklyLimit']),
            get_num(policy['localRetentionSettings']['yearlyLimit']),
            policy['state'],
        )
        new_ids.append(data[0])
        if data not in db_policies:
            if data[0] in ids:
                cursor.execute('DELETE FROM policies WHERE id = UNHEX(%s);', [data[0]])
            cursor.execute(sql, data)
            change = True
    for id in ids:
        if id not in new_ids:
            cursor.execute('DELETE FROM policies WHERE id = UNHEX(%s);', [id])
            change = True
    conn.commit()
    cursor.close()
    if change:
        compile_data()
    return whole

def get_servers(ip, host):
    change = False
    server = post(host, session, 'Configuration', 'getServerInformation')
    params = get_parameter({'storageDiskPath': '/volumes'})
    volume = post(host, session, 'StorageDisk', 'getStorageDiskByPath', params)
    params = get_parameter({'storageDiskPath': '/'})
    root = post(host, session, 'StorageDisk', 'getStorageDiskByPath', params)
    cursor = conn.cursor()
    sql = """
        INSERT INTO servers
        VALUES (%s, %s, %s,
                %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s,
                %s, %s);
    """
    cursor.execute('SELECT * FROM servers;')
    db_servers = cursor.fetchall()
    ids = [row[0] for row in db_servers]
    server = normalize(
        server,
        {
            'freePhysicalMemory': '0',
            'numberOfProcessors': '',
            'osArchitecture': '',
            'osName': '',
            'osVersion': '',
            'totalPhysicalMemory': '0',
        },
    )
    volume = normalize(
        volume,
        {
            'device': '',
            'capacityBytes': '0',
            'usageBytes': '0',
        },
    )
    root = normalize(
        root,
        {
            'device': '',
            'capacityBytes': '0',
            'usageBytes': '0',
        },
    )
    data = (
        ip,
        host,
        server['osName'],
        server['osVersion'],
        server['osArchitecture'],
        get_num(server['numberOfProcessors']),
        get_num(server['totalPhysicalMemory']),
        get_num(server['freePhysicalMemory']),
        volume['device'],
        get_num(volume['capacityBytes']),
        get_num(volume['usageBytes']),
        root['device'],
        get_num(root['capacityBytes']),
        get_num(root['usageBytes']),
    )
    if data not in db_servers:
        if data[0] in ids:
            cursor.execute('DELETE FROM servers WHERE id = %s;', [data[0]])
        cursor.execute(sql, data)
        change = True
    conn.commit()
    cursor.close()
    if change:
        compile_data()

def get_task(host):
    change = False
    cursor = conn.cursor()
    cursor.execute(f'SELECT HEX(id) FROM tasks WHERE server_id = "{host}";')
    ids = cursor.fetchall()
    ids = [row[0] for row in ids]
    params = get_parameter({
        'executionStart': date.today() - timedelta(days=1),
        'executionEnd': date.today() + timedelta(days=1),
        })
    results = post(host, session, 'TaskHistory', 'getTaskExecutionContextIDsByDate', params)
    if len(results) == 0:
        return
    for result in results:
        if result.replace('-', '').upper() in ids:
            continue
        param = get_parameter({'taskExecutionContextID': result})
        task = post(host, session, 'TaskHistory', 'getTaskExecutionContextByID', param)
        if 'emailAddresses' in task.keys():
            log_error(host, 'email task', 'skipped')
            continue
        task = normalize(
            task,
            {
                'id': '00000000-0000-0000-0000-000000000000',
                'agentId': '00000000-0000-0000-0000-000000000000',
                'taskState': '',
                'taskType': '',
                'completionTime': '',
                'executionTime': '',
                'scheduledTime': '',
            }
        )
        sql = """
            INSERT INTO tasks
            VALUES (UNHEX(%s), %s, UNHEX(%s),
                    %s, %s, %s,
                    %s, %s);
        """
        data = (
            task['id'].replace('-', ''),
            host,
            task['agentId'].replace('-', ''),
            task['taskState'],
            task['taskType'],
            get_time(task['completionTime']),
            get_time(task['executionTime']),
            get_time(task['scheduledTime']),
        )
        cursor.execute(sql, data)
        change = True
    conn.commit()
    cursor.close()
    if change:
        compile_data()

def get_alerts(host):
    change = False
    cursor = conn.cursor()
    cursor.execute(f'SELECT HEX(task_id), alerts.id FROM alerts JOIN tasks on alerts.task_id = tasks.id WHERE server_id like "{host}";')
    alert_ids = cursor.fetchall()
    cursor.execute(f'''SELECT HEX(id) FROM tasks WHERE (state LIKE "RUNNING" OR completion > (UTC_TIMESTAMP() - INTERVAL 30 MINUTE))
        AND HEX(agent_id) NOT LIKE '00000000000000000000000000000000'
        AND server_id = "{host}";''')
    task_ids = cursor.fetchall()
    task_ids = [row[0] for row in task_ids]
    params = get_parameter({
        'executionStart': date.today() - timedelta(days=1),
        'executionEnd': date.today() + timedelta(days=1),
        'hasAlerts': 'true',
        })
    results = post(host, session, 'TaskHistory', 'getTaskExecutionContextIDs', params)
    if results == {}:
        return
    elif not isinstance(results, list):
        results = [results]
    for result in results:
        if result.replace('-', '').upper() not in task_ids:
            continue
        param = get_parameter({'taskExecutionContextID': result})
        alerts = post(host, session, 'TaskHistory', 'getAlertIDsByTaskExecutionContextID', param)
        for alert_id in alerts:
            if (result.replace('-', '').upper(), int(alert_id)) in alert_ids:
                continue
            param = get_parameter({
                'taskExecutionContextID': result,
                'alertID': alert_id,
                })
            alert = post(host, session, 'TaskHistory', 'getAlertByID', param)
            alert = normalize(
                alert,
                {
                    'alertID': '0',
                    'taskExecutionContextID': '00000000-0000-0000-0000-000000000000',
                    'alertKey': '',
                    'alertString': '',
                    'alertTime': '',
                }
            )
            sql = """
                INSERT INTO alerts
                VALUES (UNHEX(%s), %s, %s,
                        %s, %s);
            """
            data = (
                alert['taskExecutionContextID'].replace('-', ''),
                alert['alertID'],
                alert['alertKey'],
                alert['alertString'],
                get_time(alert['alertTime']),
            )
            cursor.execute(sql, data)
            change = True
    conn.commit()
    cursor.close()
    if change:
        compile_data()

def update_running(host):
    change = False
    cursor = conn.cursor()
    cursor.execute(f'SELECT HEX(id) FROM tasks WHERE state LIKE "RUNNING" AND server_id LIKE "{host}";')
    ids = cursor.fetchall()
    cursor.execute(f'DELETE FROM tasks WHERE state LIKE "RUNNING" AND server_id LIKE "{host}";')
    ids = [row[0] for row in ids]
    for id in ids:
        id = id.lower()
        uuid = id[0:8] + '-' + id[8:12] + '-' + id[12:16] + '-' + id[16:20] + '-' + id[20:]
        param = get_parameter({'taskExecutionContextID': uuid})
        task = post(host, session, 'TaskHistory', 'getTaskExecutionContextByID', param)
        task = normalize(
            task,
            {
                'id': '00000000-0000-0000-0000-000000000000',
                'agentId': '00000000-0000-0000-0000-000000000000',
                'taskState': '',
                'taskType': '',
                'completionTime': '',
                'executionTime': '',
                'scheduledTime': '',
            }
        )
        sql = """
            INSERT INTO tasks
            VALUES (UNHEX(%s), %s, UNHEX(%s),
                    %s, %s, %s,
                    %s, %s);
        """
        data = (
            task['id'].replace('-', ''),
            host,
            task['agentId'].replace('-', ''),
            task['taskState'],
            task['taskType'],
            get_time(task['completionTime']),
            get_time(task['executionTime']),
            get_time(task['scheduledTime']),
        )
        cursor.execute(sql, data)
        change = True
    conn.commit()
    cursor.close()
    if change:
        compile_data()

if __name__ == '__main__':
    session = get_session()
    count = 0
    start = time.time()
    log_error('start', 'start', 'start')
    for host, ip in hosts.items():
        if not check(ip):
            log_error(host, 'skipped_ds', 'skipped')
            continue
        try:
            get_disk_safes(ip)
        except Exception as error:
            log_error(host, 'disk_safe', error)
    bad_policy_servers = []
    for i in range(29):
        while (time.time() - start) < 60*i:
            time.sleep(1)
        run_start = time.time()
        act = 'agents'
        for host, ip in hosts.items():
            if not check(ip):
                log_error(host, 'skipped', 'skipped')
                continue
            if i % 2 != 0:
                try:
                    get_agents(ip)
                    act = 'volumes'
                    get_volumes(ip)
                    act = 'reports'
                    get_reports(ip)
                    act = 'servers'
                    get_servers(ip, host)
                    act = 'policies'
                    if ip not in bad_policy_servers:
                        if not get_policies(ip):
                            bad_policy_servers.append(ip)
                except Exception as error:
                    log_error(host, act, error)
                    continue
            try:
                act = 'running'
                update_running(ip)
                act = 'tasks'
                get_task(ip)
                act = 'alerts'
                get_alerts(ip)
            except Exception as error:
                log_error(host, act, error)
    log_error('end', 'end', 'end')
