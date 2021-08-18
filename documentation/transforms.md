# Format of transform
This is an entry point for writing CMD transforms to be used by the `opendata-transform-lambda` for the AWS pipeline. This is all still open to change but for now this is how it will be.

**Location**

All transforms will be stored in the `cmd-transforms` repo of the `ONS-OpenData` github in a folder named after the dataset. Each folder will contain a `main.py` file

**Transform**

The `main.py` file will consist of functions where the main function (the transform) will be called `transform` and will take in one argument. This argument will be `location` which refers to the path where the source data files are. The `opendata-transform-lambda` will pick up a zip file from a s3 bucket and then extract these files into `/tmp/` so this location may become hard coded as this but for now it will be left changable.

The transform function will then need to find the required source file(s) from the extracted files, which will require some 'rule' where it looks for only 'xlsx' files of csv files with a certain name. Within the extracted files there will be a `manifest.json` file and a metadata file which aren't needed for the transform.

Then the actual transforming of the data will take place if using databaker. Then the 'post proccessing' bits. The file will then be outputted in the same location as all of the other files. The output file name will use the format `v4-{dataset_id}.csv` and then finally "SparsityFiller" will be run if required.

The function is not called within `main.py` but will be called from `opendata-transform-lambda` - is this the correct way to do this??

**Example**

```python
import pandas, glob
import databaker # if needed

def transfrom(location):
  # input file is an xlsx
  source_files = glob.glob(location + '*.xlsx')
  source_file = source_files[0]
  
  '''do some databaking and post processing to get v4'''
  
  output_file = location + 'v4-{dataset_id}.csv'
  # write v4
