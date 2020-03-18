from debian:latest
run apt-get update -y
run apt-get upgrade -y
run apt-get install python3 python3-redis python3-pil -y
workdir /workdir

copy build/laps.py build/redis_connection.py build/loader.py /workdir/
copy build/Dijkstra /workdir/

entrypoint ["python3", "dijkstra_module.py"]
