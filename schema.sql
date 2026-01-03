CREATE DATABASE IF NOT EXISTS BackupManager;

USE BackupManager;

CREATE TABLE agents (
  id BINARY(16) NOT NULL,
  server_id VARCHAR(37),
  type VARCHAR(12),
  description VARCHAR(50),
  hostname VARCHAR(50),
  agent_version VARCHAR(50),
  driver_version VARCHAR(50),
  os_version VARCHAR(120),
  os_type VARCHAR(50),
  port INT,
  enabled BOOLEAN,
  PRIMARY KEY (id)
);

CREATE TABLE volumes (
  id BINARY(16) NOT NULL,
  server_id VARCHAR(37),
  name VARCHAR(50),
  description VARCHAR(50),
  path VARCHAR(50),
  file_exclude BOOLEAN NOT NULL,
  database_enabled BOOLEAN NOT NULL,
  control_enabled BOOLEAN NOT NULL,
  PRIMARY KEY (id)
);

CREATE TABLE disk_safes (
  id BINARY(16) NOT NULL,
  server_id VARCHAR(37),
  agent_id BINARY(16) NOT NULL,
  volume_id BINARY(16) NOT NULL,
  description VARCHAR(100),
  path VARCHAR(75),
  re_points_limit INT,
  re_points INT,
  latest_rp INT,
  size BIGINT,
  deltas BIGINT,
  soft_quota BIGINT,
  hard_quota BIGINT,
  PRIMARY KEY (id)
);

CREATE TABLE safes_devices (
  disk_safe_id BINARY(16) NOT NULL,
  id VARCHAR(40) NOT NULL,
  alloc_blocks BIGINT,
  block_size INT,
  total_blocks BIGINT,
  capacity BIGINT,
  type VARCHAR(10),
  path VARCHAR(100),
  mount VARCHAR(100),
  enabled BOOLEAN NOT NULL,
  PRIMARY KEY (disk_safe_id, id),
  FOREIGN KEY (disk_safe_id) REFERENCES disk_safes (id)
  ON DELETE CASCADE
);

CREATE TABLE policies (
  id BINARY(16) NOT NULL,
  server_id VARCHAR(37),
  disk_safe_id BINARY(16) NOT NULL,
  name VARCHAR(100),
  last DATETIME,
  schedule VARCHAR(50),
  frequency VARCHAR(50),
  daily INT,
  hourly INT,
  minutely INT,
  monthly INT,
  weekly INT,
  yearly INT,
  state VARCHAR(10),
  PRIMARY KEY (id)
);

CREATE TABLE reports (
  id BINARY(16) NOT NULL,
  server_id VARCHAR(37),
  name VARCHAR(100),
  subject VARCHAR(100),
  last DATETIME,
  schedule DATETIME,
  frequency VARCHAR(50),
  info BOOLEAN,
  PRIMARY KEY (id)
);

CREATE TABLE reports_agents (
  report_id BINARY(16) NOT NULL,
  agent_id BINARY(16) NOT NULL,
  PRIMARY KEY (report_id, agent_id),
  FOREIGN KEY (report_id) REFERENCES reports (id)
  ON DELETE CASCADE
);

CREATE TABLE reports_emails (
  report_id BINARY(16) NOT NULL,
  email VARCHAR(100) NOT NULL,
  PRIMARY KEY (report_id, email),
  FOREIGN KEY (report_id) REFERENCES reports (id)
  ON DELETE CASCADE
);

CREATE TABLE tasks (
  id BINARY(16) NOT NULL,
  server_id VARCHAR(37),
  agent_id BINARY(16),
  state VARCHAR(20),
  type VARCHAR(150),
  completion DATETIME,
  execution DATETIME,
  schedule DATETIME,
  PRIMARY KEY (id)
);

CREATE TABLE alerts (
  task_id BINARY(16) NOT NULL,
  id INT NOT NULL,
  alert_key VARCHAR(150),
  alert_str VARCHAR(300),
  alert_time DATETIME,
  PRIMARY KEY (task_id, id),
  FOREIGN KEY (task_id) REFERENCES tasks (id)
  ON DELETE CASCADE
);

CREATE TABLE servers (
  id VARCHAR(20) NOT NULL,
  hostname VARCHAR(50),
  os_name VARCHAR(50),
  os_version VARCHAR(50),
  arch VARCHAR(50),
  cpu INT,
  memory BIGINT,
  free_mem BIGINT,
  volume_path VARCHAR(50),
  volume_cap BIGINT,
  volume_used BIGINT,
  root_path VARCHAR(50),
  root_cap BIGINT,
  root_used BIGINT,
  PRIMARY KEY (id)
);

CREATE TABLE sendgrid (
  id BINARY(16) NOT NULL,
  to_email VARCHAR(100),
  status VARCHAR(20),
  open_count INT,
  click_count INT,
  last_time DATETIME,
  event VARCHAR(20),
  reason VARCHAR(500),
  subject VARCHAR(255),
  PRIMARY KEY (id)
);

CREATE TABLE sessions (
  id VARCHAR(65) NOT NULL,
  user_agent VARCHAR(130),
  user_ip VARCHAR(40),
  expire DATETIME,
  PRIMARY KEY (id)
);
