import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="patapouf",
  database='tipe'
)
#===FONCTIONS========================================

#? Trois principes : Création , Suppression, Récupération

def creation_table_vide_colonne(nom,colonne,type_de_donnée="VARCHAR(255)") :
  mycursor = mydb.cursor()
  mycursor.execute("CREATE TABLE {} ({} {})".format(nom,colonne,type_de_donnée))
  mycursor.close

def creation_ajout_colonne(table,colonne,type_de_donnée="VARCHAR(255)"):
  mycursor = mydb.cursor()
  mycursor.execute("ALTER TABLE {} ADD COLUMN {} {}".format(table,colonne,type_de_donnée))
  mycursor.close

def creation_insertion_donnée_unique(table,colonne,donnée) :
  mycursor = mydb.cursor()
  sql = "INSERT INTO {} ({}) VALUES (%s)".format(table,colonne)
  val = ("{}".format(donnée))
  mycursor.execute(sql, val)
  mydb.commit()
  mycursor.close

def creation_insertion_données(table,colonne,données) :
  mycursor = mydb.cursor()
  sql = "INSERT INTO {} {} VALUES (%s)".format(table,colonne)
  val = [i for i in données]

  mycursor.executemany(sql, val)
  mydb.commit()
  mycursor.close

def suppression_table(table) :
  mycursor = mydb.cursor()
  sql = "DROP TABLE {}".format(table)
  mycursor.execute(sql)
  mycursor.close

def récupération_et_suppression_de_colonne(table,colonne) :

  mycursor = mydb.cursor()
  mycursor.execute("SELECT {} FROM {}".format(colonne,table))
  liste = mycursor.fetchall()

  sql = "DELETE FROM {}".format(table)
  mycursor.execute(sql)
  mydb.commit()
  mycursor.close
  
  return liste

creation_table_vide_colonne('table_test','robot1')
creation_insertion_données('table_test','robot1',['a','t_d'])


