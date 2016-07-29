
while true
do 
    date
    zip -r /var/www/html/webroot/surgujaMIS/latehar.zip /var/www/html/webroot/surgujaMIS/LATEHAR/*
    python downloadMISReports.py -d latehar -f 17
    python downloadMISReports.py -d latehar -f 16
done
