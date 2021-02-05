#! /usr/bin/env python3

''' Dependenices to install via pip
      pip install requests '''

import argparse
import requests
import json

instance_graphql_endpoint = "https://YOURINSTANCE.cesmii.net/graphql"

''' You could opt to manually update the bearer token that you retreive from the Developer menu > GraphQL - Request Header token
      But be aware this is short-lived (you set the expiry, see Authenticator comments below) and you will need to handle
      expiry and renewal -- as shown below. As an alternative, you could start your life-cycle with authentication, or
      you could authenticate with each request (assuming bandwidth and latency aren't factors in your use-case). '''
# eg: Bearer eyJyb2xlIjoieW91cl9yb2xlIiwiZXhwIjoxNDk5OTk5OTk5LCJ1c2VyX25hbWUiOiJ5b3VydXNlcm5hbWUiLCJhdXRoZW50aWNhdG9yIjoieW91cmF1dGgiLCJhdXRoZW50aWNhdGlvbl9pZCI6Ijk5IiwiaWF0Ijo5OTk5OTk5OTk5LCJhdWQiOiJhdWQiLCJpc3MiOiJpc3MifQ==

parser = argparse.ArgumentParser()
''' These values come from your Authenticator, which you configure in the Developer menu > GraphQL Authenticator
    Rather than binding this connectivity directly to a user, we bind it to an Authenticator, which has its own
    credentials. The Authenticator, in turn, is linked to a user -- sort of like a Service Principle.
    In the Authenticator setup, you will also configure role, and Token expiry. '''
parser.add_argument("-a", "--authenticator", type=str, default="YourAuthenticatorName", help="Authenticator Name")
parser.add_argument("-p", "--password", type=str, default="YourAuthenticatorPassword", help="Authenticator Password")
parser.add_argument("-n", "--name", type=str, default="YourAuthenticatorBoundUserName", help="Authenticator Bound User Name")
parser.add_argument("-r", "--role", type=str, default="YourAuthenticatorRole", help="Authenticator Role")
parser.add_argument("-u", "--url", type=str, default=instance_graphql_endpoint, help="GraphQL URL")
args = parser.parse_args()


''' Forms and sends a GraphQL request (query or mutation) and returns the response
    Accepts: The JSON payload you want to send to GraphQL and post arguments established above
    Returns: The JSON payload returned from the Server '''
def perform_graphql_request(content, url=args.url, headers=None):
  r = requests.post(url, headers=headers, data={"query": content})
  r.raise_for_status()
  return r.json()
  #TODO Handle Errors!

''' Gets a JWT Token containing the Bearer string returned from the Platform, assuming authorization is granted.
    Accepts: The JSON payload you want to send to GraphQL
    Returns: The JSON payload returned from the Server '''
def get_bearer_token (auth=args.authenticator, password=args.password, name=args.name, url=args.url, role=args.role):
  response = perform_graphql_request(f"""
    mutation authRequest {{
      authenticationRequest(
        input: {{authenticator: "{auth}", role: "{role}", userName: "{name}"}}
      ) {{
        jwtRequest {{
          challenge, message
        }}
      }}
    }}
  """) 
  jwt_request = response['data']['authenticationRequest']['jwtRequest']
  if jwt_request['challenge'] is None:
      raise requests.exceptions.HTTPError(jwt_request['message'])
  else:
      print("Challenge received: " + jwt_request['challenge'])
      response=perform_graphql_request(f"""
        mutation authValidation {{
          authenticationValidation(
            input: {{authenticator: "{auth}", signedChallenge: "{jwt_request["challenge"]}|{password}"}}
            ) {{
            jwtClaim
          }}
        }}
    """)
  jwt_claim = response['data']['authenticationValidation']['jwtClaim']
  return f"Bearer {jwt_claim}"
  #TODO Handle Errors!

# Main Program
def main():
  print("Requesting Data from CESMII Smart Manufacturing Platform...")
  print()

  ''' Request some data -- this is an equipment query.
        Use Graphiql on your instance to experiment with additional queries
        Or find additional samples at https://github.com/cesmii/API/wiki/GraphQL-Queries '''
  smp_query = """
    {
      equipments {
        id
        displayName
      }
    }"""
  smp_response = ""

  try:
    #Try to request data with the current bearer token
    current_bearer_token = "Value from Instance Portal -- You must include the prefix Bearer followed by a space"
    smp_response = perform_graphql_request(smp_query, headers={"Authorization": current_bearer_token})
  except requests.exceptions.HTTPError as e:
    if "forbidden" in str(e).lower() or "unauthorized" in str(e).lower():
      print("Bearer Token expired!")
      print("Attempting to retreive a new GraphQL Bearer Token...")
      print()

      #Authenticate
      current_bearer_token = get_bearer_token()

      print("New Token received: " + current_bearer_token)
      print()

      #Re-try our data request, using the updated bearer token
      # TODO: This is a short-cut -- if this subsequent request fails, we'll crash. You should do a better job :-)
      smp_response = perform_graphql_request(smp_query, headers={"Authorization": current_bearer_token})
    else:
      print("An error occured accessing the SM Platform!")
      print(e)
      exit(-1)
    
  print("Response from SM Platform was...")
  print(json.dumps(smp_response, indent=2))
  print()
  exit(0)

if __name__=="__main__": #Dont run main if imported...
    main()
