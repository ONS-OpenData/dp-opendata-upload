Feature: Upload metadata parser
  As a developer, I want the upload metadata parser lambda to:

  * Get metadata from the source bucket
  * Get the metadata handler from the source bucket
  * Parse the metadata using the handler
  * Return the metadata

  Scenario: Invalid starting event
    Given the lambda "opendata-v4-upload-metadata-parser"
    And we specify the event fixture "invalid-event"
    And we envoke the lambda
    Then a log line should contain
    | level  | text                                                 |
    | ERROR  | ValidationError: 'bucket' is a required property     |

  Scenario: Successfully Complete
    Given the lambda "opendata-v4-upload-metadata-parser"
    And we specify the event fixture "valid"
    And we envoke the lambda
    Then a log line should contain
      | level    | text                            |
      | WARNING  | lambda completed operation      |
    And the response returned should match
      """
      {"statusCode": 200, "body": "{\"metadata\": {}, \"dimension_data\": {}, \"usage_notes\": {}}"}
      """