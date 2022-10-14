import psycopg2 as pg


class Connection218(object):
    def __init__(self, region):
        conn = pg.connect(
            host='10.10.2.18',
            dbname='Support',
            user='postgres',
            password='Abu pfgjvybim'
        )
        cursor = conn.cursor()
        if region != 'all':
            cursor.execute("""
                SELECT ipr.region, ipr.ip_address, ipr.title, ti.rec_date, ti.enterprise, ti.body
                FROM t_ip_reference ipr
                INNER JOIN t_regions tr ON ipr.region = tr.id
                INNER JOIN t_information ti ON ipr.ip_address = ti.owner_ip
                WHERE ipr.enabled = True  AND ipr.region = {}
                ORDER BY ipr.region
                """.format(region))
        else:
            cursor.execute("""
                SELECT ipr.region, ipr.ip_address, ipr.title, ti.rec_date, ti.enterprise, ti.body
                FROM t_ip_reference ipr
                INNER JOIN t_regions tr ON ipr.region = tr.id
                INNER JOIN t_information ti ON ipr.ip_address = ti.owner_ip
                WHERE ipr.enabled = True 
                ORDER BY ipr.region
                """.format(region))
        self.serverlist = cursor.fetchall()

    def get_server_list(self):
        return self.serverlist

            
        
    
        