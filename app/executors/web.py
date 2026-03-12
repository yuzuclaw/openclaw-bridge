import httpx


async def fetch_url(input_data: dict) -> dict:
    url = input_data["url"]
    verify = bool(input_data.get("verify_ssl", False))
    async with httpx.AsyncClient(timeout=20, follow_redirects=True, verify=verify) as client:
        resp = await client.get(url)
    text = resp.text[:20000]
    return {
        "ok": resp.status_code < 400,
        "data": {
            "url": str(resp.url),
            "status_code": resp.status_code,
            "content": text,
            "verify_ssl": verify,
        },
        "error": None if resp.status_code < 400 else f"http status {resp.status_code}",
    }
