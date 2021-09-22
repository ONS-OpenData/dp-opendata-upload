Feature: Upload poller
  As a developer, I want the poller to tell me when the observations
  have all been uploaded.

  #Scenario: Receive a message with no bucket name
  #  Given the lambda "opendata-transform-decision-lambda"
  #  And we specify the event fixture "no_bucket_name"
  #  And we envoke the lambda
  #  Then a log line should contain
  #    | level    | text                                            |
  #    | ERROR    | ValidationError: 'name' is a required property  |
  #    | WARNING  | lambda failed to complete operation             |