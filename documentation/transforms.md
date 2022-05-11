# Format of transform
This is an entry point for writing CMD transforms to be used by the [opendata-transformer-lambda](https://github.com/ONS-OpenData/dp-opendata-upload/tree/main/opendata-transformer-lambda) for the AWS pipeline. This is all still open to change but for now this is how it will be.

**Location**

All transforms will be stored in the [cmd-transforms](https://github.com/ONS-OpenData/cmd-transforms) repo of the `ONS-OpenData` github in a folder named after the dataset. Each folder will contain a `main.py` file and possibly a `requirements.txt` file.

**main.py**

The main.py file is essentially the transform for the specified dataset. It is picked up by the `opendata-transform-retriever` and ran by the `opendata-transformer-lambda`.
This file contains a fuction called `transform()` and will also contain any number of further functions that are specific to the transform.
The `transform()` function takes in one argument, `files`, which is a list containing the source data file(s). The v4 is outputted to the `/tmp/` directory, which is how you are able to write files using the lambdas. The transform always returns to output file path.

**transform() example**

```python
import pandas, glob
import databaker # if needed

def transform(files):
  # input file is an xlsx
  # some assertion
  assert len(files) == 1
  source_file = source_files[0]
  
  '''do some databaking and post processing to get v4'''
  
  output_file = '/tmp/v4-{dataset_id}.csv'
  # write v4
  return output_file

def some_function(value):
  # will do some post processing on the data
  new_value = value.strip() # example
  return new_value



```

**requirements.txt**

This is a text file that supports the transform. It contains a list of any further python files that are needed by the transform that are not included in `main.py`. These are files that are used by multiple transforms so have been centralised, and example would be `sparsity-functions`. These files are kept in [modules](https://github.com/ONS-OpenData/cmd-transforms/tree/master/modules). Each folder is a different file that can be named within `requirements.txt` and each folder contains a `module.py` file.

When a `requirements.txt` is specified within a transform folder, the `opendata-transformer-lambda` knows to also pick up the specified modules, so that it can also be used.





