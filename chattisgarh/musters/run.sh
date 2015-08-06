while true
do 
    date 
    rm -rf /tmp/tmp*
    sleep 10
    python downloadMusters.py  
    sleep 10
done

