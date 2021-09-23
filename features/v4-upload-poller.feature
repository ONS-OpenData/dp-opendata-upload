Feature: Upload poller
  As a developer, I want the poller to tell me when the observations
  have all been uploaded.

  Scenario: Receive a bad starting event
    Given the lambda "opendata-v4-upload-poller"
    And we specify the event fixture "bad-starting-event"
    And set the environment varibles
      | key                     |  value                     | 
      | ZEBEDEE_ACCESS_TOKEN    |  xxxx                      |
      | DATASET_API_URL         |  http://im-the-dataset-api |
    And we invoke the lambda
    Then a log line should contain
      | level    | text                                                   |
      | ERROR    | ValidationError: 'instance_id' is a required property  |
      | WARNING  | lambda failed to complete operation                    |

  Scenario: Env vars are not set
    Given the lambda "opendata-v4-upload-poller"
    And we specify the event fixture "valid"
    And set the environment varibles
      | key                     |  value                     | 
      | MAXIMUM_POLLING_TIME    |  5                         |
      | ZEBEDEE_ACCESS_TOKEN    |  xxxx                      |
      | DATASET_API_URL         |  http://im-the-dataset-api |
    And we invoke the lambda
    Then a log line should contain
      | level    | text                                                 |
      | ERROR    | Lambda cannot run with env var DELAY_BETWEEN_CHECKS  |
      | WARNING  | lambda failed to complete operation                  |

  Scenario: Poller completes one iteration successfully
    Given the lambda "opendata-v4-upload-poller"
    And we specify the event fixture "valid"
    And set the environment varibles
      | key                     |  value                     | 
      | MAXIMUM_POLLING_TIME    |  5                         |
      | DELAY_BETWEEN_CHECKS    |  1                         |
      | ZEBEDEE_ACCESS_TOKEN    |  xxxx                      |
      | DATASET_API_URL         |  http://im-the-dataset-api |
    And we invoke the lambda
    Then a log line should contain
      | level    | text                            |
      | WARNING  | lambda completed operation      |
    And the lambda was invoked "1" times

  Scenario: Poller completes multiple iterations successfully
    Given the lambda "opendata-v4-upload-poller"
    And we specify the event fixture "valid-longer-polling"
    And set the environment varibles
      | key                     |  value                     | 
      | MAXIMUM_POLLING_TIME    |  5                         |
      | DELAY_BETWEEN_CHECKS    |  2                         |
      | ZEBEDEE_ACCESS_TOKEN    |  xxxx                      |
      | DATASET_API_URL         |  http://im-the-dataset-api |
    And we invoke the lambda
    And we reinvoke the lambda
    And we reinvoke the lambda
    Then the lambda was invoked "3" times
    And a log line should contain
      | level    | text                            |
      | WARNING  | lambda completed operation      |
    And the logs should contain "2" instances of message containing "New poller invoked"
