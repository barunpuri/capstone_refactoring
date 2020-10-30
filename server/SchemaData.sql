-- Capstone Database
-- Version 1.0

-- SHOW VARIABLES;
-- SELECT @@GLOBAL.sql_mode;
-- SELECT @@SESSION.sql_mode;

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;					/* Default : 1 (ON) */
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;		/* Default : 1 (ON) */


DROP SCHEMA IF EXISTS capstone;

CREATE SCHEMA capstone DEFAULT CHARACTER SET utf8;
USE capstone;

DROP TABLE IF EXISTS user_info;
DROP TABLE IF EXISTS conn_info;

-------------------------------------------
-- Schema
-------------------------------------------
CREATE TABLE USER_INFO (
    USER_ID     CHAR(15)    NOT NULL,
    PASSWORD    CHAR(15)    NOT NULL,
    NAME        CHAR(10)    NOT NULL,
    EMAIL       CHAR(30)    NOT NULL,

    PRIMARY KEY (USER_ID),
    INDEX   IDX_USER_ID      (USER_ID ASC)
);

CREATE TABLE CONN_INFO (
    ID   CHAR(15)    NOT NULL,
    MAC_ADDR    CHAR(17)    NOT NULL,
    DEVICE_NAME CHAR(100)   NOT NULL,

    PRIMARY KEY (ID, MAC_ADDR),
    INDEX   IDX_ID   (ID ASC),
    INDEX   IDX_MAC_ADDR    (MAC_ADDR ASC),

    CONSTRAINT  FK_USER_CONN    FOREIGN KEY (ID)    REFERENCES USER_INFO(USER_ID)
                                        ON DELETE CASCADE
                                        ON UPDATE CASCADE
);

-------------------------------------------
-- Data
-------------------------------------------

INSERT INTO USER_INFO VALUES
('test', 'test', 'test', 'test@mail.com'),
('test2', 'test', 'test', 'test@mail.com'),
('test3', 'test', 'test', 'test@mail.com');

INSERT INTO CONN_INFO VALUES
('test', 'ff:ff:ff:ff:ff:ff', 'test'),
('test', 'ff:ff:ff:ff:ff:ee', 'test_pc'),
('test2', 'ff:ff:ff:ff:ff:ff', 'test'),
('test3', 'ff:ff:ff:ff:ff:ff', 'test');



-- SET SQL_MODE=@OLD_SQL_MODE;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;