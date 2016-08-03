while true
do 
    date
    python downloadMusters.py -f $1 -d $2 -limit 150 
    #sh downloadMustersWrapper.sh surguja 16
#    sleep 100
#    sh downloadMustersWrapper.sh korea 16
done

