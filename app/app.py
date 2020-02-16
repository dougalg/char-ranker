import os
import unicodedata
import regex

from flask import Flask, request, jsonify, abort, make_response
from redis import Redis

app = Flask(__name__)
redis = Redis(host=os.environ['REDIS_HOST'], port=os.environ['REDIS_PORT'])


CHAR_SET = 'CHAR SET'

@app.route('/api/char/<char>', methods = ['GET'])
def retrieve(char):
	assert_valid_char(char)
	val = redis.zscore(CHAR_SET, char)
	return char_response(char, val)

@app.route('/api/char/<char>/<op>', methods = ['POST'])
def upDown(char, op):
	assert_valid_char(char)
	if (op not in [ 'up', 'down' ]):
		abort(404)
	inc = -1 if op == 'down' else 1
	val = redis.zincrby(CHAR_SET, char, inc)
	return char_response(char, val)

def char_response(char, val):
	val = 0 if val == None else val
	result = {
		'char': char,
		'val': val
	}
	return jsonify(result)

def assert_valid_char(char):
	if get_unicode_char_length(char) > 1:
		abort(make_response(jsonify({ "error_message": "'{}' is not a valid char. It is too long: {}".format(char, get_unicode_char_length(char)) }), 404))

def get_unicode_char_length(char):
	return len(regex.findall(r'\X', char))

if __name__ == "__main__":
	bind_port = int(os.environ['BIND_PORT'])
	app.run(host="0.0.0.0", debug=True, port=bind_port)
