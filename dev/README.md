
Simple helper for triggering individual lambdas **once deployed**.

### Setup

* `brew install jq`
* `chmod +x ./invoke.sh`


### Payloads

Precanned payloads need to go in `./dev/payloads`. You'll need to create the `payloads` directory yourself locally - I've git ignored it so we don't have to worry about accidently commiting sensitive information to github.

**NOTE** - when adding new payloads the name of the json file you put in `./dev/payloads` must **match the name of the lambda**. If you need to do something more complicated than that, just fish the command out of `./dev/invoke.sh`


### Usage

* `cd dev`
* `./invoke.sh <NAME OF LAMBDA>`

example: 

* `cd dev`
* `./invoke.sh opendata-source-extractor-lambda`

Press q to close down the initial summary, then jq will give you a nice readable summary of the response json.
