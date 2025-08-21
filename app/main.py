from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse
import httpx

app = FastAPI(title="Gateway (простой)")

SERVICE_ROUTES = {
    "lobby":   "http://host.docker.internal:8000",
    "tracker": "http://host.docker.internal:8100",
}

@app.get("/health")
def health():
    return {"status": "ok", "routes": SERVICE_ROUTES}

def _match_service(full_path: str):
    """
    Возвращает (service_key, base_url, trimmed_path), либо (None, None, "").
    """
    parts = [p for p in full_path.split("/") if p]
    if not parts:
        return None, None, ""
    key = parts[0]
    base = SERVICE_ROUTES.get(key)
    trimmed = "/".join(parts[1:])
    return key, base, trimmed

@app.api_route("/{full_path:path}", methods=["GET","POST","PUT","DELETE","PATCH","OPTIONS"])
async def proxy(full_path: str, request: Request):
    service_key, base_url, trimmed_path = _match_service(full_path)
    if not base_url:
        raise HTTPException(status_code=404, detail=f"Service not found for path '/{full_path}'")

    orig_has_slash = request.url.path.endswith("/")
    if trimmed_path:
        dest = f"{base_url}/{trimmed_path}"
        if orig_has_slash and not dest.endswith("/"):
            dest += "/"
    else:
        dest = base_url

    method  = request.method.upper()
    headers = dict(request.headers)
    body    = await request.body()
    params  = dict(request.query_params)

    try:
        async with httpx.AsyncClient(follow_redirects=False, timeout=15.0) as client:
            resp = await client.request(method, dest, headers=headers, content=body, params=params)
    except httpx.ConnectError as e:
        raise HTTPException(status_code=502, detail=f"Upstream connect error: {e}")
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail=f"Upstream timeout")

    excluded = {"content-encoding", "transfer-encoding", "connection"}
    out_headers = [(k,v) for k,v in resp.headers.items() if k.lower() not in excluded]

    return StreamingResponse(
        resp.aiter_bytes(),
        status_code=resp.status_code,
        headers=dict(out_headers),
        media_type=resp.headers.get("content-type"),
    )