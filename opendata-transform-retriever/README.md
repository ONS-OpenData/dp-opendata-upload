This lambda is triggered by [opendata-transformer-lambda](https://github.com/ONS-OpenData/dp-opendata-upload/blob/main/opendata-transformer-lambda/README.md)

**Actions**
- Gets the `main.py` file for the relevant dataset from the [cmd-transforms](https://github.com/ONS-OpenData/cmd-transforms) repo and stores it as a string
- If there is a `requirements.txt` file in the relevant dataset folder then this is read in too. This file gives a list of any other python files that are required for the transform. These are then read in as a string.
- Returns the transform script and returns any requirements. Will return an empty dict of requirements if there aren't any
