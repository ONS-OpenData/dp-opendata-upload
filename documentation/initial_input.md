# Initial Input

At time of writing we're not 100% sure what the initial inputs will be (or the format of the metadata) so we're starting with an assumption of a zip file appearing in the bucket `opendata-transform-needed-source-bucket`.

The contents of this zip file will be:

```
/manifest.json
/<metadata file in whatever format>
/<1-n files of source data in whatever format>
```

The `manifest.json` will contain the following json key

```json
{
  "metadata": "<the exact file from the zip that represents metadata",
  "metadata_handler": "<explicitly declared for use by `opendata-v4-metadata-parser`>" 
}
```

All files from the zip other than `manifest.json` and the file declared by the above `metadata` key are assumed to be source data files required by a transform.

**Example**

contents of zip

```
/manfiest.json
/ashe_metadata_csvw.json
/ashe_source1.xls
/ashe_source2.xls
```

would have the manifest

```json
{
  "metadata": "ashe_metadata_csvw.json",
  "metadata_handler": "csvw" 
}
```

### what's the point of metadata_handler?

tbh in most cases it'll be unnecessary, but as soon as we start getting 2 way of representing metadata in the same format (i.e 2 json representations of metadata that need to be parsed in slightly different ways) it'll make our lives _much_ easier. 
