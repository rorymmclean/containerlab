docker-compose -f ./compose/$1.yaml -p $1 down
rm -f ./compose/$1.yaml