import argparse
import requests
import json

class graphql:

    def __init__(self, authenticator, password, username, role, endpoint):
        self.current_bearer_token = ""
        self.parser = None
        self.args = None

        self.parser = argparse.ArgumentParser()
        self.parser.add_argument("-a", "--authenticator", type=str, default=authenticator)
        self.parser.add_argument("-p", "--password", type=str, default=password)
        self.parser.add_argument("-n", "--name", type=str, default=username)
        self.parser.add_argument("-r", "--role", type=str, default=role)
        self.parser.add_argument("-u", "--url", type=str, default=endpoint)
        self.args = self.parser.parse_args()

    def post(self, content):
        if self.current_bearer_token == "":
            self.current_bearer_token = self.get_bearer_token()
        try:
            response = self.perform_graphql_request(content)
        except requests.exceptions.HTTPError as e:
            if "forbidden" in str(e).lower() or "unauthorized" in str(e).lower():
                print ("Not authorized, getting new token...")
                self.current_bearer_token = self.get_bearer_token()
                response = self.perform_graphql_request(content)
            else:
                print("An unhandled error occured accessing the SM Platform!")
                print(e)
                raise requests.exceptions.HTTPError(e)
        return response

    def perform_graphql_request(self, content, auth=False):
        print("Performing request with content: ")
        print(content)
        print()
        if auth == True:
            header=None
        else:
            header={"Authorization": self.current_bearer_token}
        r = requests.post(self.args.url, headers=header, data={"query": content})
        r.raise_for_status()
        return r.json()
        
    def get_bearer_token (self):
        response = self.perform_graphql_request(f"""
        mutation authRequest {{
                authenticationRequest(
                    input: {{authenticator: "{self.args.authenticator}", role: "{self.args.role}", userName: "{self.args.name}"}}
                ) {{
                    jwtRequest {{
                    challenge, message
                    }}
                }}
                }}
            """, True) 
        jwt_request = response['data']['authenticationRequest']['jwtRequest']
        print ("got auth request response")
        if jwt_request['challenge'] is None:
            print ("no challenge in response")
            raise requests.exceptions.HTTPError(jwt_request['message'])
        else:
            print("Challenge received: " + jwt_request['challenge'])
            response=self.perform_graphql_request(f"""
                mutation authValidation {{
                authenticationValidation(
                    input: {{authenticator: "{self.args.authenticator}", signedChallenge: "{jwt_request["challenge"]}|{self.args.password}"}}
                    ) {{
                    jwtClaim
                }}
                }}
            """, True)
        jwt_claim = response['data']['authenticationValidation']['jwtClaim']
        return f"Bearer {jwt_claim}"
