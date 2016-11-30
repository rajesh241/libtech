import re



def formatName(name):
  formatName=re.sub(r"[^A-Za-z]+", '', name).lower()
  return formatName

