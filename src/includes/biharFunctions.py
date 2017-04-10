def cleanFPSName(inname):
  fpsName1 = inname.replace("'","")
  fpsName3 = fpsName1.replace("/", "")
  fpsName = fpsName3.replace(".", "")
  return fpsName
