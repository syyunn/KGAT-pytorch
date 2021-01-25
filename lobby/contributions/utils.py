from lobby.utils import select_data_from_postgres, create_connection


def get_congressmen(congress):
    conn = create_connection()
    congressmen_query_house = """
    select distinct id, concat(first_name, ' ', last_name) as first_last_name, congress, chamber 
            from prorepublica.members_house
            where congress = {}
    """.format(
        congress
    )

    df_congressmen_house = select_data_from_postgres(conn, congressmen_query_house)

    congressmen_query_senate = """
    select distinct id, concat(first_name, ' ', last_name) as first_last_name, congress, chamber 
            from prorepublica.members_senate
            where congress = {}
    """.format(
        congress
    )

    df_congressmen_senate = select_data_from_postgres(conn, congressmen_query_senate)

    df_congressmen = df_congressmen_house.append(
        df_congressmen_senate, ignore_index=True
    )
    return df_congressmen


def cleanse_honoree_name(x):
    if x:
        x = (
            x.replace("Rep.", "")
            .replace("Rep", "")
            .replace("Representative", "")
            .replace("Sen.", "")
            .replace("Congressman", "")
            .replace("Senator", "")
            .replace("PAC", "")
            .replace("Congress", "")
            .replace("Senate", "")
            .replace("Sen", "")
            .replace("Honorable", "")
            .replace("Candidate", "")
            .replace("U.S.", "")
            .replace("Committee", "")
            .replace("Democratic", "")
            .replace("Congresswoman", "")
            .replace("Congresswoman", "")
            .replace("Jr.", "")
            .replace("Leadership", "")
            .replace("State", "")
        )
        return x
    else:
        return x
