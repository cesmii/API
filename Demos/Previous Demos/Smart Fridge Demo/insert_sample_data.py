import common_graphql_functions

tag_to_update = "1848"
sample_value = 9

query_string = '''
  mutation InsertSampleData {
    replaceTimeSeriesRange(
      input: {
        entries: [
          {value: "''' + str(sample_value) + '''", timestamp: "UTCStart", status: "0"}
        ],
        tagId: "''' + tag_to_update + '''"
      }) {
      string
    }
  }
  '''

result = common_graphql_functions.post_graphql_query(query_string)