import json

from mitmproxy import http


def response(flow: http.HTTPFlow):
    url = flow.request.url
    response = flow.response

    if response is not None:
        cur_text: str | None = response.text

        if "https://firestore.googleapis.com/google.firestore.v1.Firestore/Listen/channel" in url:
            with open("log.txt", "a", encoding="utf8") as f:
                print(
                    json.dumps(
                        {"url": url, "status_code": response.status_code, "text": cur_text},
                        ensure_ascii=True,
                        separators=(",", ":"),
                    ),
                    file=f,
                )
