"""
Very small client that

1. Zips  the contents of   ../data/data
2. Base-64 encodes the bytes so they fit into JSON
3. Sends them to  http://localhost:8000/estimate
4. Prints the returned 4 × 4 matrix
"""

import os, io, zipfile, base64, requests


SERVER_URL = "http://127.0.0.1:8000/estimate"


def _zip_dir_to_bytes(dir_path: str) -> bytes:
    """Create an in-memory ZIP archive of `dir_path`."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(dir_path):
            for f in files:
                full_path = os.path.join(root, f)
                rel_path = os.path.relpath(full_path, dir_path)
                zf.write(full_path, arcname=rel_path)
    return buf.getvalue()


def main() -> None:
    data_dir = "/Users/kobikelemen/robots/data/data"
    raw_zip  = _zip_dir_to_bytes(data_dir)

    # JSON only knows strings → base-64 the raw bytes
    payload_b64 = base64.b64encode(raw_zip).decode("ascii")
    # breakpoint()
    response = requests.post(SERVER_URL, json={"payload": payload_b64}, timeout=60)
    response.raise_for_status()

    transform = response.json()["transform"]
    print("4×4 transform matrix from server:")
    for row in transform:
        print(row)


if __name__ == "__main__":
    main()