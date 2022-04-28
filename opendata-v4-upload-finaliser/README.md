This lambda is triggered by [opendata-v4-upload-poller](https://github.com/ONS-OpenData/dp-opendata-upload/blob/main/opendata-v4-upload-poller/README.md). The purpose of the finaliser is to use the CMD APIs to make the data ready for publishing.

**Actions**
- Creates a new collection
- Updates the dataset specific metadata (title, contact details, etc)
- Assigns the instance a version number by changing its state
- Adds the data to the newly created collection
- Updates dimension specific metadata (dimension labels and descriptions)
- Updates any further metadata (usage notes)
