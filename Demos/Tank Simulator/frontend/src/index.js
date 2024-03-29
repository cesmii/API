import React from "react";
import ReactDOM from "react-dom";
import { BrowserRouter, Route, Switch, Redirect } from "react-router-dom";
import { ApolloProvider, ApolloClient, createHttpLink, InMemoryCache } from "@apollo/client";
import { setContext } from "@apollo/client/link/context";

import "@fortawesome/fontawesome-free/css/all.min.css";
import "assets/styles/tailwind.css";

// layouts

import Admin from "layouts/Admin.js";

// views without layouts

import Index from "views/Index.js";

const instanceGraphQLEndpoint = "YOUR INSTANCE ENDPOINT";
/* You could opt to manually update the bearer token that you retreive from the Developer menu > GraphQL - Request Header token
But be aware this is short-lived (you set the expiry, see Authenticator comments below) and you will need to handle
expiry and renewal -- as shown below. As an alternative, you could start your life-cycle with authentication, or
you could authenticate with each request (assuming bandwidth and latency aren't factors in your use-case). */
var currentBearerToken = "BEAR TOKEN AT YOUR PLATFORM"
/* These values come from your Authenticator, which you configure in the Developer menu > GraphQL Authenticator
    Rather than binding this connectivity directly to a user, we bind it to an Authenticator, which has its own
    credentials. The Authenticator, in turn, is linked to a user -- sort of like a Service Principle.
    In the Authenticator setup, you will also configure role, and Token expiry. */
const clientId = "CLIENTID";
const clientSecret = "CLIENTSECRET";
const userName = "USERNAME";
const role = "ROLE SHOWN ON AUTHENTICATOR IN PLATFORM";
const equipment_type_id = "YOUR EQUIPMENT TYPE ID"

console.log("before http");
const httpLink = createHttpLink({
  uri: instanceGraphQLEndpoint,
});
console.log("before auth");

const tempvar = 99999;
var tank_volumesID = [];
var tank_sizes = [];
const tank_names = [];
const tank_info = [];
const tank_flowrateID = [];
const tank_temperatureID = [];
const tank_serialNumber = [];
var tank_colors = [];
let one_tank_info = [];


const authLink = setContext((_, { headers }) => {
  // get the authentication token from local storage if it exists
  const token = localStorage.getItem("token");
  // return the headers to the context so httpLink can read them
  return {
    headers: {
      ...headers,
      authorization: token ? `Bearer ${token}` : "",
    },
  };
});
console.log("after auth");
const client = new ApolloClient({
  link: authLink.concat(httpLink),
  cache: new InMemoryCache(),
});
console.log("after client");

/* Dependenices to install via npm
 - node-fetch
 Tested with Node.JS 12.6.3
*/
const fetch = require("node-fetch");



//Call main program function
doMain();

//Forms and sends a GraphQL request (query or mutation) and returns the response
async function performGraphQLRequest(query, endPoint, bearerToken) {
  let opt = {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: query,
  };
  if (bearerToken && bearerToken != "") opt.headers.Authorization = bearerToken;
  const response = await fetch(endPoint, opt);
  return await response.json();

  //TODO: Handle errors!
}

//Gets a JWT Token containing the Bearer string returned from the Platform, assuming authorization is granted.
async function getBearerToken() {
  // Step 1: Request a challenge
  const authResponse = await performGraphQLRequest(
    JSON.stringify({
      query:
        ' mutation {\
            authenticationRequest(input: \
              {authenticator:"' +
        clientId +
        '", \
              role: "' +
        role +
        '", \
              userName: "' +
        userName +
        '"})\
             { jwtRequest { challenge, message } } }',
    }),
    instanceGraphQLEndpoint
  );
  const challenge = authResponse.data.authenticationRequest.jwtRequest.challenge;
  console.log("Challenge received: " + challenge);

  // Step 2: Get token
  const challengeResponse = await performGraphQLRequest(
    JSON.stringify({
      query:
        ' mutation {\
            authenticationValidation(input: \
              {authenticator:"' +
        clientId +
        '", \
              signedChallenge: "' +
        challenge +
        "|" +
        clientSecret +
        '"})\
             { jwtClaim } }',
    }),
    instanceGraphQLEndpoint
  );

  const newJwtToken = challengeResponse.data.authenticationValidation.jwtClaim;

  // Set localstorage for Apollo
  localStorage.setItem("token", newJwtToken);

  // TODO: Remove local storage token after logging out of the app

  return newJwtToken;

  //TODO: Handle errors!
}

//Main Program Function
var smpResponse = ""


async function doMain() {
  console.log("Requesting Data from CESMII Smart Manufacturing Platform...");
  console.log();

  /* Request some data -- this is an equipment query.
        Use Graphiql on your instance to experiment with additional queries
        Or find additional samples at https://github.com/cesmii/API/wiki/GraphQL-Queries */
    let today = new Date().toISOString().slice(0, 10)
    today +=  "T00:00:00+00:00"
    console.log(today)
    let new_day = new Date()
    var tomorrow = new Date(new_day)
    tomorrow.setDate(tomorrow.getDate() + 1)
    tomorrow = tomorrow.toISOString().slice(0, 10) + "T00:00:00+00:00"
    console.log("tomorrow", tomorrow)
    const smpQuery = JSON.stringify({
    query: `{
          equipments( filter:{typeId: {equalTo: "${equipment_type_id}"}}
            ) {
              displayName
              id
            attributes{
              displayName
              id
              getTimeSeries(
                startTime: "${today}"
                endTime: "${tomorrow}"
                maxSamples: 1
              ) {
                floatvalue
                stringvalue
                ts
              }
            }
          }
        }`,
  });

  let smpResponse = await performGraphQLRequest(
    smpQuery,
    instanceGraphQLEndpoint,
    currentBearerToken
  );

  if (JSON.stringify(smpResponse).indexOf("expired") != -1 || JSON.stringify(smpResponse).indexOf("malformed") != -1) {
    console.log("Bearer Token expired!");
    console.log("Attempting to retreive a new GraphQL Bearer Token...");
    console.log();

    //Authenticate
    const newTokenResponse = await getBearerToken(instanceGraphQLEndpoint);
    currentBearerToken = "Bearer " + newTokenResponse;

    console.log("New Token received: " + JSON.stringify(newTokenResponse));
    console.log();

    //Re-try our data request, using the updated bearer token
    //  TODO: This is a short-cut -- if this subsequent request fails, we'll crash. You should do a better job :-)
    smpResponse = await performGraphQLRequest(
      smpQuery,
      instanceGraphQLEndpoint,
      currentBearerToken
    );
  }

  console.log("Response from SM Platform was... ", smpResponse.data);
  for (let ele of smpResponse.data.equipments){
    console.log(ele);
    const attributes = ele.attributes;
    let temp = {"name": ele.displayName};
    let one = false;
    for (let attribute of attributes){
      if(attribute.displayName=="size") temp["size"] = attribute.getTimeSeries[0].floatvalue;
      else if(attribute.displayName=="volume") temp["volumeID"] = attribute.id;
      else if(attribute.displayName=="flowrate") temp["flowrateID"] = attribute.id;
      else if(attribute.displayName=="temperature") temp["temperatureID"] = attribute.id;
      else if(attribute.displayName=="serialNumber") temp["serialNumber"] = attribute.getTimeSeries[0].stringvalue;
    }
    tank_info.push(temp);
    
    }

  tank_info.sort(function(a, b){
    let x = a.name;
    let y = b.name;
    if (x < y) {return -1;}
    if (x > y) {return 1;}
    return (x<y);
  });

  for (let tank of tank_info){
    tank_names.push(tank.name);
    tank_sizes.push(tank.size);
    tank_volumesID.push(tank.volumeID);
    tank_flowrateID.push(tank.flowrateID);
    tank_temperatureID.push(tank.temperatureID);
    tank_serialNumber.push(tank.serialNumber);

  }
  //tank_sizes = [20, 20, 10, 10, 20]
  one_tank_info = [tank_volumesID[0], tank_flowrateID[0], tank_temperatureID[0]]
  var tank_amount = tank_volumesID.length;
  console.log(one_tank_info);
  console.log(tank_info);
  //console.log(JSON.stringify(smpResponse, null, 2));
  console.log(tank_names);
  console.log(tank_sizes);
  console.log(tank_volumesID);
  console.log(tank_flowrateID);
  console.log(tank_temperatureID);
  console.log(tank_serialNumber);
  console.log("colors",tank_colors);
}

ReactDOM.render(
  <ApolloProvider client={client}>
    <BrowserRouter>
      <Switch>
        {/* add routes with layouts */}
        <Route path="/admin" component={Admin} />
        {/* add routes without layouts */}
        <Route path="/" exact component={Index} />
        {/* add redirect for first page */}
        <Redirect from="*" to="/" />
      </Switch>
    </BrowserRouter>
  </ApolloProvider>,
  document.getElementById("root")
);

export {instanceGraphQLEndpoint, currentBearerToken, clientId, clientSecret, userName, role, tempvar, tank_names, tank_sizes, tank_volumesID, tank_flowrateID, tank_temperatureID, tank_serialNumber, one_tank_info, tank_colors, doMain} ;

