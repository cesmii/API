using System;
using System.Collections.Generic;
using System.Text;
using Newtonsoft.Json;
using System.Net;
using System.Security.Cryptography.X509Certificates;
using System.Net.Security;
using RestSharp;
using Microsoft.Extensions.Logging;
using System.Configuration;

namespace CesmiiGraphQLAzureFunctionDemos
{
    public class WorkflowMethodsDemo
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
        public WorkflowMethodsDemo(ILogger log)
        {
            _log = log;
        }

        #region Portable Demo Methods
        /// <summary>
        /// These demo methods can be used in an Azure Function, .NET Console App, or Savigent Workflow
        /// </summary>

        //TODO: We could generate this from an object we manipulate from arguments then serialize to JSON
        const string attributeQuery = "{\"query\":\"query TSQuery {\\n getRawHistoryDataWithSampling(maxSamples: 3, ids: [\\\"1798\\\"], \\n    startTime: \\\"UTCStart\\\", \\n    endTime: \\\"UTCEnd\\\") {\\n    nodes {\\n      id\\n      status\\n      boolvalue\\n      dataType\\n      ts\\n    }\\n  }\\n}\\n\\nquery MyQuery2\\n{ \\n  attributes { \\n    nodes  { displayName, id, partOfId, tagId, boolValue }  }  \\n}\\n\",\"variables\":null,\"operationName\":\"TSQuery\"}";
        const string mutateQuery = "{\"query\":\"mutation cancelMembraneIssue {\\n  __typename\\n  replaceTimeSeriesRange(\\n    input: {\\n      entries: [\\n        {value: \\\"0\\\", timestamp: \\\"UTCStart\\\", status: \\\"0\\\"},\\n        {value: \\\"0\\\", timestamp: \\\"UTCEnd\\\", status: \\\"0\\\"}\\n      ],\\n       tagId: \\\"1798\\\"\\n    }) {\\n    string\\n  }\\n}\",\"variables\":null,\"operationName\":\"CauseMembraneIssue\"}";

        public bool CheckTIQForMembraneIssue()
        {
            CommonGraphQLFunctions myGQL = new CommonGraphQLFunctions(_log);
            ServicePointManager.SecurityProtocol = SecurityProtocolType.Ssl3 | SecurityProtocolType.Tls | SecurityProtocolType.Tls11 | SecurityProtocolType.Tls12;
            ServicePointManager.ServerCertificateValidationCallback += new RemoteCertificateValidationCallback(myGQL.ValidateCertificate);

            //Ask ThinkIQ for data about the RO Skid Side A membrane
            LogToEnvironmentDebug("Getting Membrane Data from ThinkIQ...");
            string result = myGQL.PostGraphQLQuery(myGQL.InjectUTCDateTime(attributeQuery));
            LogToEnvironmentDebug(result);

            //Evaluate the response to see if the membrane issue exists
            if (ParseOutMembraneIssue(result))
            {
                //If the membrane issue DOES exist, toggle it back off (so the Workflow doesn't run again next time) 
                // then return true so the Workflow will run
                LogToEnvironmentDebug("Canceling Membrane Issue in ThinkIQ...");
                myGQL.PostGraphQLQuery(myGQL.InjectUTCDateTime(mutateQuery));
                return true;
            }
            else
            {
                //If the membrane issue does NOT exist, we have nothing to do
                //	return false so the Workflow will not run
                return false;
            }
        }

        //Super crude JSON parser cause its faster than strongly typing the response
        public bool ParseOutMembraneIssue(string strJson)
        {
            bool retValue = false;
            string[] jsonParts = strJson.Split(new[] { "\"boolvalue\":" }, StringSplitOptions.None);
            string lastPart = jsonParts[jsonParts.Length - 1];
            if (lastPart.IndexOf("true") == 0)
                retValue = true;
            LogToEnvironmentDebug("Last JSON part was: " + lastPart);
            LogToEnvironmentDebug("Parsed value is: " + retValue.ToString());
            return retValue;
        }

        #endregion
    }
}
