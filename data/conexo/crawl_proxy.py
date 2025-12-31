from mitmproxy import http
from pydantic import BaseModel


class Record(BaseModel):
    url: str
    status_code: int
    text: str | None


def response(flow: http.HTTPFlow):
    url = flow.request.url
    response = flow.response

    if response is not None:
        if "https://firestore.googleapis.com/google.firestore.v1.Firestore/Listen/channel" in url:
            with open("log.txt", "a", encoding="utf8") as f:
                f.write(
                    Record(
                        url=url, status_code=response.status_code, text=response.text
                    ).model_dump_json()
                )

                f.write("\n")
