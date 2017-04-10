#!/usr/bin/python
import cgi
import cgitb; cgitb.enable() # Optional; for debugging only

print "Content-Type: text/html"
print ""
print "<h1> hey guys python is working. Am going to print the status here </h1>"
#arguments = cgi.FieldStorage()
#for i in arguments.keys():
# print arguments[i].value
# print "<html><h1>test</h1></html>"
