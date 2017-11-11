import unicodecsv as csv
import shutil
from io import BytesIO

def main():
  print("writing csv")
  f = BytesIO()
  w = csv.writer(f, encoding='utf-8', delimiter=',')
  c0="गुजरात"
  c1="महाराष्"
  a=[]
  a.append(c0)
  a.append(c1)
#  w.writerow((u'गुजरात', u'महाराष्ट्र'))
  w.writerow(a)
  f.seek(0)
  with open("/tmp/a.csv","wb") as f1:
    shutil.copyfileobj(f, f1)
if __name__ == '__main__':
  main()
