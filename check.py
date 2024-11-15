import redis
r = redis.Redis(host='ehms-redis3.redis.cache.windows.net', port=6380, password='4V3i2If2NiavGbYHt5JpvAi7n0bLfSQIpAzCaDrCVoM=', ssl=True)
print(r.ping())
