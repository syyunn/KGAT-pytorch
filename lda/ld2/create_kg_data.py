from lda.utils import create_connection, select_data_from_postgres

query = """
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
select distinct client_id as id, 'client' as entity_type from sample
order by client_id asc 
)
, distinct_registrants as (
select distinct regis_id as id, 'registrant' as entity_type from sample
order by regis_id asc 
)
, distinct_entities as (
select * from distinct_clients 
union all
select * from distinct_registrants
)
, distinct_gic as (
select distinct general_issue_code from sample
order by general_issue_code asc
)
, distinct_entities_w_rnum as (
select row_number() OVER () as rnum, id, entity_type from distinct_entities
)
, distinct_gic_w_rnum_original as (
select row_number() OVER () as rnum, general_issue_code from distinct_gic
)
, distinct_gic_w_rnum as (
select (rnum - 1) as rnum, general_issue_code from distinct_gic_w_rnum_original
)
, distinct_client_w_rnum as (
select distinct (rnum-1) as rnum, id, entity_type from distinct_entities_w_rnum
where entity_type = 'client'
)
, distinct_regis_w_rnum as (
select distinct (rnum-1) as rnum, id, entity_type from distinct_entities_w_rnum
where entity_type = 'registrant'
)
select cr.rnum as client_rnum, gicr.rnum as gic_rnum, rr.rnum as regis_rnum -- , s.client, s.regis, s.client_id, s.regis_id
from sample s
	inner join distinct_client_w_rnum cr on cr.id = s.client_id
	inner join distinct_regis_w_rnum rr on rr.id = s.regis_id
	inner join distinct_gic_w_rnum gicr on gicr.general_issue_code = s.general_issue_code	
"""

conn = create_connection()
df = select_data_from_postgres(conn, query)

import os
import numpy as np

prefix = "/tmp/pycharm_project_478/datasets/lda"
np.savetxt(os.path.join(prefix, "kg_final.txt"), df.values, fmt="%d")

if __name__ == "__main__":
    pass
