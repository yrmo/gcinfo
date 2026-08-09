# gcinfo

```py
# List dataset titles that match a query and have type CSV
import gcinfo

for i, pkg in enumerate(gcinfo.search_datasets(query="temporary", format_filter="CSV")["results"]):
    gcinfo.list_title(pkg)
```

```py
# List resources on a dataset by querying it's exact title
import gcinfo

for i, pkg in enumerate(gcinfo.search_datasets(query='title:"Temporary Residents: Temporary Foreign Worker Program (TFWP) and International Mobility Program (IMP) Work Permit Holders – Monthly IRCC Updates"', format_filter="CSV")["results"]):
    gcinfo.list_resources(pkg)
```

```py
# List all datasets their datatypes that have type CSV, limiting to 15 datasets per Open Canada API call
import gcinfo

result = gcinfo.search_datasets(query="*:*", rows=15, format_filter="CSV")
print(f"Total matching packages: {result['count']}")

for i, pkg in enumerate(result["results"]):
    if i == 2:
        break
    gcinfo.list_resources(pkg)
```

```py
# Other dataset search examples
result = gcinfo.search_datasets(query="GC InfoBase OR \"Departmental Plans\" OR \"Departmental Results\"", rows=10)
result = gcinfo.search_datasets(organization="cbsa-asfc", format_filter="CSV")
result = gcinfo.search_datasets(format_filter="JSON", rows=25)
```

## Government of Canada Information

|Purpose                      |Endpoint                             |
|-----------------------------|-------------------------------------|
|Search packages              |`/package_search`                      |
|Get one package by id/name   |`/package_show?id=...`                 |
|Search resources             |`/resource_search?query=name:something`|
|List all organizations       |`/organization_list`                   |
|List all tags                |`/tag_list`                            |
|Package list (just names/ids)|`/package_list`                        |

- [GC InfoBase - Open Datasets](https://open.canada.ca/data/en/dataset/a35cf382-690c-4221-a971-cf0fd189a46f)
- [GC InfoBase – Departmental Plans and Results Reports](https://open.canada.ca/data/en/dataset/b15ee8d7-2ac0-4656-8330-6c60d085cda8)

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
