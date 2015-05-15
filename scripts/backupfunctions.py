import os
def savedb(db,filename,filepath):
  DB_HOST = 'localhost'
  DB_USER = 'root'
  DB_USER_PASSWORD = 'ccmpProject**'
  fullfilepath=filepath+filename
  dumpcmd = "mysqldump -u " + DB_USER + " -p" + DB_USER_PASSWORD + " " + db + " | gzip -c | cat > " + filepath + "/" + filename + ".sql.gz" 
  print dumpcmd
  os.system(dumpcmd)
