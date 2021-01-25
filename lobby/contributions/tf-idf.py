from lobby.utils import create_connection, select_data_from_postgres

conn = create_connection()

honoree_names_distinct = """
    with contribution_sample as (
    select * from senate_lda_api_v1.contributions c 
        inner join senate_lda_api_v1.contribution_items ci on c.filing_uuid = ci.filing_uuid 
    --where dt_posted > '2020-10-01'::timestamptz and c.filing_year = 2020
    order by c.dt_posted desc, c.filing_uuid, contribution_item_ord asc
    )
    select distinct honoree_name from contribution_sample
"""

df = select_data_from_postgres(conn, honoree_names_distinct)

import texthero as hero

df['honoree_name_tokenized'] = df['honoree_name'].apply(lambda x: x.split(' ') if x else [])

import pandas as pd
import numpy as np

tf = df['honoree_name_tokenized'].apply(pd.value_counts).fillna(0)
idf = np.log((len(df) + 1 ) / (tf.gt(0).sum() + 1))

idf = idf.sort_values(ascending=True)


if __name__ == "__main__":
    pass

