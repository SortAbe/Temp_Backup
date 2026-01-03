SELECT
  HEX(id),
  server_id,
  type,
  description,
  hostname,
  agent_version
  driver_version,
  os_version,
  os_type,
  port
FROM
  agents;

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
  volumes;

SELECT
  HEX(id),
  server_id,
  HEX(agent_id),
  HEX(volume_id),
  description,
  path,
  re_points_limit,
  re_points,
  size,
  deltas,
  soft_quota,
  hard_quota
FROM
  disk_safes;

SELECT
  HEX(disk_safe_id),
  id,
  alloc_blocks,
  block_size,
  total_blocks,
  capacity,
  type,
  path,
  mount,
  enabled
FROM
  safes_devices;

SELECT
  *
FROM
  servers;

SELECT
  HEX(id),
  server_id,
  name,
  subject,
  DATE_FORMAT(last, '%Y-%m-%d %H:%i:%S'),
  DATE_FORMAT(schedule, '%Y-%m-%d %H:%i:%S'),
  frequency
FROM
  reports;

SELECT
  HEX(report_id),
  HEX(agent_id)
FROM
  reports_agents;

SELECT
  HEX(report_id),
  email
FROM
  reports_agents;

DELETE
FROM agents
WHERE id = UNHEX();

select
  dense_rank() over(order by agents.id) as 'aid',
  agents.id,
  case when disk_safes.id is null
    then null
    else dense_rank() over(order by disk_safes.id)
  end as 'did',
  disk_safes.id,
  case when policies.id is null
    then null
    else dense_rank() over(order by policies.id)
  end as 'pid',
  policies.id
from agents
cross join disk_safes on disk_safes.agent_id = agents.id
cross join policies on policies.disk_safe_id = disk_safes.id
order by policies.id desc limit 10;

create view i_agents as (select id, RANK() over(order by id) - 1 as 'index' from agents);
create view i_disk_safes as (select id, RANK() over(order by id) - 1 as 'index' from disk_safes);
create view i_volumes as (select id, RANK() over(order by id) - 1 as 'index' from volumes);
create view i_tasks as (select id, RANK() over(order by id) - 1 as 'index' from tasks);
create view i_policies as (select id, RANK() over(order by id) - 1 as 'index' from policies);
create view i_reports as (select id, RANK() over(order by id) - 1 as 'index' from reports);

SELECT
  RANK() OVER(order by id) - 1,
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
FROM agents;

SELECT
  RANK() OVER(order by id),
  name,
  description,
  path,
  file_exclude,
  database_enabled,
  control_enabled
FROM volumes;

SELECT
  RANK() OVER(order by disk_safes.id),
  a_agents.alias as 'aid',
  a_volumes.alias as 'vid',
  description,
  path,
  re_points_limit,
  re_points,
  latest_rp,
  size,
  deltas,
  soft_quota,
  hard_quota
FROM disk_safes
LEFT JOIN a_agents on a_agents.id = disk_safes.agent_id
LEFT JOIN a_volumes on a_volumes.id = disk_safes.volume_id;

SELECT
  RANK() OVER(order by policies.id),
  a_disk_safes.alias as 'did',
  name,
  last,
  schedule,
  frequency,
  daily,
  hourly,
  minutely,
  monthly,
  weekly,
  yearly
FROM policies
LEFT JOIN a_disk_safes on a_disk_safes.id = policies.disk_safe_id;

SELECT
  RANK() OVER(order by tasks.id),
  server_id,
  i_agents.index,
  state,
  type,
  completion,
  execution,
  schedule
FROM tasks
LEFT JOIN i_agents on i_agents.id = tasks.agent_id
WHERE i_agents.index IS NOT NULL
AND type not like 'ARCHIVE';

SELECT
  a_reports.alias,
  a_agents.alias
FROM reports_agents
LEFT JOIN a_agents on a_agents.id = reports_agents.agent_id
LEFT JOIN a_reports on a_reports.id = reports_agents.report_id
WHERE a_agents.alias is not null;

SELECT
  a_reports.alias,
  reports_emails.email
FROM reports_emails
LEFT JOIN a_reports on a_reports.id =  reports_emails.report_id;

SELECT
  reports_emails.email,
  a_agents.alias
FROM reports_emails
LEFT JOIN reports_agents on reports_agents.report_id = reports_emails.report_id
LEFT JOIN a_agents on a_agents.id = reports_agents.agent_id
WHERE a_agents.id IS NOT NULL
ORDER BY reports_emails.email;

SELECT
  *
FROM servers;

SELECT
  RANK() OVER(order by alerts.task_id) as 'index',
  alerts.id,
  alert_key,
  alert_str,
  alert_time
FROM alerts
LEFT JOIN a_tasks on alerts.task_id = a_tasks.id;

SELECT
  a_reports.alias
FROM reports
LEFT JOIN a_reports on a_reports.id =  reports_emails.report_id;

SELECT
  name,
  i_agents.index
FROM reports
LEFT JOIN reports_agents ON reports_agents.report_id = reports.id
LEFT JOIN i_agents ON i_agents.id = reports_agents.agent_id
WHERE i_agents.id IS NOT NULL
AND name NOT LIKE '%quota%';


SELECT
  i_reports.index,
  reports_emails.email,
  reports.name,
  sendgrid.status,
  sendgrid.last_time,
  sendgrid.open_count,
  sendgrid.click_count,
  sendgrid.event,
  sendgrid.reason
FROM reports
LEFT JOIN i_reports ON i_reports.id = reports.id
LEFT JOIN reports_emails ON reports_emails.report_id = reports.id
LEFT JOIN sendgrid ON sendgrid.to_email = reports_emails.email
ORDER BY i_reports.index;

SELECT
  sendgrid.to_email,
  sendgrid.status,
  sendgrid.subject,
  sendgrid.open_count,
  sendgrid.click_count,
  sendgrid.last_time,
  sendgrid.event,
  sendgrid.reason
FROM sendgrid
INNER JOIN
  (SELECT
    to_email,
    MAX(last_time) AS 'lt'
    FROM sendgrid
    WHERE status NOT LIKE 'processing'
    GROUP BY to_email)
AS sub ON sub.to_email = sendgrid.to_email AND sub.lt = sendgrid.last_time;

SELECT
  i_reports.index,
  reports.server_id,
  reports.name,
  reports.last,
  reports_emails.email,
  agents.description,
  reports.info
FROM reports
JOIN i_reports ON i_reports.id = reports.id
LEFT JOIN reports_emails ON reports_emails.report_id = reports.id
LEFT JOIN reports_agents ON reports_agents.report_id = reports.id
LEFT JOIN agents ON reports_agents.agent_id = agents.id;

DELETE FROM tasks
WHERE HEX(agent_id) LIKE '00000000000000000000000000000000'
OR type like 'ARCHIVE';

SELECT HEX(id), HEX(agent_id), execution
FROM tasks
WHERE type like "DATA_PROTECTION_POLICY"
ORDER BY agent_id, execution DESC;

DELETE FROM tasks
WHERE id = UNHEX('');

SELECT tasks.id, agent_id, description, tasks.server_id, DATE(execution) FROM tasks
JOIN alerts ON tasks.id = alerts.task_id
JOIN agents ON tasks.agent_id = agents.id
WHERE alert_key IN ('Alerts.Main.dpp-disabled', 'Messages.UI.invalid-policy', 'Alerts.Main.disk-safe-closed-alert')
ORDER BY description;

SELECT description, MAX(DATE(execution)) FROM tasks
JOIN alerts ON tasks.id = alerts.task_id
JOIN agents ON tasks.agent_id = agents.id
WHERE alert_key IN ('Alerts.Main.dpp-disabled', 'Messages.UI.invalid-policy', 'Alerts.Main.disk-safe-closed-alert')
GROUP BY description;

SELECT agent_id FROM tasks
JOIN alerts ON tasks.id = alerts.task_id
WHERE alert_key IN ('Alerts.Main.dpp-disabled', 'Messages.UI.invalid-policy', 'Alerts.Main.disk-safe-closed-alert')
GROUP BY agent_id;

SELECT *
FROM tasks
WHERE agent_id = UNHEX('1F7994745B2447A6B08393C64435B353')
AND type = 'DATA_PROTECTION_POLICY';

SELECT
 HEX(tasks.id),
 HEX(tasks.agent_id),
 SUBSTRING(alerts.alert_key, 1, 68),
 DATE(tasks.execution) as 'date'
FROM tasks
LEFT JOIN alerts ON tasks.id = alerts.task_id
WHERE agent_id IN (
  SELECT agent_id
  FROM tasks
  JOIN alerts ON tasks.id = alerts.task_id
  WHERE alert_key IN ('Alerts.Main.dpp-disabled', 'Messages.UI.invalid-policy', 'Alerts.Main.disk-safe-closed-alert')
  GROUP BY agent_id
)
AND type = 'DATA_PROTECTION_POLICY'
ORDER BY agent_id, execution DESC;
