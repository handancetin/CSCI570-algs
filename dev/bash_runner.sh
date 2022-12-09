for f in {1..15};  
    do python3 basic_3.py datapoints/in$f.txt outputs_basic/output$f.txt
    do python3 efficient_3.py datapoints/in$f.txt outputs_efficient/output$f.txt
done
