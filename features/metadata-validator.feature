Feature: Metadata validator lambda
  As a developer, I want the metadata validator lambda to:

  * Trigger opendata-v4-upload-metadata-parser
  * Validate the response
  * Return a payload of valid is True/False

  Scenario: Invalid starting event
    Given the lambda "opendata-metadata-validator"
    And we specify the event fixture "invalid-event"
    And we invoke the lambda
    Then a log line should contain
    | level  | text                                                 |
    | ERROR  | ValidationError: 'bucket' is a required property     |

  Scenario: Receive a 500 response from the metadata parser lambda
    Given the lambda "opendata-metadata-validator"
    And we specify the event fixture "failed_response_metadata_parser"
    And we invoke the lambda
    Then a log line should contain
      | level    | text                                                                                        |
      | ERROR    | Exception: Failed to get response from opendata-v4-metadata-parser, with status code 500    |
      | WARNING  | lambda failed to complete operation                                                         |  

  Scenario: Receive invalid format for metadata 
    Given the lambda "opendata-metadata-validator"
    And we specify the event fixture "invalid_metadata"
    And we invoke the lambda
    Then a log line should contain
      | level    | text                                                        |
      | ERROR    | ValidationError: 'dimension_data' is a required property    |

                          