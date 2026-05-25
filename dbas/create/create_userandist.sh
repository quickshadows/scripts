twc db ls | awk '/Postg/ && /Aleks/ {print $1}' | xargs -I {} twc db instance create {} db1

twc db ls | awk '/Postg/ && /Aleks/ {print $1}' | xargs -I {} twc db user create {} --login user1_api --password Passwd+++123 --privileges "SELECT,CREATE"