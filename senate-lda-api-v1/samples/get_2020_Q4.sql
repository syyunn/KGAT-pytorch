with sample as (
select filing_uuid, r.name as regis, c.name as client, r.id as regis_id, c.id as client_id from senate_lda_api_v1.filings f
	inner join senate_lda_api_v1.registrants r on r.id = f.registrants_id
	inner join senate_lda_api_v1.clients c on c.id = f.clients_id
where filing_year = 2020 and filing_type = 'Q4'
order by f.dt_posted desc
)
select count(*) from sample