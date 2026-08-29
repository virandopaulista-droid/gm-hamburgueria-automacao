import json
import mimetypes
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

IMAGE_PATH = "/home/runner/gdrive/Agência BEEF MTK/Clientes /GM - Hamburgueria /STORIES /Brenda - Stories /3.jpg"

page_id = os.environ["FB_PAGE_ID"]
ig_id = os.environ["IG_BUSINESS_ID"]
token = os.environ["FB_PAGE_ACCESS_TOKEN"]


def post_multipart(url, fields, files):
    import uuid
    boundary = uuid.uuid4().hex
    body = b""
    for name, value in fields.items():
        body += (f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"\r\n\r\n{value}\r\n").encode("utf-8")
    for name, filename, content in files:
        ctype = mimetypes.guess_type(filename)[0] or "application/octet-stream"
        body += (f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"; filename=\"{filename}\"\r\nContent-Type: {ctype}\r\n\r\n").encode("utf-8") + content + b"\r\n"
    body += f"--{boundary}--\r\n".encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}, method="POST")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def post_form(url, fields):
    req = urllib.request.Request(url, data=urllib.parse.urlencode(fields).encode("utf-8"), method="POST")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def get_json(url):
    with urllib.request.urlopen(url) as resp:
        return json.loads(resp.read())


def post_form_retry(url, fields, retries=5, delay=4):
    for attempt in range(1, retries + 1):
        try:
            return post_form(url, fields)
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8")
            if attempt == retries or "2207027" not in body:
                raise
            print(f"  (midia ainda nao pronta no IG, tentativa {attempt}/{retries}, aguardando {delay}s...)", file=sys.stderr)
            time.sleep(delay)


# Upload the photo UNPUBLISHED (published:false) just to get a fresh public
# CDN URL for Instagram -- does NOT create a new visible Facebook post, so
# no risk of duplicating the FB story that already went out for real on
# 2026-08-11 before the original run crashed on the IG leg.
with open(IMAGE_PATH, "rb") as f:
    image_bytes = f.read()

photo_result = post_multipart(
    f"https://graph.facebook.com/v20.0/{page_id}/photos",
    {"access_token": token, "published": "false"},
    [("source", os.path.basename(IMAGE_PATH), image_bytes)],
)
info = get_json(f"https://graph.facebook.com/v20.0/{photo_result['id']}?fields=images&access_token={urllib.parse.quote(token, safe='')}")
public_url = info["images"][0]["source"]

container = post_form_retry(
    f"https://graph.facebook.com/v20.0/{ig_id}/media",
    {"access_token": token, "image_url": public_url, "media_type": "STORIES"},
)
ig_story = post_form_retry(
    f"https://graph.facebook.com/v20.0/{ig_id}/media_publish",
    {"access_token": token, "creation_id": container["id"]},
)
print(f"IG story publicado: {ig_story}")
