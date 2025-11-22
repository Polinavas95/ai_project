import logging
import re

import orjson
from json_repair import repair_json


logger = logging.getLogger(__name__)

CODEBLOCK_PATTERN = re.compile(r"```(?P<type>\S*)\s*(?P<body>.*?)\s*```", re.MULTILINE | re.DOTALL)


class JSONParserError(Exception): ...


def parse_json(text: str):
    text = text.strip()
    match = re.match(CODEBLOCK_PATTERN, text)
    if match:
        _, body = match.groups()
        text = body
    try:
        return orjson.loads(text)
    except orjson.JSONDecodeError:
        text = repair_json(text)
    try:
        return orjson.loads(text)
    except orjson.JSONDecodeError as exc:
        logger.error("Invalid GigaChat response: invalid JSON string")
        raise JSONParserError from exc
