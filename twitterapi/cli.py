"""
	This command line script can be run with any Twitter endpoint.  The json-formatted
	response is printed to the console.  The script works with both Streaming API and
	REST API endpoints.

	IMPORTANT: Before using this script, you must enter your Twitter application's OAuth 
	credentials in TwitterAPI/credentials.txt.  Log into to dev.twitter.com to create 
	your application.
	
	Examples:
	
	> python cly.py -endpoint search/tweets -parameters q=zzz 
	> python cly.py -endpoint statuses/filter -parameters track=zzz
		
	These examples print the raw json response.  You can also print one or more fields
	from the response, for instance the tweet 'text' field, like this:
	
	> python cly.py -endpoint statuses/filter -parameters track=zzz -fields text
		
	Twitter's endpoints are documented at this site:
		https://dev.twitter.com/docs/api/1.1
"""

__author__ = "Jonas Geduldig"
__date__ = "June 7, 2013"
__license__ = "MIT"

# unicode printing for Windows 
import sys, codecs
sys.stdout = codecs.getwriter('utf8')(sys.stdout)

import argparse
import constants
import pprint
from TwitterOAuth import TwitterOAuth
from TwitterAPI import TwitterAPI


def find_field(name, obj):
	"""Breadth-first search of the JSON result fields."""
	q = []
	q.append(obj)
	while q:
		obj = q.pop(0)
		if hasattr(obj, '__iter__'):
			isdict = type(obj) is dict
			if isdict and name in obj:
				return obj[name]
			for k in obj:
				q.append(obj[k] if isdict else k)
	else:
		return None


def to_dict(param_list):
	"""Convert a list of key=value to dict[key]=value"""			
	if param_list is not None:
		return {name: value for (name, value) in [param.split('=') for param in param_list]}
	else:
		return None


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Request any Twitter Streaming or REST API endpoint')
	parser.add_argument('-oauth', metavar='FILENAME', type=str, help='file containing OAuth credentials')
	parser.add_argument('-endpoint', metavar='ENDPOINT', type=str, help='Twitter endpoint', required=True)
	parser.add_argument('-parameters', metavar='NAME_VALUE', type=str, help='parameter NAME=VALUE', nargs='+')
	parser.add_argument('-fields', metavar='FIELD', type=str, help='print a top-level field in the json response', nargs='+')
	args = parser.parse_args()	

	try:
		params = to_dict(args.parameters)
		#oauth = TwitterOAuth.read_file(args.oauth)
		oauth = TwitterOAuth('1M7kTHFb4aDJYaH3w3np9g',
							 'NWfJ1wE12Cjh677buqObs1jSKzvXhEP0tJ0zYcbQ5Kw',
							 '43513175-iznkrt1saCyFyzSyaHuOTLcceGPGXHcz6rgQHM2A6',
							 'xWtKlDyeiuAmUmgZtTBZtsEivCd9HqXc2FWaUy8')

		api = TwitterAPI(oauth.consumer_key, oauth.consumer_secret, oauth.access_token_key, oauth.access_token_secret)
		api.request(args.endpoint, params)
		iter = api.get_iterator()
		
		pp = pprint.PrettyPrinter()
		for item in iter:
			if 'message' in item:
				print 'ERROR:', item['message']
			elif args.fields is None:
				pp.pprint(item)
			else:
				for name in args.fields:
					value = find_field(name, item)
					if value is not None:
						print '%s: %s' % (name, value)
						
	except KeyboardInterrupt:
		print>>sys.stderr, '\nTerminated by user'
		
	except Exception, e:
		print>>sys.stderr, '*** STOPPED', e