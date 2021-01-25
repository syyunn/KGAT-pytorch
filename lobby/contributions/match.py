from lobby.utils import create_connection, select_data_from_postgres, copy_from_stringio
import pandas as pd
from lobby.contributions.utils import get_congressmen, cleanse_honoree_name
from text_similarity import similarity

# select congressman w/ CONGRESS YEAR, SENATE, HOUSE

df_congressmen = get_congressmen(116)

query = """
        with contribution_sample as (
        select ci.filing_uuid, ci.contribution_item_ord, ci.honoree_name from senate_lda_api_v1.contributions c 
            inner join senate_lda_api_v1.contribution_items ci on c.filing_uuid = ci.filing_uuid 
        where dt_posted > '2020-10-01'::timestamptz and c.filing_year = 2020
        order by c.dt_posted desc, c.filing_uuid, contribution_item_ord asc
        )
        select * from contribution_sample
        """

conn = create_connection()
df_honorees = select_data_from_postgres(conn=conn, query=query)
df_honorees["honoree_clean"] = df_honorees["honoree_name"].apply(cleanse_honoree_name)

df_nsquare = pd.DataFrame.from_dict(
    {
        f: {s: similarity(f, s) for s in df_congressmen["first_last_name"]}
        for f in df_honorees["honoree_clean"]
    },
    orient="index",
)

print(len(list(set(df_honorees["honoree_clean"].to_list()))))

maxvals = df_nsquare.idxmax(axis=1)

match_table = pd.DataFrame({"propublica": maxvals.values,}, index=maxvals.index)

match_table["score"] = None
for enum, row in match_table.iterrows():
    score = df_nsquare[row["propublica"]].loc[row.name]
    match_table["score"].loc[row.name] = score
    pass

match_table = match_table.sort_values("score")

thres = 0.4
match_table_thres = match_table[match_table["score"] > thres]
match_table_thres["honoree_index"] = match_table_thres.index
match_table_w_id = pd.merge(
    match_table_thres,
    df_congressmen,
    left_on="propublica",
    right_on="first_last_name",
    how="left",
)
match_table_w_id = match_table_w_id[["propublica", "id", "score", "honoree_index"]]
df_honorees_w_match_result = pd.merge(
    df_honorees,
    match_table_w_id,
    left_on="honoree_clean",
    right_on="honoree_index",
    how="left",
)
df_honorees_w_match_result = df_honorees_w_match_result.loc[:, "filing_uuid":"score"]
df_honorees_w_match_result = df_honorees_w_match_result.where(
    pd.notnull(df_honorees_w_match_result), None
)
copy_from_stringio(conn, df_honorees_w_match_result, table='senate_lda_api_v1_propublica.match_honoree_legislator')

if __name__ == "__main__":
    pass
