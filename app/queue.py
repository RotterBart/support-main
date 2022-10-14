import psycopg2 as pg


class Connection209(object):
    def __init__(self):
        conn = pg.connect(
            host='10.10.2.209',
            dbname='Integro.Agent',
            user='postgres',
            password='Abu pfgjvybim'
        )
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM t_queue
            """)
        self.serverlist = cursor.fetchall()

    def get_server_list(self):

        return self.serverlist