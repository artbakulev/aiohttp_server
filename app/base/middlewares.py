import logging
from datetime import datetime

from aiohttp import web

from app.base.responses import json_response


@web.middleware
async def error_middleware(request, handler):
    try:
        return await handler(request)
    except web.HTTPException as ex:
        return json_response(status=ex.status, text_status=ex.text, data={})
    except Exception as e:
        return json_response(status=500, text_status=str(e), data={})


@web.middleware
async def request_logging_middleware(request: web.Request, handler):
    logger = logging.getLogger("request")
    logger.info("%s %s %d", datetime.now().strftime("%S:%M:%H %D.$m.%Y"), request.host)
    logger.info(request.url, request.content)
    response: web.Response = await handler(request)
    logger.info(response.status, response.text)
    return response
