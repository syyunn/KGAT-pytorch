with contribution_sample as (
select * from senate_lda_api_v1.contributions c 
	inner join senate_lda_api_v1.contribution_items ci on c.filing_uuid = ci.filing_uuid 
where dt_posted > '2020-10-01'::timestamptz and c.filing_year = 2020
order by c.dt_posted desc, c.filing_uuid, contribution_item_ord asc
)
select distinct honoree_name from contribution_sample
