while true
do 
    date 
    python downloadMusters.py  
    rm -rf /tmp/tmp*
    sleep 10
done

