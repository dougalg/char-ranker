import os

from flask import Flask
from redis import Redis


app = Flask(__name__)
redis = Redis(host=os.environ['REDIS_HOST'], port=os.environ['REDIS_PORT'])


@app.route('/api')
def hello2():
	redis.incr('hits')
	total_hits = redis.get('hits').decode()
	return f'Hello from Redis! I have been seen {total_hits} times.'


if __name__ == "__main__":
	bind_port = int(os.environ['BIND_PORT'])
	app.run(host="0.0.0.0", debug=True, port=bind_port)
