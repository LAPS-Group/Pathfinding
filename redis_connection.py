import redis, sys

# A simple file that connects to Redis and stores the connection in  redis_connection.
# Will default to 'dockers_redis_1' if there are no command-line arguments.
host = "dockers_redis_1"
port = 6379
if len(sys.argv) != 1 and len(sys.argv) != 3:
    raise Exception("Expected 2 or zero command line arguments")
elif len(sys.argv) == 3:
    host = sys.argv[1]
    port = sys.argv[2]



redis_connection = redis.StrictRedis(host=host, port=port)
