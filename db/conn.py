import psycopg2

def open_conn():
    conn = psycopg2.connect(
        host="localhost",
        port="5435",
        database="postgiscwb",
        user="postread",
        password="PostRead")
    
    return conn

if __name__ == '__main__':
    print(open_conn())