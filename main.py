from aiohttp import web
import aiohttp_cors
from handlers import setup_routes
import logging
import os
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent

async def init_app():
    app = web.Application()
    
    # Setup CORS
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
        )
    })
    
    # Setup static routes first
    app.router.add_static('/static/', path=BASE_DIR / 'static', name='static')
    
    # Setup API routes
    setup_routes(app, cors)
    
    # Add route for serving index.html
    async def serve_index(request):
        return web.FileResponse(BASE_DIR / 'static' / 'index.html')
    
    app.router.add_get('/', serve_index)
    
    return app

if __name__ == '__main__':
    app = init_app()
    from config import WEBAPP_HOST, WEBAPP_PORT
    web.run_app(app, host=WEBAPP_HOST, port=WEBAPP_PORT)
