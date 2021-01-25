import json
import requests

import pandas as pd
from lobby.utils import create_connection, copy_from_stringio

chamber = "house"
congress = "116"
res = requests.get(
    "https://api.propublica.org/congress/v1/{}/{}/members.json".format(congress, chamber),
    headers={"X-API-Key": "bE56m8ifzeSgZMdbepGA7F9I7NFJp7491ewZOikM"},
)
data = json.loads(res.text)

results = data["results"]
members = results[0]["members"]

df = pd.DataFrame(members)
df['congress'] = congress
df['chamber'] = chamber

df = df[['congress', 'chamber', 'fec_candidate_id', 'id', 'first_name', 'middle_name', 'last_name', 'gender', 'date_of_birth', 'state', 'district']]

print(list(df))
if __name__ == "__main__":
    conn = create_connection()
    copy_from_stringio(conn=conn, df=df, table='prorepublica.members_house')
    pass
