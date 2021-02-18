using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Azure.WebJobs;
using Microsoft.Azure.WebJobs.Extensions.Http;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.Logging;
using System.Configuration;

namespace CesmiiGraphQLAzureFunctionDemos
{
    public static class AzureFunctionCancelMembraneIssue
    {
        //TODO: We could generate this from an object we manipulate from arguments then serialize to JSON
        public static string cancelMutateQuery = "{\"query\":\"mutation CancelMembraneIssue {\\n  __typename\\n  replaceTimeSeriesRange(\\n    input: {\\n      entries: [\\n        {value: \\\"0\\\", timestamp: \\\"UTCStart\\\", status: \\\"0\\\"},\\n        {value: \\\"0\\\", timestamp: \\\"UTCEnd\\\", status: \\\"0\\\"}\\n      ],\\n       tagId: \\\"1798\\\"\\n    }) {\\n    string\\n  }\\n}\",\"variables\":null,\"operationName\":\"CancelMembraneIssue\"}";

        [FunctionName("CancelMembraneIssue")]
        public static async Task<IActionResult> Run(
            [HttpTrigger(AuthorizationLevel.Function, "get", "post", Route = null)] HttpRequest req,
            ILogger log)
        {
            log.LogInformation("C# HTTP trigger function processed a request to CancelMembraneIssue.");
            CommonGraphQLFunctions myGQL = new CommonGraphQLFunctions(log);
            string result = myGQL.PostGraphQLQuery(myGQL.InjectUTCDateTime(cancelMutateQuery));
            return (ActionResult)new OkObjectResult(result);
        }
    }
}
