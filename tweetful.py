import authorization
import requests
import sys
import argparse

from urls import *
from secret import YAHOO_APP_ID

def make_parser():
    """ Construct the command line parser """
    description = 'Interact with Twitter from command line interface'
    parser = argparse.ArgumentParser(description=description)

    subparsers = parser.add_subparsers(help='Available commands')

    # Subparsers for the "update status / tweet" command
    put_parser = subparsers.add_parser('tweet', help='Update status / post a tweet')
    put_parser.add_argument('message', help='The message to post, must be no longer than 140 characters')
    put_parser.set_defaults(command="tweet")

    # Subparsers for the "see homepage tweets" command
    put_parser = subparsers.add_parser('home', help='See timeline of tweets on your Twitter homepage')
    put_parser.set_defaults(command='home')

    # Subparsers for the "get trending posts" command
    put_parser = subparsers.add_parser('trends', help='See trending topics globally or in your location')
    put_parser.add_argument('location', default='world', nargs='?',
                            help='The name of a location of interest')
    put_parser.set_defaults(command='trends')

    return parser

def tweet(message):
	auth = authorization.authorize()
	payload = {'status':message}
	return requests.post(UPDATE_STATUS_URL, auth=auth, params=payload)

def home():
	auth = authorization.authorize()
	return requests.get(TIMELINE_URL, auth=auth)

def trends(location):
	yahoo_response = requests.get(WOEID_URL.format(location_name = location, app_id = YAHOO_APP_ID))
	
	# I had a HELL OF A TIME trying to parse the XML (could access the "woeid" element but couldn't get at the value in between the tags) so I took this very clumsy approach instead ...
	open_tag = yahoo_response.text.find('<woeid>')
	close_tag = yahoo_response.text.find('</woeid>')
	woeid = int(yahoo_response.text[open_tag+len('<woeid>'):close_tag])
	payload = {'id':woeid}

	auth = authorization.authorize()

	return requests.get(GET_TRENDS_URL, auth=auth, params = payload)

def main():
	parser = make_parser()
	arguments = parser.parse_args(sys.argv[1:])

	# Convert parsed arguments from Namespace to dictionary
	arguments = vars(arguments)
	command = arguments.pop('command')

	if command == "tweet":
		response = tweet(**arguments)
		
		# check for an error, if so print the error message for the user
		try:
			response.json().get('errors')
			print response.json().get('errors')[0].get('message') + " Please try again."
		# otherwise confirm with user that the tweet was successful
		except:
			print "Tweet posted successfully on {}".format(response.json().get('created_at'))
	
	if command == "home":
		response = home(**arguments)
		# check for an error, if so print the error message for the user
		try:
			response.json().get('errors')
			print response.json().get('errors')[0].get('message') + " Please try again."
		# otherwise print out the tweets on the user's homepage
		except:
			print "Posts on twitter homepage:\n"
			for item in response.json():
				print "{} posted \'{}\' on {}".format(item.get('user').get('name'), item.get('text'), item.get('created_at'))


	if command == "trends":
		response = trends(**arguments)

		# check for an error, if so print the error message for the user
		try:
			response.json().get('errors')
			print response.json().get('errors')[0].get('message') + " Please try again."
		# otherwise print out the top trends for the user
		except:
			print "Top 10 trending Twitter topics in " + arguments.get('location') + ' :\n'
			for trend in response.json()[0].get('trends'):
				print trend.get('name')
			print
		
if __name__ == "__main__":
    main()