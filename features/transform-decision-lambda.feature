Feature: Transform decision lambda
  As a developer, I want the transform decison lambda to:

  * Be triggered by a notification with bucket url in it.
  * Validate the triggering message.
  * Call `opendata-transform-decision-lambda` for dataset details.
  * Make a decision based on those details 

  Scenario: Receive a message with no bucket name
    Given the lambda "opendata-transform-decision-lambda"
    And we specify the message "message_no_bucket_name"
    And we envoke the lambda
    Then a log line should contain
      | level    | text                                            |
      | ERROR    | ValidationError: 'name' is a required property  |
      | WARNING  | lambda failed to complete operation         |

  Scenario: Receive a message with no object key
    Given the lambda "opendata-transform-decision-lambda"
    And we specify the message "message_no_object_key"
    And we envoke the lambda
    Then a log line should contain
      | level    | text                                            |
      | ERROR    | ValidationError: 'key' is a required property   |
      | WARNING  | lambda failed to complete operation         |

  Scenario: Receive a 500 response from the details lambda
    Given the lambda "opendata-transform-decision-lambda"
    And we specify the message "message_failed_response_details_lambda"
    And we envoke the lambda
    Then a log line should contain
      | level    | text                                                                                             |
      | ERROR    | Exception: Failed to get response from opendata-transform-details-lambda, with status code 500   |
      | WARNING  | lambda failed to complete operation         |

  Scenario: Successfully Complete
    Given the lambda "opendata-transform-decision-lambda"
    And we specify the message "message_valid"
    And we envoke the lambda
    Then a log line should contain
      | level    | text                            |
      | WARNING  | lambda completed operation      |
