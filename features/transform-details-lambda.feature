Feature: Transform details lambda
  As a developer, I want the transform details lambda to:

  * Use the dataset name to get details about a pipeline.
  * Trigger opendata-metadata-validator
  * If valid, return details to calling service

  Scenario: Successfully Complete
    Given the lambda "opendata-transform-details-lambda"
    And we specify the event fixture "valid"
    And we invoke the lambda
    Then a log line should contain
      | level    | text                            |
      | WARNING  | lambda completed operation      |

  Scenario: Receive a 500 response from the metadata validator lambda
    Given the lambda "opendata-transform-details-lambda"
    And we specify the event fixture "failed_response_metadata_validator"
    And we invoke the lambda
    Then a log line should contain
      | level    | text                                                                                     |
      | ERROR    | Exception: Failed to get response from opendata-metadata-validator, with status code 500 |
      | WARNING  | lambda failed to complete operation                                                      |