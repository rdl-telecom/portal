CREATE TABLE IF NOT EXISTS device_code (
	mac CHAR(12),
	code CHAR(7),
	PRIMARY KEY (mac),
	INDEX (code)
) ENGINE INNODB;
