import httpx
import asyncio
import time
from config import TIMEOUT, REPEAT
from reporter import record_result

async def hit_endpoint(session, request, results):
    url = request['url']
    method = request['method'].lower()
    headers = request.get('headers', {})
    body = request.get('body', {})

    try:
        start = time.monotonic()
        response = await session.request(method, url, headers=headers, json=body, timeout=TIMEOUT)
        elapsed = time.monotonic() - start

        record_result(results, True, elapsed, response.status_code)
    except Exception as e:
        record_result(results, False, None, str(e))

async def run_requests_concurrently(requests, concurrency):
    results = {"success": 0, "fail": 0, "times": [], "status_codes": {}, "errors": []}
    
    connector = httpx.AsyncClient()
    sem = asyncio.Semaphore(concurrency)

    async def sem_task(req):
        async with sem:
            await hit_endpoint(connector, req, results)

    tasks = [sem_task(req) for _ in range(REPEAT) for req in requests]
    await asyncio.gather(*tasks)
    await connector.aclose()
    return results
