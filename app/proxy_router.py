from fastapi import APIRouter, Request
from fastapi.responses import Response
import httpx
from app.services import SERVICE_ROUTES

proxy_router = APIRouter()

@proxy_router.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def proxy(full_path: str, request: Request):
    matched_prefix = None

    for key, target_url in SERVICE_ROUTES.items():
        if full_path.startswith(f"{key}/") or full_path == key:
            trimmed_path = full_path[len(key):].lstrip("/")
            destination_url = f"{target_url}/{trimmed_path}"
            matched_prefix = key
            break
    else:
        return {"error": "Unknown service path."}

    method = request.method
    headers = dict(request.headers)
    body = await request.body()

    async with httpx.AsyncClient(follow_redirects=False) as client:
        try:
            response = await client.request(
                method=method,
                url=destination_url,
                headers=headers,
                content=body
            )

            response_headers = dict(response.headers)

            location = response_headers.get("location")
            if location and location.startswith("/") and matched_prefix:
                if not location.startswith(f"/{matched_prefix}/"):
                    response_headers["location"] = f"/{matched_prefix}{location}"

            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=response_headers,
                media_type=response.headers.get("content-type")
            )

        except httpx.RequestError as e:
            return {"error": f"Service unreachable: {e}"}