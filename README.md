# gcinfo

```py
import gcinfo
```

```py
# List dataset titles that match a query and have type CSV
gcinfo.search_titles(query="non-permanent", format_filter="CSV")
```

```py
# List resources on a dataset by querying it's exact title
gcinfo.list_resources(gcinfo.search_datasets(query='title:"Estimates of the number of non-permanent residents by type, quarterly"')["results"][0])
```

```py
# Download and store dataset and metadata in dataframes
df, df_meta = gcinfo.download_zip("https://www150.statcan.gc.ca/n1/tbl/csv/17100121-eng.zip")
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

# Plot Prompt

Make a matplotlib line plot in **exactly** this style:

- Use `fig, ax = plt.subplots()` (default figsize, do not set a custom size)
- If plotting **multiple series**, use `marker="."` and `linestyle="solid"`
- If plotting **only one series**, use a solid line (`linestyle="-"`) with `marker="."`
- Put the legend **below** the plot using:
  ```python
  ax.legend(
      title=None,
      loc="upper center",
      bbox_to_anchor=(0.5, -0.22),
      ncol=1,
      frameon=True
  )
  ```
- Add a source citation under the legend with:
  ```python
  plt.figtext(
      0.5, -0.03,
      "Source: [insert source here]",
      ha="center",
      fontsize=8,
      style="italic"
  )
  ```
  (I will tell you the exact source text each time)
- Use `plt.subplots_adjust(bottom=0.3)`
- Rotate x-tick labels: `plt.xticks(rotation=45, ha="right")`
- End with `plt.tight_layout()` then `plt.show()`
- Set title, xlabel, and ylabel with `ax.set_...`
- Shorten long legend labels when it improves readability

Match this style precisely (including the default figsize).
