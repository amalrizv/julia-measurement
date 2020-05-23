MYCMD=$1
for i in 02 03 04 05 06 08 12 13 14 15 16 17 18
do 
	echo "torusnode$i"
	ssh torusnode$i $MYCMD
done
