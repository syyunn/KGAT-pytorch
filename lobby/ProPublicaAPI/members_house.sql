CREATE SCHEMA IF NOT EXISTS prorepublica;

DROP TABLE IF EXISTS prorepublica.members_house;

CREATE TABLE IF NOT EXISTS prorepublica.members_house (
    congress int,
    chamber text,
    fec_candidate_id text,
    id text,
    first_name text,
    middle_name text,
    last_name text,
    gender text,
    date_of_birth date,
    state text,
    district text
);
