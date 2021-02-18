using System;
using System.Collections.Generic;
using System.Text;
using Newtonsoft.Json;
using System.Net;
using System.Security.Cryptography.X509Certificates;
using System.Net.Security;
using RestSharp;
using Microsoft.Extensions.Logging;

namespace CesmiiGraphQLAzureFunctionDemos
{
    public class CommonGraphQLFunctions
    {
        #region Environment-specific logging abstraction
        /// <summary>
        /// Most of this demo code can work as an Azure Function, .NET Console App or Savigent Workflow
        /// but since each of those environments has a different approach to logging, we'll abstract it out
        /// Update the code in this region to support your desired execution environment.
        /// </summary>
        static ILogger _log;
        public static void LogToEnvironmentDebug(string message)
        {
            _log.LogInformation(message);
        }
        #endregion

        // The end point of your platform instance. Can also be passed into the constructor.
        string _endPointURI = "http://yourplatforminstance.com/graphql";

        public CommonGraphQLFunctions(ILogger log)
        {
            _log = log;
        }

        public CommonGraphQLFunctions(ILogger log, string endPointURI)
        {
            if (endPointURI != "")
                _endPointURI = endPointURI;
            _log = log;
        }

        #region Portable Common Methods
        /// <summary>
        /// These common GraphQL methods can be used in an Azure Function, .NET Console App, or Savigent Workflow
        /// </summary>

        public string PostGraphQLQuery(string gqlQuery)
        {
            var client = new RestClient(_endPointURI);
            client.Timeout = -1;
            var request = new RestRequest(Method.POST);
            request.AddHeader("Content-Type", "application/json");
            request.AddParameter("application/json", gqlQuery, ParameterType.RequestBody);
            IRestResponse response = client.Execute(request);
            LogToEnvironmentDebug(response.Content);
            return response.Content;
        }

        //Replace datetime placeholders with calculated datetimes
        public string InjectUTCDateTime(string gqlQuery)
        {
            DateTime endTime = DateTime.Now;
            DateTime startTime = endTime.AddMinutes(-1);
            return InjectUTCDateTime(gqlQuery, startTime, endTime);
        }

        public string InjectUTCDateTime(string gqlQuery, int offsetMinutes)
        {
            DateTime endTime = DateTime.Now;
            if (offsetMinutes > 0)
                offsetMinutes = offsetMinutes * -1;
            endTime = endTime.AddMinutes(offsetMinutes);
            DateTime startTime = endTime.AddMinutes(-1);
            return InjectUTCDateTime(gqlQuery, startTime, endTime);
        }
        public string InjectUTCDateTime(string gqlQuery, DateTime startTime, DateTime endTime)
        {
            string offSet = TimeZone.CurrentTimeZone.GetUtcOffset(DateTime.Now).ToString();
            if (offSet == "00:00:00")
                offSet = "";
            //ThinkIQ time series queries take a time range
            string utcStartDateTime = startTime.ToString("yyyy'-'MM'-'dd'T'HH':'mm':'ss") + offSet;
            string utcEndDateTime = endTime.ToString("yyyy'-'MM'-'dd'T'HH':'mm':'ss") + offSet;
            gqlQuery = gqlQuery.Replace("UTCStart", utcStartDateTime).Replace("UTCEnd", utcEndDateTime);
            return gqlQuery;
        }

        //For demo purposes we'll allow any kind of cert -- even self-signed.
        //TODO: For production use, we should tighten this up.
        public bool ValidateCertificate(object sender, X509Certificate certificate, X509Chain chain, SslPolicyErrors policyErrors)
        {
            return true;
        }

        #endregion
    }
}
