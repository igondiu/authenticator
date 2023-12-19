# -*- coding: utf-8 -*-

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(
    tags=["service_info"],
    responses={
        404: {"description": "Route doesn't exist"}
    }
)


@router.get("/")
def welcome_page():
    html_code = """
    <!DOCTYPE html>
    <html>
    <body>
    <h1>AUTHENTICATOR welcome page</h1>
    <ul>
      <li><a href="/docs">SWAGGER</a></li>
      <li><a href="/locate">LOCATE</a></li>
    </ul>
    </body>
    </html> """
    return HTMLResponse(html_code)
