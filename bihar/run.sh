while true
do 
    date 
    rm -rf /tmp/tmp*
    python downloadFPSStatus.py -limit 1 -d 1022
    #python downloadFPSStatus.py -limit 1  
#    sleep 100
#    sh downloadMustersWrapper.sh korea 16
done

