CREATE OR REPLACE PROCEDURE create_user()
LANGUAGE plpgsql
AS
$$
BEGIN
	IF NOT EXISTS (SELECT 1 FROM pg_catalog.pg_roles WHERE rolname ='repl_user') THEN
		CREATE USER repl_user WITH REPLICATION ENCRYPTED PASSWORD 'eve@123';
	END IF;
END;
$$;

CALL create_user();

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
