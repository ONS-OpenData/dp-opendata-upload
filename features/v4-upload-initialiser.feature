Feature: V4 Upload Initialiser
  As a developer, I want the upload initialiser to:

  * Be tiggered by the arrival of a v4 in the bucket.
  * Do nothing where the v4 object doesnt have a metadata source attribute.
  * Acquire the upload metdata using the source attribute.
  * Use the cmd apis to upload the observation data.
  * Call the polling service, passing along the upload metadata.

  Scenario: Receive a message with no bucket name
    Given the lambda "opendata-v4-upload-initialiser"
    And we specify the event fixture "no_bucket_name"
    And set the environment varibles
      | key               |  value                                | 
      | ZEBEDEE_EMAIL     |  fake@doesntmatter.com                |
      | ZEBEDEE_PASSWORD  |  password                             |
      | ZEBEDEE_URL       |  http://not.actually.zebedee          |
      | RECIPE_API_URL    |  http://not.recipe.api                |
      | DATASET_API_URL   |  http://not.dataset.api               |
      | S3_V4_BUCKET_URL  |  https://s3-fake.amazonaws.com/bucket |
    And we envoke the lambda
    Then a log line should contain
      | level    | text                                            |
      | ERROR    | ValidationError: 'name' is a required property  |
      | WARNING  | lambda failed to complete operation             |

  Scenario: Receive a message with no bucket name
    Given the lambda "opendata-v4-upload-initialiser"
    And we specify the event fixture "not_automated"
    And set the environment varibles
      | key               |  value                                | 
      | ZEBEDEE_EMAIL     |  fake@doesntmatter.com                |
      | ZEBEDEE_PASSWORD  |  password                             |
      | ZEBEDEE_URL       |  http://not.actually.zebedee          |
      | RECIPE_API_URL    |  http://not.recipe.api                |
      | DATASET_API_URL   |  http://not.dataset.api               |
      | S3_V4_BUCKET_URL  |  https://s3-fake.amazonaws.com/bucket |
    And we envoke the lambda
    Then no warning or error logs should occur

  Scenario: Successfully Initialise An Upload
    Given the lambda "opendata-v4-upload-initialiser"
    And we specify the event fixture "valid"
    And set the environment varibles
      | key               |  value                                | 
      | ZEBEDEE_EMAIL     |  fake@doesntmatter.com                |
      | ZEBEDEE_PASSWORD  |  password                             |
      | ZEBEDEE_URL       |  http://not.actually.zebedee          |
      | RECIPE_API_URL    |  http://not.recipe.api                |
      | DATASET_API_URL   |  http://not.dataset.api               |
      | S3_V4_BUCKET_URL  |  https://s3-fake.amazonaws.com/bucket |
    And we envoke the lambda
    Then a log line should contain
      | level    | text                            |
      | WARNING  | lambda completed operation      |

