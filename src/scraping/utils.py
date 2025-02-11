import re
from re import Pattern

URL_PATTERN: Pattern = re.compile(
    r"^(?:https?:\/\/)?([\w\-]+(\.[\w\-]+)+)([\w\-\.,@?^=%&:\/~\+#]*[\w\-\@?^=%&\/~\+#])?$"
)


def validate_urls(urls: list[str]):
    # Normalize the URLs and remove duplicates.
    urls = [url.strip() for url in urls]
    urls = list(set(urls))

    valid, invalid = [], []

    for url in urls:
        if URL_PATTERN.match(url):
            valid.append(url)
        else:
            invalid.append(url)

    if invalid:
        print(f"There are {len(invalid)} invalid URLs in the list. Skipping them.")

    if not valid:
        raise ValueError("No valid URLs provided.")

    # If the URL doesn't have a protocol, add https://
    valid = [url if url.startswith("http") else f"https://{url}" for url in valid]


    return valid
