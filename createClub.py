import sqlite3
from datetime import date
from datetime import datetime

cam = sqlite3.connect('cam.db')
niu=cam.cursor()

# cam.execute("""CREATE TABLE club
# (SNO INTEGER PRIMARY KEY AUTOINCREMENT,
# NAME TEXT NOT NULL,
# DATE TEXT NOT NULL,
# MEMBERS INT NOT NULL,
# DESC TEXT NOT NULL,
# EVENTS INT,
# VALUE TEXT,
# TRANS TEXT,
# SHARE TEXT,
# VAULT REAL NOT NULL)""")

# #text for execom has stuent sno not name
# cam.execute("""CREATE TABLE execom
# (SNO INT NOT NULL UNIQUE,
# CHAIR TEXT NOT NULL,
# VC TEXT,
# TREASURER TEXT,
# SECRETERY TEXT,
# WEBMASTER TEXT,
# CONSTRAINT der_sno
# FOREIGN KEY(SNO) REFERENCES club(SNO))""")

# cam.commit()

def create_club():
    name = input("club name : ")
    num = input("num of members : ")
    desc = input("description : ")
    dat = str(date.today())
    
    cam.execute("INSERT INTO club(NAME,DATE,MEMBERS,DESC,VAULT) VALUES(?,?,?,?,0)",(name, dat, num, desc))
    x = list(niu.execute("SELECT MAX(SNO) FROM club"))[0][0]
    val = 'val' + str(x)
    trans = 'trans' + str(x)
    share = 'share' + str(x)
    
    #stock value
    cam.execute("CREATE TABLE "+val+"(week INTEGER PRIMARY KEY AUTOINCREMENT, mon REAL, wed REAL, thu REAL, sat REAL)")
    cam.execute("UPDATE club SET VALUE=? WHERE SNO=?",(val, x))
    
    #transaction and history
    cam.execute("CREATE TABLE "+trans+"(type text, timestamp text, amount REAL, other text)")
    cam.execute("UPDATE club SET TRANS=? WHERE SNO=?",(trans, x))
    
    #inverstor's ledger
    cam.execute("CREATE TABLE "+share+"(ssn text PRIMARY KEY, amount REAL)")
    cam.execute("UPDATE club SET VALUE=? WHERE SNO=?",(val, x))
    
    cam.commit()

def transf(sno, amt, typ, ssn):
    trans = 'trans' + str(sno)
    #type in-0 || out-1
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    bal = list(niu.execute("SELECT VAULT FROM club WHERE SNO=?",str(sno,)))[0][0]
    if(typ==1):
        if(bal<amt):
            #throw error
            pass
        else:
            bal-=amt
            cam.execute("UPDATE club SET VAULT=? WHERE SNO=?",(bal, str(sno)))
            cam.execute("INSERT INTO "+trans+"(type, timestamp, amount, other) VALUES(?,?,?,?)",('expenditure', dt_string, str(amt), ssn))

    else:
        bal+=amt
        cam.execute("UPDATE club SET VAULT=? WHERE SNO=?",(bal, str(sno)))
        cam.execute("INSERT INTO "+trans+"(type, timestamp, amount, other) VALUES(?,?,?,?)",('income', dt_string, str(amt), ssn))
    
    cam.commit()


niu.close()
cam.close()

