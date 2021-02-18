from graphql_client import GraphQLClient
from time import gmtime, strftime
from datetime import timedelta
import os.path
import configparser

endpoint_uri = "http://yourplatforminstance.com/graphql"
client = GraphQLClient(endpoint_uri)

def post_graphql_query(gql_query):
  gql_query = inject_utc_date_time(gql_query)
  print("Sending: " + gql_query)
  result = client.query(gql_query)
  print("Response: " + str(result))
  return result

def inject_utc_date_time(gql_query):
  start_time = strftime("%Y-%m-%dT%H:%M:%S", gmtime())
  gql_query = gql_query.replace("UTCStart", str(start_time))
  return gql_query