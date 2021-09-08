Feature: V4 Upload Initialiser
  As a developer, I want the transform details lambda to:

  * Use the dataset name to get details about a pipeline.
  * Trigger opendata-metadata-validator
  * If valid, return details to calling service

  Scenario: Receive a message with no bucket name
    Given the lambda "opendata-v4-upload-initialiser"
    And we specify the message "message_no_bucket_name"
    And we envoke the lambda
    Then a log line should contain
      | level    | text                                            |
      | ERROR    | ValidationError: 'name' is a required property  |
      | WARNING  | lambda failed to complete operation             |

  Scenario: Receive a message with no bucket name
    Given the lambda "opendata-v4-upload-initialiser"
    And we specify the message "message_not_automated"
    And we envoke the lambda
    Then no warning or error logs should occur

  Scenario: Successfully Complete
    Given the lambda "opendata-v4-upload-initialiser"
    And we specify the message "message_valid"
    And we envoke the lambda
    Then a log line should contain
      | level    | text                            |
      | WARNING  | lambda completed operation      |

