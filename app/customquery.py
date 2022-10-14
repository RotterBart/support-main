import psycopg2 as pg 


def CustomQuery(ip, password, dbname, query):
	
	conn = pg.connect(
            host=ip,
            dbname=dbname,
            user='postgres',
            password=password
        )
	with conn.cursor() as cursor:
		cursor.execute(query)

		return cursor.fetchall()