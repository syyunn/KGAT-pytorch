select * from prorepublica.members_senate mh 

select * from senate_lda_api_v1_propublica.match_honoree_legislator


with sample as (
select f.filing_uuid, c.name as client, r.name as regis,c.id as client_id, r.id as regis_id,  f.expenses, f.income, la.general_issue_code from senate_lda_api_v1.filings f
	inner join senate_lda_api_v1.registrants r on r.id = f.registrants_id
	inner join senate_lda_api_v1.clients c on c.id = f.clients_id
	inner join senate_lda_api_v1.lobbying_activities la on f.filing_uuid = la.filing_uuid 
where filing_year = 2020 and filing_type = 'Q4'
order by f.dt_posted, filing_uuid, general_issue_code desc
)
, distinct_relations as (
select distinct general_issue_code from sample
order by general_issue_code asc
)
, distinct_clients as (
select distinct client_id from sample
order by client_id asc 
)
, distinct_registrants as (
select distinct regis_id from sample
order by regis_id asc 
)
, distinct_gic as (
select distinct general_issue_code from sample
order by general_issue_code asc
)
, distinct_registrants_w_rnum as (
select row_number() OVER () as rnum, regis_id from distinct_registrants
)
, distinct_clients_w_rnum as (
select row_number() OVER () as rnum, client_id from distinct_clients
)
, distinct_gic_w_rnum as (
select row_number() OVER () as rnum, general_issue_code from distinct_gic
)
select s.*, cr.rnum as client_rnum, rr.rnum as regis_rnum, gicr.rnum as gic_rnum from sample s
	inner join distinct_clients_w_rnum cr on cr.client_id = s.client_id
	inner join distinct_registrants_w_rnum rr on rr.regis_id = s.regis_id
	inner join distinct_gic_w_rnum gicr on gicr.general_issue_code = s.general_issue_code	
	