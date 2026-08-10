# gcinfo

```py
# List dataset titles that match a query and have type CSV
import gcinfo

gcinfo.search_titles(query="temporary", format_filter="CSV")
```

```py
# List resources on a dataset by querying it's exact title
import gcinfo

gcinfo.list_resources(gcinfo.search_datasets(query='title:"Estimates of the number of non-permanent residents by type, quarterly"')["results"][0])
```

```py
# List all datasets their datatypes that have type CSV, limiting to 15 datasets per Open Canada API call
import gcinfo

result = gcinfo.search_datasets(query="*:*", rows=15, format_filter="CSV")
print(f"Total matching packages: {result['count']}")

for i, dataset in enumerate(result["results"]):
    if i == 2:
        break
    gcinfo.list_resources(dataset)
```

```py
# Other dataset search examples
result = gcinfo.search_datasets(query="GC InfoBase OR \"Departmental Plans\" OR \"Departmental Results\"", rows=10)
result = gcinfo.search_datasets(organization="cbsa-asfc", format_filter="CSV")
result = gcinfo.search_datasets(format_filter="JSON", rows=25)
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
