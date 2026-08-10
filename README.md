# gcinfo

```py
# List dataset titles that match a query and have type CSV
import gcinfo

gcinfo.search_titles(query="non-permanent", format_filter="CSV")
```

```py
# List resources on a dataset by querying it's exact title
import gcinfo

gcinfo.list_resources(gcinfo.search_datasets(query='title:"Estimates of the number of non-permanent residents by type, quarterly"')["results"][0])
```

```py
df, df_meta = gcinfo.download_zip("https://www150.statcan.gc.ca/n1/tbl/csv/17100121-eng.zip") # URL from list_resources
```

# [Solr query syntax](https://solr.apache.org/guide/solr/latest/query-guide/standard-query-parser.html)

|Query                                        |Meaning                           |
|---------------------------------------------|----------------------------------|
|`*:*`                                          |Everything                        |
|`border`                                       |Free-text search for “border”     |
|`title:removals`                               |Word “removals” in the title field|
|`organization:cbsa-asfc`                       |Exact organization slug           |
|`res_format:CSV`                               |Has at least one CSV resource     |
|`tags:immigration`                             |Has the tag “immigration”         |
|`title:(removals OR detention)`                |Title contains either word        |
|`metadata_modified:[2024-01-01T00:00:00Z TO *]`|Updated since 2024                |
