from urllib.request import urlopen


def download_source(url: str) -> bytes:
    with urlopen(url) as req:
        data = req.read()
    assert isinstance(data, bytes)
    return data
