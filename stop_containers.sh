docker ps -a -q --filter="name=consensus"
docker ps -a -q --filter="name=settp"
docker ps -a -q --filter="name=rest-api"
docker ps -a -q --filter="name=validator"