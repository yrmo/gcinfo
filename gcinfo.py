import requests


import requests

CKAN_BASE = "https://open.canada.ca/data/api/3/action"

def find_rbpo_rppo_en_url():
    """
    Discover the current English rbpo_rppo_en.csv download URL
    from the GC InfoBase Departmental Plans / Results dataset.
    """
    search_params = {
        "q": "GC InfoBase Departmental Plans Results Expenditures Full Time Equivalents",
        "rows": 10,
        "fq": "res_format:CSV"
    }

    r = requests.get(f"{CKAN_BASE}/package_search", params=search_params, timeout=30)
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
        package = results[0]          # fallback to the top hit

    print(f"Using package: {package['title']}  (id={package['id']})")

    # Look through its resources for the English expenditures/FTE CSV
    for res in package.get("resources", []):
        name = (res.get("name") or "").lower()
        url  = res.get("url") or ""
        fmt  = (res.get("format") or "").upper()

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
