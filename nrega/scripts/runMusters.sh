while true
do 
    date
    python downloadMusters.py -f 17 -d latehar -limit 150 -b $1 
    #sh downloadMustersWrapper.sh surguja 16
#    sleep 100
#    sh downloadMustersWrapper.sh korea 16
done

