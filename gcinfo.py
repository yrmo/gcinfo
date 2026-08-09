import requests
from typing import Optional

CKAN = "https://open.canada.ca/data/api/3/action"


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


def list_resources(package: dict, preferred_formats: list[str] = None):
    """Pretty-print the downloadable resources of a package."""
    preferred_formats = preferred_formats or ["CSV", "JSON", "XLSX", "XML", "GEOJSON"]

    print(f"\n=== {package['title']} ===")
    print(f"ID: {package['id']}")
    print(f"Org: {package.get('organization', {}).get('title')}")
    print(f"Notes: {(package.get('notes') or '')[:200]}...")

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
