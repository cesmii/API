using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Azure.WebJobs;
using Microsoft.Azure.WebJobs.Extensions.Http;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.Logging;
using System.Configuration;

namespace CesmiiGraphQLAzureFunctionDemos
{
    public static class AzureFunctionForceMembraneIssue
    {
        //TODO: We could generate this from an object we manipulate from arguments then serialize to JSON
        public static string forceMutateQuery = "{\"query\":\"mutation CauseMembraneIssue {\\n  __typename\\n  replaceTimeSeriesRange(\\n    input: {\\n      entries: [\\n        {value: \\\"1\\\", timestamp: \\\"UTCStart\\\", status: \\\"0\\\"},\\n        {value: \\\"1\\\", timestamp: \\\"UTCEnd\\\", status: \\\"0\\\"}\\n      ],\\n       tagId: \\\"1798\\\"\\n    }) {\\n    string\\n  }\\n}\",\"variables\":null,\"operationName\":\"CauseMembraneIssue\"}";

        [FunctionName("ForceMembraneIssue")]
        public static async Task<IActionResult> Run(
            [HttpTrigger(AuthorizationLevel.Function, "get", "post", Route = null)] HttpRequest req,
            ILogger log)
        {
            log.LogInformation("C# HTTP trigger function processed a request to ForceMembraneIssue.");
            CommonGraphQLFunctions myGQL = new CommonGraphQLFunctions(log);
            string result = myGQL.PostGraphQLQuery(myGQL.InjectUTCDateTime(forceMutateQuery));
            return (ActionResult)new OkObjectResult(result);
        }
    }
}
