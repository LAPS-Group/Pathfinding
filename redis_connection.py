import redis

#A simple file that creates the variable redis_connection, which lets you do
#Redis stuff regardless of the name of the Redis container.
redis_connection = redis.StrictRedis(host='dockers_redis_1', port=6379)