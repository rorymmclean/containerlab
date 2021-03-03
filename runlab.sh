sed -e 's/'$1'/'$1$2'/g; s/LabPort01/'$3'/g; s/LabPort02/'$4'/g; s/LabPort03/'$5'/g; s/LabPort04/'$6'/g; s/LabPort05/'$7'/g; s/LabPort06/'$8'/g;' ./compose/$1.yaml > ./compose/$1-$2.yaml
docker-compose -f ./compose/$1-$2.yaml -p $1-$2 up -d
