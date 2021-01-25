def create_connection():
    import psycopg2
    # Connection from pwr
    conn = psycopg2.connect(
        user="postgres",
        password="6z/.R^_6-UstW4f`",
        host="localhost",
        port="5432",
        database="postgres",
    )
    return conn


def copy_from_stringio(conn, df, table):
    """
    Here we are going save the dataframe in memory
    and use copy_from() to copy it to the table
    """
    from io import StringIO
    import psycopg2

    # save pd.DataFrame to an in memory buffer
    buffer = StringIO()
    df.to_csv(buffer, header=False, index=False, sep='\t')
    buffer.seek(0)
    cursor = conn.cursor()
    try:
        cursor.copy_from(buffer, table, sep="\t", null="")
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        conn.rollback()
        cursor.close()
        return 1
    print("copy_from_stringio() done")
    cursor.close()


def select_data_from_postgres(conn, query):
    import pandas as pd

    cursor = conn.cursor()  # cursor is kind of intermediary later that constitutes
    cursor.execute(query)
    df = pd.DataFrame(cursor.fetchall())
    df.columns = [i[0] for i in cursor.description]

    return df
