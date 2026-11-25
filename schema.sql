-- =====================================================================
-- Astro Pitch Database - schema.sql
-- INFO8021 Submission 3 - Andrew White (R00253860)
--
-- Creates the four tables from the Milestone 2 ERD:
--   facility 1 ---< pitch 1 ---< review >--- 1 users
-- "users" is used instead of "user" because USER is a reserved word
-- in PostgreSQL.
-- Run by initialise_db.py, or by hand:  psql -d astropitch -f schema.sql
-- =====================================================================

-- Drop in reverse dependency order so the script can be re-run safely
DROP TABLE IF EXISTS review   CASCADE;
DROP TABLE IF EXISTS users    CASCADE;
DROP TABLE IF EXISTS pitch    CASCADE;
DROP TABLE IF EXISTS facility CASCADE;

-- ---------------------------------------------------------------------
-- facility: a sports centre / venue that owns one or more pitches
-- ---------------------------------------------------------------------
CREATE TABLE facility (
    facility_id    VARCHAR(10)  PRIMARY KEY,
    facility_name  VARCHAR(50)  NOT NULL,
    address        VARCHAR(100) NOT NULL
);

-- ---------------------------------------------------------------------
-- pitch: an individual astro pitch at a facility (main table)
-- ---------------------------------------------------------------------
CREATE TABLE pitch (
    pitch_id      VARCHAR(10) PRIMARY KEY,
    pitch_name    VARCHAR(30) NOT NULL,
    pitch_size    VARCHAR(10) NOT NULL
                  CHECK (pitch_size IN ('5-a-side', '7-a-side', '9-a-side', '11-a-side')),
    max_players   INT         NOT NULL CHECK (max_players > 0),
    opening_time  TIME        NOT NULL,
    closing_time  TIME        NOT NULL,
    facility_id   VARCHAR(10) NOT NULL
                  REFERENCES facility (facility_id)
                  ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT pitch_hours_valid CHECK (closing_time > opening_time)
);

-- ---------------------------------------------------------------------
-- users: registered users (passwords are stored as hashes, never plain)
-- ---------------------------------------------------------------------
CREATE TABLE users (
    user_id   VARCHAR(15)  PRIMARY KEY,
    username  VARCHAR(30)  NOT NULL UNIQUE,
    email     VARCHAR(50)  NOT NULL UNIQUE,
    password  VARCHAR(255) NOT NULL
);

-- ---------------------------------------------------------------------
-- review: a user's rating and comment for a pitch
-- ---------------------------------------------------------------------
CREATE TABLE review (
    review_id    VARCHAR(10)  PRIMARY KEY,
    rating       INT          NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment      VARCHAR(255),
    review_date  DATE         NOT NULL DEFAULT CURRENT_DATE,
    user_id      VARCHAR(15)  NOT NULL
                 REFERENCES users (user_id)
                 ON UPDATE CASCADE ON DELETE CASCADE,
    pitch_id     VARCHAR(10)  NOT NULL
                 REFERENCES pitch (pitch_id)
                 ON UPDATE CASCADE ON DELETE CASCADE
);

-- Indexes on foreign keys and on the columns the two search features use
CREATE INDEX idx_pitch_facility   ON pitch (facility_id);
CREATE INDEX idx_pitch_hours      ON pitch (opening_time, closing_time);
CREATE INDEX idx_pitch_players    ON pitch (max_players);
CREATE INDEX idx_review_pitch     ON review (pitch_id);
CREATE INDEX idx_review_user      ON review (user_id);
