import re
def getString(a):
  if isinstance(a, basestring):
    try:
      a.decode('ascii')
    except UnicodeDecodeError:
      #return "it was not a ascii-encoded unicode string"
      return a.decode("UTF-8")
    else:
      #return "It may have been an ascii-encoded unicode string"
      return a
  else:
    return str(a)

def getCenterAligned(text):
  return '<div align="center">%s</div>' % text

def htmlWrapper(title = None, head = None, body = None):
  html_text = '''
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <!-- The above 3 meta tags *must* come first in the head; any other head content must come *after* these tags -->
    
    <title>title_text</title>

    <!-- Bootstrap -->

    <!-- Latest compiled and minified CSS -->
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/css/bootstrap.min.css">

    <!-- Optional theme -->
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/css/bootstrap-theme.min.css">

    <div align="center">head_text</div>

  </head>
    
  <body>

    body_text
    
    <!-- jQuery (necessary for Bootstrap"s JavaScript plugins) -->
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.3/jquery.min.js"></script>
    <!-- Include all compiled plugins (below), or include individual files as needed -->

    <!-- Latest compiled and minified JavaScript -->
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/js/bootstrap.min.js"></script>

  </body>
</html>
'''
  html_text = html_text.replace('title_text', title)
  html_text = html_text.replace('head_text', head)
  html_text = html_text.replace('body_text', body)

  return html_text

def htmlWrapperLocal(title = None, head = None, body = None):
  html_text = '''
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <!-- The above 3 meta tags *must* come first in the head; any other head content must come *after* these tags -->
    
    <title>title_text</title>

    <!-- Bootstrap -->

    <!-- Latest compiled and minified CSS -->
    <link rel="stylesheet" href="/css/bootstrap.min.css">

    <!-- Optional theme -->
    <link rel="stylesheet" href="/css/bootstrap-theme.min.css">

    <div align="center">head_text</div>

  </head>
    
  <body>

    body_text
    
    <!-- jQuery (necessary for Bootstrap"s JavaScript plugins) -->
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.3/jquery.min.js"></script>
    <!-- Include all compiled plugins (below), or include individual files as needed -->

    <!-- Latest compiled and minified JavaScript -->
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/js/bootstrap.min.js"></script>

  </body>
</html>
'''
  html_text = html_text.replace('title_text', title)
  html_text = html_text.replace('head_text', head)
  html_text = html_text.replace('body_text', body)

  return html_text


def bsQuery2Html(cur, query, query_caption=None, field_names=None, extra=None):

  cur.execute(query)
  results = cur.fetchall()

  if query_caption == None:
    query_caption = "Query:"

  if field_names == None:
    field_names = [i[0] for i in cur.description]
  num_fields = len(cur.description)
  
  table_html='''
<div class="container">
  <h2>query_caption</h2>
  <pre>    query_text</pre>
  <table class="table table-striped">
    <thead>
      <tr>
      '''

  for field_name in field_names:
    table_html += "<th>" + field_name.strip() + "</th>"

  table_html += '''
      </tr>
    </thead>
    <tbody>
      <tr>
      '''
  
  for row in results:
    table_html += "<tr>"

    i = 0
    while i < num_fields:
      table_html += "<td>" + getString(row[i]) + "</td>"
      i += 1

    if extra != None:
      table_html += "<td>" + extra.replace('section_tag',str(row[0])).replace('section_text',str(row[0])) + "</td>"
      table_html = table_html.replace('jobcard_value', str(row[0]))

    table_html += "</tr>"

  table_html += '''
    </tbody>
  </table>
</div>
  '''
  return table_html.replace('query_caption', query_caption).replace('query_text', query).replace('colspan_value', str(num_fields))


def getForm(qid, action_text, form_type, button_text, query_text = None):
  if query_text == None:
    query_text = ''
    
  form_html = '''
  <form action="action_text" method="POST">
    form_text
  </form>
'''
  form_html = form_html.replace('action_text', action_text)

  form_text = '''
    <div class="row">

      <div class="col-xs-2">
      </div>

      <div class="col-xs-8">
        <div class="input-group">
          <input name="qid" value="qid_value" type="hidden">
          <input name="formType" value="form_type" type="hidden">
          <input name="query" type="text" class="form-control" placeholder="Query..." value="query_text">
          <span class="input-group-btn">
            <button type="submit" class="btn btn-default">button_text</button>
          </span>
        </div>
      </div>

      <div class="col-xs-2">
      </div>

    </div>
'''
  form_text = form_text.replace('qid_value', str(qid))
  form_text = form_text.replace('form_type', form_type)
  form_text = form_text.replace('button_text', button_text)
  form_text = form_text.replace('query_text', query_text)

  input_element = '''
        <div class="input-group">
          <input type="text" class="form-control" placeholder="Query...">
        </div>
'''  

  formhtml='<br /><form action="./queryDashboardPost.py" method="POST"><input name="qid" value="%s" type="hidden"><input name="formType" value="%s" type="hidden"></input>%s<button type="submit">%s</button></form>' %(qid, form_type, input_element, "Go")
  
#  return formhtml
  return form_html.replace('form_text', form_text)


def getButton(jobcard, action_text, form_type, button_text):
  form_html = '''
  <form action="action_text" method="POST">
    form_text
  </form>
'''
  form_html = form_html.replace('action_text', action_text)

  form_text = '''
        <div class="input-group">
          <input name="jobcardValue" value="jobcard_value" type="hidden">
          <input name="formType" value="form_type" type="hidden">
          <button type="submit" class="btn btn-default">button_text</button>
        </div>
'''
#  form_text = form_text.replace('jobcard_value', str(jobcard))
  form_text = form_text.replace('form_type', form_type)
  form_text = form_text.replace('button_text', button_text)

  return form_html.replace('form_text', form_text)

def bsQuery2HtmlV2(cur, query, query_caption=None, field_names=None, extra=None,extraLabel=None,hiddenNames=None,hiddenValues=None):

  cur.execute(query)
  results = cur.fetchall()

  if query_caption == None:
    query_caption = "Query:"

  if field_names == None:
    field_names = [i[0] for i in cur.description]
  num_fields = len(cur.description)
  
  table_html='''
<div class="container">
  <pre>    query_text</pre>
  <table class="table table-striped">
    <thead>
      <tr>
      '''

  for field_name in field_names:
    table_html += "<th>" + field_name.strip() + "</th>"

  if extra != None:
    table_html += "<th>" + extraLabel + "</th>"

  table_html += '''
      </tr>
    </thead>
    <tbody>
      <tr>
      '''
  
  for row in results:
    inputs=''
    i=0
    if hiddenNames != None:
      for inputName in hiddenNames:
        inputValue=row[hiddenValues[i]]
        i=i+1
        inputs+='<input name="%s" value="%s" type="hidden">' %(inputName,inputValue)


    table_html += "<tr>"

    i = 0
    while i < num_fields:
      table_html += "<td>" + getString(row[i]) + "</td>"
      i += 1

    if extra != None:
      table_html += "<td>" + extra.replace('extrainputs',inputs) + "</td>"

    table_html += "</tr>"

  table_html += '''
    </tbody>
  </table>
</div>
  '''
  return table_html

def getButtonV2(action_text, form_type, button_text):


  form_html = '''
  <form action="action_text" method="POST">
    form_text
  </form>
'''
  form_html = form_html.replace('action_text', action_text)

  form_text = '''
        <div class="input-group">
          <input name="formType" value="form_type" type="hidden">
          extrainputs 
          <button type="submit" class="btn btn-default">button_text</button>
        </div>
''' 
#  form_text = form_text.replace('jobcard_value', str(jobcard))
  form_text = form_text.replace('form_type', form_type)
  form_text = form_text.replace('button_text', button_text)

  return form_html.replace('form_text', form_text)

def getButtonV3(action_text, form_type, button_text):


  form_html = '''
  <form action="action_text" method="POST" enctype="multipart/form-data" >
    form_text
  </form>
'''
  form_html = form_html.replace('action_text', action_text)

  form_text = '''
        <div class="input-group">
          <input name="formType" value="form_type" type="hidden">
          extrainputs 
          <button type="submit" class="btn btn-default">button_text</button>
        </div>
''' 
#  form_text = form_text.replace('jobcard_value', str(jobcard))
  form_text = form_text.replace('form_type', form_type)
  form_text = form_text.replace('button_text', button_text)

  return form_html.replace('form_text', form_text)

def bsQuery2HTMLLinkV1(cur, query, query_caption=None, field_names=None, extra=None,extraLabel=None,hiddenNames=None,hiddenValues=None):

  cur.execute(query)
  results = cur.fetchall()

  if query_caption == None:
    query_caption = "Query:"

  if field_names == None:
    field_names = [i[0] for i in cur.description]
  num_fields = len(cur.description)
  
  table_html='''
<div class="container col-xs-6">
  <div class="table-responsive">
  <table class="table table-striped">
    <thead>
      <tr class="info">
      '''
  i=0
  for field_name in field_names:
    if i==0:
      table_html += "<th >" + field_name.strip() + "</th>"
    i=i+1 
  if extra != None:
    table_html += "<th >" + extraLabel + "</th>"

  table_html += '''
      </tr>
    </thead>
    <tbody>
      <tr class="info">
      '''
  
  baseLink='<a href="./dataDashboardMain.py?extrainputs">linktext</a>'
  for row in results:
    inputs=''
    i=0
    if hiddenNames != None:
      for inputName in hiddenNames:
        inputValue=row[hiddenValues[i]]
        i=i+1
        inputs+='%s=%s&' % (inputName,inputValue)
    linkValue=baseLink.replace("extrainputs",inputs)
    linkValue=linkValue[:-1]
    table_html += "<tr class='success'>"

    i = 0
    while i < num_fields:
      if i==0:
        rowvalue=linkValue.replace("linktext",row[i])
        table_html += "<td>" + getString(rowvalue) + "</td>"
      #else:
      #  table_html += "<td>" + getString(row[i]) + "</td>"
      i += 1

    if extra != None:
      table_html += "<td>" + extra.replace('extrainputs',inputs) + "</td>"

    table_html += "</tr>"

  table_html += '''
    </tbody>
  </table>
  </div>
</div>
  '''
  return table_html

def bsQuery2HtmlV3(cur, query, query_caption=None, field_names=None, extra=None,extraLabel=None,hiddenNames=None,hiddenValues=None):

  cur.execute(query)
  results = cur.fetchall()

  if query_caption == None:
    query_caption = "Query:"

  if field_names == None:
    field_names = [i[0] for i in cur.description]
  num_fields = len(cur.description)
  
  table_html='''
<div class="container col-xs-6">
  <div class="table-responsive">
  <table class="table table-striped">
    <thead>
      <tr class="danger">
      '''

  for field_name in field_names:
    table_html += "<th>" + field_name.strip() + "</th>"

  if extra != None:
    table_html += "<th>" + extraLabel + "</th>"

  table_html += '''
      </tr>
    </thead>
    <tbody>
      <tr>
      '''
  
  for row in results:
    inputs=''
    i=0
    if hiddenNames != None:
      for inputName in hiddenNames:
        inputValue=row[hiddenValues[i]]
        i=i+1
        inputs+='<input name="%s" value="%s" type="hidden">' %(inputName,inputValue)


    table_html += '<tr class="warning">'

    i = 0
    while i < num_fields:
      table_html += "<td>" + getString(row[i]) + "</td>"
      i += 1

    if extra != None:
      table_html += "<td>" + extra.replace('extrainputs',inputs) + "</td>"

    table_html += "</tr>"

  table_html += '''
    </tbody>
  </table>
  </div>
</div>
  '''
  return table_html


def libtechInsertLink(cur,myhtml):
  m=re.findall ( '<td>libtechConvertToLinkMusterNo(.*?)</td>',myhtml, re.DOTALL);
  for musterID in m:
    musterLink="http://surguja.libtech.info/nrega/SURGUJA/UDAIPUR/CHAINPUR/MUSTERS/2015-2016/11788.html"
    query="select b.name,p.name,m.musterNo,m.isDownloaded from musters m, blocks b,panchayats p where m.blockCode=b.blockCode and m.panchayatCode=p.panchayatCode and m.blockCode=p.blockCode and m.id=%s" % musterID
    cur.execute(query)
    row=cur.fetchone()
    blockName=row[0]
    panchayatName=row[1]
    musterNo=str(row[2])
    musterLink="http://surguja.libtech.info/nrega/SURGUJA/%s/%s/MUSTERS/2015-2016/%s" % (blockName.upper(),panchayatName.upper(),musterNo)  
    linkHTML='< a href="%s"> link </a>' %(musterLink)
    linkHTML='<a href="'+musterLink+'">'+musterNo+'</a>' 
    myhtml=myhtml.replace("libtechConvertToLinkMusterNo"+musterID,linkHTML)
  myhtml1=myhtml
  return myhtml1


def tabletUIQueryToHTMLTable(cur, query, staticLinkPath=None,field_names=None, extra=None,extraLabel=None,hiddenNames=None,hiddenValues=None):

  cur.execute(query)
  results = cur.fetchall()


  if field_names == None:
    field_names = [i[0] for i in cur.description]
  num_fields = len(cur.description)
  
  table_html='''
<div class="container col-xs-6">
  <div class="table-responsive">
  <table class="table table-striped">
    <thead>
      <tr class="info">
      '''
  i=0
  for field_name in field_names:
    if i==0:
      table_html += "<th >" + field_name.strip() + "</th>"
    i=i+1 
  if extra != None:
    table_html += "<th >" + extraLabel + "</th>"

  table_html += '''
      </tr>
    </thead>
    <tbody>
      '''
  
  for row in results:
    inputs=''
    table_html += "<tr class='success'>"

    i = 0
    while i < num_fields:
      if i==0:
        rowstripped=row[0].replace(" ","")
        if staticLinkPath != None:
          rowvalue='<a href="./%s/%s.html"> %s </a>' % (staticLinkPath,rowstripped.upper(),row[0])
        else:
          rowvalue='<a href="./%s/%s.html"> %s </a>' % (rowstripped.upper(),rowstripped.upper(),row[0])
       # rowvalue=linkValue.replace("linktext",row[i])
        table_html += "<td>" + getString(rowvalue) + "</td>"
      else:
        table_html += "<td>" + getString(row[i]) + "</td>"
      i += 1


    table_html += "</tr>"

  table_html += '''
    </tbody>
  </table>
  </div>
</div>
  '''
  return table_html
def tabletUIQuery2HTML(cur, query, query_caption=None, districtName=None,blockName=None,panchayatName=None,field_names=None, extra=None,extraLabel=None,hiddenNames=None,hiddenValues=None):

  cur.execute(query)
  results = cur.fetchall()

  if query_caption == None:
    query_caption = "Query:"

  if field_names == None:
    field_names = [i[0] for i in cur.description]
  num_fields = len(cur.description)
  
  table_html='''
<div class="container">
  <pre>    query_text</pre>
  <table class="table table-striped">
    <thead>
      <tr>
      '''

  for field_name in field_names:
    table_html += "<th>" + field_name.strip() + "</th>"


  table_html += '''
      </tr>
    </thead>
    <tbody>
      <tr>
      '''
  
  for row in results:
    inputs=''
    i=0
  # if hiddenNames != None:
  #   for inputName in hiddenNames:
  #     inputValue=row[hiddenValues[i]]
  #     i=i+1
  #     inputs+='<input name="%s" value="%s" type="hidden">' %(inputName,inputValue)


    table_html += "<tr>"

    i = 0
    while i < num_fields:
      rowvalue=row[i]
      if rowvalue is not None:
        baseLinkTarget="http://surguja.libtech.info"
        if hiddenNames != None:
          if str(i) in hiddenValues:
            j=hiddenValues.index(str(i))
            linktype=hiddenNames[j]
            if linktype == 'jobcard':
              baseLinkTarget='../jobcardRegister/'+rowvalue.replace("/","_")+'.html'
            if linktype == 'muster':
              baseLinkPath='/nrega/%s/%s/%s/MUSTERS/2015-2016/' % (districtName.upper(),blockName.upper(),panchayatName.upper())
              #print rowvalue
              baseLinkTarget=baseLinkPath+rowvalue+'.html'
            if linktype == 'fto':
              baseLinkPath='/nrega/%s/%s/FTO/2015-2016/' % (districtName.upper(),blockName.upper())
              baseLinkTarget=baseLinkPath+rowvalue.replace("/","_")+'.html'
            rowvalue='<a href="%s">%s</a>'%(baseLinkTarget,rowvalue)
      table_html += "<td>" + getString(rowvalue) + "</td>"
      i += 1

    if extra != None:
      table_html += "<td>" + extra.replace('extrainputs',inputs) + "</td>"

    table_html += "</tr>"

  table_html += '''
    </tbody>
  </table>
</div>
  '''
  return table_html

def tabletUIReportTable(cur, query, staticLinkPath=None,field_names=None, extra=None,extraLabel=None,hiddenNames=None,hiddenValues=None):

  cur.execute(query)
  results = cur.fetchall()


  if field_names == None:
    field_names = [i[0] for i in cur.description]
  num_fields = len(cur.description)
  
  table_html='''
<div class="container col-xs-6">
  <div class="table-responsive">
  <table class="table table-striped">
    <thead>
      <tr class="info">
      '''
  i=0
  for field_name in field_names:
    table_html += "<th >" + field_name.strip() + "</th>"
    i=i+1 
  table_html += "<th colspan=3>View HTML</th>"
  table_html += "<th > | </th>"
  table_html += "<th colspan=3>Download CSV</th>"
  if extra != None:
    table_html += "<th >" + extraLabel + "</th>"

  table_html += '''
      </tr>
    </thead>
    <tbody>
      '''
  
  for row in results:
    inputs=''
    table_html += "<tr class='success'>"

    i = 0
    while i < num_fields:
      if i==1:
        rowstripped=row[1].replace(" ","")
        if staticLinkPath != None:
          targetLink="./%s/%s.html" % (staticLinkPath,rowstripped)
          targetcsv="./%s/%s.csv" % (staticLinkPath,rowstripped)
          targetLink16="./%s/%s.html" % (staticLinkPath+'16',rowstripped)
          targetcsv16="./%s/%s.csv" % (staticLinkPath+'16',rowstripped)
          targetLink17="./%s/%s.html" % (staticLinkPath+'17',rowstripped)
          targetcsv17="./%s/%s.csv" % (staticLinkPath+'17',rowstripped)
          rowvalue='<a href="./%s/%s.html"> %s </a>' % (staticLinkPath,rowstripped,row[1])
        else:
          rowvalue='<a href="./%s/%s.html"> %s </a>' % (rowstripped.upper(),rowstripped.upper(),row[1])
       # rowvalue=linkValue.replace("linktext",row[i])
        table_html += "<td>" + getString(rowvalue) + "</td>"
      else:
        table_html += "<td>" + getString(row[i]) + "</td>"
      i += 1

    myForm=getButtonV3(targetLink,'viewHTML','All')
    myForm=myForm.replace("extrainputs","")
    table_html += "<td>  " + myForm + "</td>"
    myForm=getButtonV3(targetLink16,'viewHTML','FY16')
    myForm=myForm.replace("extrainputs","")
    table_html += "<td>" + myForm + "</td>"
    myForm=getButtonV3(targetLink17,'viewHTML','FY17')
    myForm=myForm.replace("extrainputs","")
    table_html += "<td>" + myForm + "</td>"

    table_html += "<td > | </td>"
    myForm=getButtonV3(targetcsv,'viewCSV','All')
    myForm=myForm.replace("extrainputs","")
    table_html += "<td>" + myForm + "</td>"
    myForm=getButtonV3(targetcsv16,'viewCSV','FY16')
    myForm=myForm.replace("extrainputs","")
    table_html += "<td>" + myForm + "</td>"
    myForm=getButtonV3(targetcsv17,'viewCSV','FY17')
    myForm=myForm.replace("extrainputs","")
    table_html += "<td>" + myForm + "</td>"

    table_html += "</tr>"

  table_html += '''
    </tbody>
  </table>
  </div>
</div>
  '''
  return table_html


def main():
  testSuite()

if __name__ == '__main__':
  main()
