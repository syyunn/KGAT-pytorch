CREATE SCHEMA IF NOT EXISTS prorepublica;

DROP TABLE IF EXISTS prorepublica.members_senate;

CREATE TABLE IF NOT EXISTS prorepublica.members_senate (
    congress int,
    chamber text,
    fec_candidate_id text,
    id text,
    first_name text,
    middle_name text,
    last_name text,
    gender text,
    date_of_birth date,
    state text
);
