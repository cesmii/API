using System;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Azure.WebJobs;
using Microsoft.Azure.WebJobs.Extensions.Http;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.Logging;
using System.Configuration;
using System.Threading;

namespace CesmiiGraphQLAzureFunctionDemos
{
    public static class AzureFunctionInsertSampleData
    {
        //Load relevant config
        public static int sampleMins = 8;

        [FunctionName("InsertSampleData")]
        public static async Task<IActionResult> Run(
            [HttpTrigger(AuthorizationLevel.Function, "get", "post", Route = null)] HttpRequest req,
            ILogger log)
        {
            log.LogInformation("C# HTTP trigger function processed a request to InsertSampleData.");

            Random r = new Random();
            int loopCount = 1;

            for (int i=0;i<=sampleMins; i++)
            {
                if (i < sampleMins)
                {
                    doSampleInsert(generateSampleDataQuery(472, r.Next(6, 9)), log, (sampleMins - loopCount));    //Backflush Flow
                    doSampleInsert(generateSampleDataQuery(508, r.Next(4, 12)), log, (sampleMins - loopCount));    //Outlet Flow
                    doSampleInsert(generateSampleDataQuery(1286, r.Next(4, 17)), log, (sampleMins - loopCount));    //Inlet Flow
                    doSampleInsert(generateSampleDataQuery(685, r.Next(0, 5)), log, (sampleMins - loopCount));    //Reject Flow
                }
                else
                {
                    doSampleInsert(generateSampleDataQuery(472, 0), log, 0);   //Backflush Flow
                    doSampleInsert(generateSampleDataQuery(508, 0), log, 0);    //Outlet Flow
                    doSampleInsert(generateSampleDataQuery(1286, 0), log, 0);    //Inlet Flow
                    doSampleInsert(generateSampleDataQuery(685, 0), log, 0);    //Reject Flow
                }
                loopCount++;
            }

            string result = "OK. Inserted " + sampleMins.ToString() + " minutes of sample values.";
            return (ActionResult)new OkObjectResult(result);
        }

        private static void doSampleInsert(string insertMutateQuery, ILogger log, int offsetMinutes)
        {
            CommonGraphQLFunctions myGQL = new CommonGraphQLFunctions(log);
            string result = myGQL.PostGraphQLQuery(myGQL.InjectUTCDateTime(insertMutateQuery, offsetMinutes));
            log.LogInformation(result);
        }

        private static string generateSampleDataQuery(int tagId, int value)
        {
            string query = "{\"query\":\"mutation InsertSampleData {\\n  __typename\\n  replaceTimeSeriesRange(\\n    input: {\\n      entries: [\\n        {value: \\\"" + value.ToString() + "\\\", timestamp: \\\"UTCStart\\\", status: \\\"0\\\"},\\n        {value: \\\"" + value.ToString() + "\\\", timestamp: \\\"UTCEnd\\\", status: \\\"0\\\"}\\n      ],\\n       tagId: \\\""+ tagId +"\\\"\\n    }) {\\n    string\\n  }\\n}\",\"variables\":null,\"operationName\":\"InsertSampleData\"}";
            return query;
        }
    }
}
