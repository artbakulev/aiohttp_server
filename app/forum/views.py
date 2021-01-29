from datetime import datetime

import aiohttp_jinja2
from aiohttp import web
from aiohttp_apispec import request_schema, docs, response_schema

from app.base.responses import json_response
from app.base.schemas import BaseResponseSchema
from app.base.utils import analyze_text
from app.forum.models import Message
from app.forum.schemas import (
    CreateMessageRequestSchema,
    ListMessageResponseSchema,
    CreateMessageResponseSchema,
)


@aiohttp_jinja2.template("index.html")
async def index(_):
    return {}


class CreateMessageView(web.View):
    @docs(
        tags=["message"],
        summary="Method for posting new message",
        description="Create new message, analyze it and add to database",
    )
    @request_schema(CreateMessageRequestSchema)
    @response_schema(
        BaseResponseSchema, 200, description="New message has been created"
    )
    async def post(self):
        text = self.request["data"]["text"]
        polarity, subjectivity = analyze_text(text)
        message = await self.request.app["db"].message.create(
            text=text,
            created=datetime.now(),
            polarity=polarity,
            subjectivity=subjectivity,
        )

        average_polarity, average_subjectivity = await self.request.app[
            "db"
        ].get_total_polarity_and_subjectivity()
        await self.request.app["telegram"].send_message(
            text, polarity, subjectivity, average_polarity, average_subjectivity
        )
        return json_response(data=CreateMessageResponseSchema().dump(message))


class ListMessageView(web.View):
    @docs(
        tags=["message"],
        summary="Method for listing messages",
        description="List messages in desc order",
    )
    @response_schema(ListMessageResponseSchema(), 200, description="List messages")
    async def get(self):
        messages = await Message.query.order_by(Message.id.desc()).gino.all()
        return json_response(
            data=ListMessageResponseSchema().dump({"messages": messages})
        )
