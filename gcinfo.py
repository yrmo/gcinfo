from pathlib import Path
import requests
import zipfile
import io
import pandas as pd
from typing import Optional, Tuple

CKAN = "https://open.canada.ca/data/api/3/action"
CACHE_DIR = Path("cache")
CACHE_DIR.mkdir(exist_ok=True)


def search_datasets(
    query: str = "*:*",
    rows: int = 20,
    start: int = 0,
    organization: Optional[str] = None,
    format_filter: Optional[str] = None,  # e.g. "CSV", "JSON", "XLSX"
    tags: Optional[list[str]] = None,
) -> dict:
    """
    Search the Open Canada CKAN catalog.
    Returns the raw package_search result.
    """
    params = {
        "q": query,
        "rows": rows,
        "start": start,
    }

    fq_parts = []
    if organization:
        fq_parts.append(f"organization:{organization}")
    if format_filter:
        fq_parts.append(f"res_format:{format_filter}")
    if tags:
        for tag in tags:
            fq_parts.append(f"tags:{tag}")

    if fq_parts:
        params["fq"] = " AND ".join(fq_parts)

    r = requests.get(f"{CKAN}/package_search", params=params, timeout=30)
    r.raise_for_status()
    return r.json()["result"]


def search_titles(*args, **kwargs):
    for dataset in search_datasets(*args, **kwargs)["results"]:
        list_title(dataset)


def download_zip(
    url: str,
    force: bool = False,
    return_metadata: bool = True,
) -> Tuple[pd.DataFrame, Optional[pd.DataFrame]]:
    """
    Download a StatCan table ZIP, cache it, and return the data (and optional metadata) DataFrames.

    Parameters
    ----------
    url : str
        Full URL to the .zip file (e.g. https://www150.statcan.gc.ca/n1/tbl/csv/17100121-eng.zip)
    force : bool
        If True, re-download even if the file is already cached.
    return_metadata : bool
        If True, also return the metadata CSV as a second DataFrame.

    Returns
    -------
    (df, df_metadata)  or  (df, None)
    """
    filename = url.split("/")[-1]
    cache_path = CACHE_DIR / filename

    if force or not cache_path.exists():
        print(f"Downloading {filename} ...")
        r = requests.get(url)
        r.raise_for_status()
        cache_path.write_bytes(r.content)
        print(f"Saved to {cache_path}")
    else:
        print(f"Using cached file: {cache_path}")

    with zipfile.ZipFile(cache_path) as z:
        csv_files = [n for n in z.namelist() if n.lower().endswith(".csv")]

        if not csv_files:
            raise ValueError("No CSV files found in the ZIP")

        # First CSV is almost always the data
        with z.open(csv_files[0]) as f:
            df = pd.read_csv(f)

        df_metadata = None
        if return_metadata and len(csv_files) > 1:
            with z.open(csv_files[1]) as f:
                df_metadata = pd.read_csv(f)

    return df, df_metadata


from pathlib import Path
from typing import Optional, Tuple, Union, Dict
import requests
import pandas as pd

# Assume this already exists in your module
CACHE_DIR = Path("cache")  # or whatever you use
CACHE_DIR.mkdir(exist_ok=True)


def download_xlsx(
    url: str,
    force: bool = False,
    sheet_name: Union[str, int, list, None] = 0,
    return_all_sheets: bool = False,
) -> Union[pd.DataFrame, Dict[str, pd.DataFrame]]:
    """
    Download an IRCC / open-data XLSX file, cache it, and return a DataFrame
    (or dict of DataFrames if multiple sheets).

    Parameters
    ----------
    url : str
        Full URL to the .xlsx file
        (e.g. https://www.ircc.canada.ca/opendata-donneesouvertes/data/EN_ODP_annual-TR-work-IMP_PT_program_year_end.xlsx)
    force : bool
        If True, re-download even if the file is already cached.
    sheet_name : str | int | list | None
        Which sheet(s) to load. Same behaviour as pd.read_excel.
        Default = 0 (first sheet).
    return_all_sheets : bool
        If True, ignore sheet_name and return a dict of {sheet_name: DataFrame}
        for every sheet in the workbook.

    Returns
    -------
    pd.DataFrame
        or Dict[str, pd.DataFrame] when return_all_sheets=True
    """
    filename = url.split("/")[-1]
    filename = filename.split("?")[0]  # clear query parameters
    cache_path = CACHE_DIR / filename

    if force or not cache_path.exists():
        print(f"Downloading {filename} ...")
        r = requests.get(url, timeout=60)
        r.raise_for_status()
        cache_path.write_bytes(r.content)
        print(f"Saved to {cache_path}")
    else:
        print(f"Using cached file: {cache_path}")

    if return_all_sheets:
        xls = pd.ExcelFile(cache_path)
        return {name: pd.read_excel(xls, sheet_name=name) for name in xls.sheet_names}

    return pd.read_excel(cache_path, sheet_name=sheet_name)


def list_resources(package: dict, preferred_formats: list[str] = None):
    """Pretty-print the downloadable resources of a package."""
    preferred_formats = preferred_formats or ["CSV", "JSON", "XLSX", "XML", "GEOJSON"]

    print(f"\n=== {package['title']} ===")
    print(f"ID: {package['id']}")
    print(f"Org: {package.get('organization', {}).get('title')}")
    print(f"Notes: {(package.get('notes') or '')[:200]}...")

    # --- Web UI link ---
    web_url = None

    # 1. Try package['url'] (sometimes a string, sometimes {'en': ..., 'fr': ...})
    raw_url = package.get("url")
    if isinstance(raw_url, dict):
        web_url = raw_url.get("en") or raw_url.get("fr")
    elif isinstance(raw_url, str) and raw_url.startswith("http"):
        web_url = raw_url

    # 2. Better: detect StatCan table number from resource download URLs
    #    e.g. .../98100361-eng.zip  →  https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=9810036101
    table_id = None
    if not web_url or "cansim/home" in (web_url or ""):
        import re

        for res in package.get("resources", []):
            url = res.get("url") or ""
            m = re.search(r"/(\d{8})-(?:eng|fra)\.zip", url)
            if m:
                table_id = m.group(1)
                web_url = f"https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid={table_id}01"
                break

    if web_url:
        print(f"URL: {web_url}")

    citation = None

    # Prefer official StatCan-style citation when we can build it
    org = (
        package.get("org_title_at_publication", {}).get("en")
        or package.get("organization", {}).get("title")
        or "Statistics Canada"
    )
    title = package.get("title") or package.get("title_translated", {}).get("en")

    table_number = None
    series = package.get("data_series_issue_identification", {})
    if isinstance(series, dict):
        raw = series.get("en") or series.get("fr") or ""
        # "Table 17100121" → "17-10-0121-01"
        import re

        m = re.search(r"(\d{8})", raw)
        if m:
            tid = m.group(1)
            table_number = f"{tid[:2]}-{tid[2:4]}-{tid[4:8]}-01"
    elif table_id:
        table_number = f"{table_id[:2]}-{table_id[2:4]}-{table_id[4:8]}-01"

    if table_number and title:
        citation = f"{org}. Table {table_number} {title}"
    elif title:
        citation = f"{org}. {title}"

    # Also surface any explicit citation / DOI-like fields if they exist
    explicit = (
        package.get("citation") or package.get("doi") or package.get("identifier")
    )
    if explicit:
        citation = explicit if not citation else f"{citation}\n  (also: {explicit})"

    if citation:
        print(f"Citation: {citation}")
        if table_number:
            print(
                f"DOI:      https://doi.org/10.25318/{table_number.replace('-', '')}-eng"
            )

    for res in package.get("resources", []):
        fmt = (res.get("format") or "").upper()
        if preferred_formats and fmt not in preferred_formats:
            continue
        print(f"  [{fmt:8}] {res.get('name')}")
        print(f"           {res.get('url')}")


def list_title(package: dict, preferred_formats: list[str] = None):
    """Pretty-print the downloadable resources of a package."""
    preferred_formats = preferred_formats or ["CSV", "JSON", "XLSX", "XML", "GEOJSON"]

    print(f"{package['title']}")


def find_resource_url(
    query: str, name_contains: str, format: str = "CSV"
) -> str | None:
    """
    Search for a dataset and return the first resource URL whose name
    contains the given substring.
    """
    result = search_datasets(query=query, rows=10, format_filter=format)

    for pkg in result["results"]:
        for res in pkg.get("resources", []):
            name = (res.get("name") or "").lower()
            url = res.get("url") or ""
            if name_contains.lower() in name and url:
                return url
    return None


def search_cbsa_enforcement(rows: int = 25) -> list[dict]:
    """
    Return the most relevant CBSA + enforcement-related packages.
    """
    # Two complementary queries
    queries = [
        {"q": "organization:cbsa-asfc", "rows": rows},
        {
            "q": 'title:(removals OR detention OR "traveller volumes" OR "border wait" OR AMPS OR "administrative monetary")',
            "rows": 15,
        },
        {"q": '"Removals Processed by Region"', "rows": 5},
    ]

    seen = set()
    packages = []

    for params in queries:
        r = requests.get(f"{CKAN}/package_search", params=params, timeout=30)
        r.raise_for_status()
        for pkg in r.json()["result"]["results"]:
            if pkg["id"] not in seen:
                seen.add(pkg["id"])
                packages.append(pkg)

    return packages


def show_package(pkg: dict, max_resources: int = 6):
    org = (pkg.get("organization") or {}).get("title", "?")
    print(f"\n• {pkg['title']}")
    print(f"  {org}")
    print(f"  https://open.canada.ca/data/en/dataset/{pkg['id']}")

    for res in pkg.get("resources", [])[:max_resources]:
        fmt = (res.get("format") or "").upper()
        if fmt in {"CSV", "JSON", "XLSX", "XML", "TXT"}:
            print(f"    [{fmt:5}] {res.get('name')}")
            print(f"           {res.get('url')}")


def find_rbpo_rppo_en_url():
    """
    Discover the current English rbpo_rppo_en.csv download URL
    from the GC InfoBase Departmental Plans / Results dataset.
    """
    search_params = {
        "q": "GC InfoBase Departmental Plans Results Expenditures Full Time Equivalents",
        "rows": 10,
        "fq": "res_format:CSV",
    }

    r = requests.get(f"{CKAN}/package_search", params=search_params, timeout=30)
    r.raise_for_status()
    results = r.json()["result"]["results"]

    if not results:
        raise RuntimeError("No matching package found")

    # Prefer the main "Departmental Plans and Results Reports" package
    package = None
    for pkg in results:
        title = pkg.get("title", "").lower()
        if "departmental plans" in title and "results" in title:
            package = pkg
            break
    if package is None:
        package = results[0]  # fallback to the top hit

    print(f"Using package: {package['title']}  (id={package['id']})")

    # Look through its resources for the English expenditures/FTE CSV
    for res in package.get("resources", []):
        name = (res.get("name") or "").lower()
        url = res.get("url") or ""
        fmt = (res.get("format") or "").upper()

        if fmt == "CSV" and (
            "rbpo_rppo_en.csv" in url.lower()
            or ("expenditure" in name and "fte" in name and "english" in name)
            or ("expenditures and full time equivalents" in name and "en" in name)
        ):
            return url

    raise RuntimeError("Could not find the English rbpo_rppo CSV resource")


if __name__ == "__main__":
    url = find_rbpo_rppo_en_url()
    # url = "https://open.canada.ca/data/dataset/a35cf382-690c-4221-a971-cf0fd189a46f/resource/64774bc1-c90a-4ae2-a3ac-d9b50673a895/download/rbpo_rppo_en.csv"
    # url = "https://open.canada.ca/data/dataset/b15ee8d7-2ac0-4656-8330-6c60d085cda8/resource/02929919-d9ab-494e-8fce-012119b479ff/download/rbpo_rppo_en.csv"
    print(f"{url=}")

    r = requests.get(url, allow_redirects=True, timeout=60)
    r.raise_for_status()

    print(r.status_code)
    print(r.headers.get("content-type"))
    print(len(r.content), "bytes")

    with open("rbpo_rppo_en.csv", "wb") as f:
        f.write(r.content)
