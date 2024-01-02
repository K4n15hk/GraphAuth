import sqlite3
#creating a function to check if a database exists in path specified
def ifdbexists(filename):
    try:
        conn_query='file:'+filename+'?mode=r0'
        db_conn=sqlite3.connect(f"file:{filename}?mode=ro",uri =True)
        db_conn.close()
        return True
    except:
        return False    
db_name="GraphAuthUserDatabase.db"
if ifdbexists(db_name):
    print("Exists")
else:
    print("NO")
    x=input("Create Now?[y/n]: ")
    if x=="y":
        db_conn=sqlite3.connect(db_name)
        cursor=db_conn.cursor()
        query='''CREATE TABLE USERDB(
        UserName TEXT NOT NULL,
        img_1 BLOB,
        img_2 BLOB,
        img_3 BLOB,
        img_4 BLOB,
        img_5 BLOB,
        img_6 BLOB,
        img_7 BLOB,
        img_8 BLOB,
        img_9 BLOB,
        userhash BLOB,
        tries INTEGER)'''
        cursor.execute(query)
        db_conn.close()
        print("Database Created")
    elif x=="n":
        print("OK")
    else:
        print("Invalid Input,Exiting.")
