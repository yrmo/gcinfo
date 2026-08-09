# gcinfo

```py
import gcinfo

result = gcinfo.search_datasets(query="*:*", rows=15, format_filter="CSV")
print(f"Total matching packages: {result['count']}")

for i, pkg in enumerate(result["results"]):
    if i == 3:
        break
    gcinfo.list_resources(pkg)

result = gcinfo.search_datasets(query="removals", rows=20, format_filter="CSV")
for i, pkg in enumerate(result["results"]):
    if i == 3:
        break
    gcinfo.list_resources(pkg)

# result = gcinfo.search_datasets(query="GC InfoBase OR \"Departmental Plans\" OR \"Departmental Results\"", rows=10)
# result = gcinfo.search_datasets(organization="cbsa-asfc", format_filter="CSV")
# result = gcinfo.search_datasets(format_filter="JSON", rows=25)
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
