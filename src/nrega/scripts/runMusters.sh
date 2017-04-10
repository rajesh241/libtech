while true
do 
    date
    python downloadMusters.py -f 17 -b $1 -d $2 -limit 150 
done

