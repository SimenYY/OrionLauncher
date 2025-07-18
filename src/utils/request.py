from typing import Callable

import httpx

from src.utils.Exceptions import *
from src.utils.tools import empty


async def request_json(
    url: str,
    method: str = "GET",
    headers: dict = {},
    finnished: Callable = empty,
    error: Callable = empty,
) -> dict | list | None:
    """
    发送请求并返回 JSON 数据
    """
    try:
        async with httpx.AsyncClient() as client:
            if method.upper() == "GET":
                response = await client.get(url, headers=headers)
            elif method.upper() == "POST":
                response = await client.post(url, headers=headers)
            elif method.upper() == "PUT":
                response = await client.put(url, headers=headers)
            elif method.upper() == "DELETE":
                response = await client.delete(url, headers=headers)
            else:
                raise NetworkException(f"不支持的HTTP方法: {method}")

            response.raise_for_status()
            json_data = response.json()

            if finnished and callable(finnished):
                finnished(json_data)

            return json_data
    except httpx.HTTPStatusError as e:
        error_msg = f"HTTP状态错误: {e.response.status_code} - {url}"
        if error and callable(error):
            error(error_msg)
        raise ApiException(
            error_msg, details={"status_code": e.response.status_code, "url": url}
        )
    except httpx.RequestError as e:
        error_msg = f"请求错误: {str(e)} - {url}"
        if error and callable(error):
            error(error_msg)
        raise NetworkException(error_msg, details={"url": url, "error": str(e)})
    except Exception as e:
        error_msg = f"请求JSON数据时发生错误: {str(e)}"
        if error and callable(error):
            error(error_msg)
        raise WrappedSystemException(e, error_msg)
