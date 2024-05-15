
CREATE USER repl_user WITH REPLICATION ENCRYPTED PASSWORD 'eve@123';
ALTER SYSTEM SET archive_mode TO 'on';
ALTER SYSTEM SET archive_command TO 'cp %p /oracle/pg_data/archive/%f';
ALTER SYSTEM SET max_wal_senders TO 10;
ALTER SYSTEM SET log_replication_commands TO 'on';
ALTER SYSTEM SET wal_level TO 'replica';
ALTER SYSTEM SET wal_log_hints TO 'on';
ALTER SYSTEM SET logging_collector TO 'on';
ALTER SYSTEM SET log_directory TO '/var/log/postgresql';
ALTER SYSTEM SET log_filename TO 'postgresql-15-main.log';

CREATE TABLE IF NOT EXISTS email_info (
	id SERIAL PRIMARY KEY,
	username VARCHAR(256) NOT NULL,
	add_date DATE DEFAULT CURRENT_DATE,
	email VARCHAR(256) NOT NULL
);

CREATE TABLE IF NOT EXISTS phone_info (
	id SERIAL PRIMARY KEY,
	username VARCHAR(256) NOT NULL,
	add_date DATE DEFAULT CURRENT_DATE,
	phone VARCHAR(32) NOT NULL
);

INSERT INTO email_info(username, email)
VALUES('Flandre Scarlet', 'angela@naver.com'),
('Cirno', 'ihatemath@gmail.com');

INSERT INTO phone_info(username, phone)
VALUES('Remiliya Scarlet', '+79174141521'),
('Yukari Yakumo', '8 (800) 555-35-35');
