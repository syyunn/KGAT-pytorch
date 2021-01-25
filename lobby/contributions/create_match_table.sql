CREATE SCHEMA IF NOT EXISTS senate_lda_api_v1_propublica;

DROP TABLE IF EXISTS senate_lda_api_v1_propublica.match_honoree_legislator;

CREATE TABLE IF NOT EXISTS senate_lda_api_v1_propublica.match_honoree_legislator(
    filing_uuid uuid,
    contribution_item_ord int,
    honoree_name text,
    honoree_clean text,
    propublica text,
    id text,
    score float
    );
