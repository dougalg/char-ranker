"""
Char-Ranker - Rank Chars
"""

import os
import regex

from redis import Redis
from flask import Flask, request, jsonify, abort, make_response

app = Flask(__name__) # pylint: disable=invalid-name
redis = Redis(host=os.environ['REDIS_HOST'], port=os.environ['REDIS_PORT']) # pylint: disable=invalid-name


MAX_CHAR_LEN = 1
CHAR_RANK_ZSET = 'CHAR_SET'
ERROR_LONG_TEXT = "'{}' is not a valid char. It is too long: It is {} chars, but must not be more than {}"

@app.route('/api/char/<char>', methods=['GET'])
def retrieve(char):
	assert_valid_char(char)
	val = redis.zscore(CHAR_RANK_ZSET, char)
	return jsonify(char_response(char, val))

@app.route('/api/char/<char>/<op>', methods=['POST'])
def up_down(char, op):
	assert_valid_char(char)
	if (op not in ['up', 'down']):
		abort(404)
	inc = -1 if op == 'down' else 1
	val = redis.zincrby(CHAR_RANK_ZSET, char, inc)
	return char_response(char, val)

@app.route('/api/char/top/<num>', methods=['GET'])
def top_chars(num=5):
	res = redis.zrange(CHAR_RANK_ZSET, 0, num, desc=True, withscores=True)
	return jsonify([char_response(item[0].decode('utf-8'), item[1]) for item in res])

def char_response(char, val):
	val = 0 if val is None else val
	return {
		'char': char,
		'val': val
	}

def assert_valid_char(char):
	if get_unicode_char_length(char) > MAX_CHAR_LEN:
		error_message = ERROR_LONG_TEXT.format(char, get_unicode_char_length(char), MAX_CHAR_LEN)
		abort(make_response(jsonify({"error_message": error_message}), 404))

def get_unicode_char_length(char):
	return len(regex.findall(r'\X', char))

if __name__ == "__main__":
	app.run(host="0.0.0.0", debug=True, port=int(os.environ['BIND_PORT']))
