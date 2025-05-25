"""
Local OAuth redirect server for Gmail authentication.

This module provides a temporary local server to handle OAuth redirects,
replacing the deprecated out-of-band flow.
"""

import asyncio
import webbrowser
from aiohttp import web
from typing import Optional, Callable
import logging

logger = logging.getLogger(__name__)


class OAuthRedirectServer:
    """Local server to handle OAuth redirect."""
    
    def __init__(self, port: int = 8080):
        self.port = port
        self.auth_code: Optional[str] = None
        self.error: Optional[str] = None
        self._callback: Optional[Callable] = None
        
    async def handle_oauth_redirect(self, request: web.Request) -> web.Response:
        """Handle the OAuth redirect from Google."""
        # Extract authorization code or error
        self.auth_code = request.rel_url.query.get('code')
        self.error = request.rel_url.query.get('error')
        
        if self.error:
            html = f"""
            <html>
            <body>
            <h1>Authorization Failed</h1>
            <p>Error: {self.error}</p>
            <p>You can close this window.</p>
            </body>
            </html>
            """
        elif self.auth_code:
            html = """
            <html>
            <body>
            <h1>Authorization Successful!</h1>
            <p>You have successfully authorized the application.</p>
            <p>You can close this window and return to the application.</p>
            </body>
            </html>
            """
        else:
            html = """
            <html>
            <body>
            <h1>Authorization Error</h1>
            <p>No authorization code received.</p>
            <p>You can close this window.</p>
            </body>
            </html>
            """
        
        # Notify callback if set
        if self._callback:
            await self._callback(self.auth_code, self.error)
        
        return web.Response(text=html, content_type='text/html')
    
    async def start_server(self, callback: Optional[Callable] = None) -> web.AppRunner:
        """Start the local redirect server."""
        self._callback = callback
        
        app = web.Application()
        app.router.add_get('/', self.handle_oauth_redirect)
        app.router.add_get('/callback', self.handle_oauth_redirect)
        
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, 'localhost', self.port)
        await site.start()
        
        logger.info(f"OAuth redirect server started on http://localhost:{self.port}")
        return runner
    
    @staticmethod
    async def run_oauth_flow(auth_url: str, port: int = 8080) -> Optional[str]:
        """
        Run the complete OAuth flow.
        
        Args:
            auth_url: The authorization URL from Google
            port: Local port for redirect server
            
        Returns:
            Authorization code or None if failed
        """
        server = OAuthRedirectServer(port)
        code_future = asyncio.Future()
        
        async def callback(code: Optional[str], error: Optional[str]):
            if error:
                code_future.set_exception(Exception(f"OAuth error: {error}"))
            else:
                code_future.set_result(code)
        
        # Start server
        runner = await server.start_server(callback)
        
        # Open browser
        logger.info(f"Opening browser for authorization: {auth_url}")
        webbrowser.open(auth_url)
        
        try:
            # Wait for authorization code
            auth_code = await asyncio.wait_for(code_future, timeout=300)  # 5 minute timeout
            logger.info("Received authorization code")
            return auth_code
        except asyncio.TimeoutError:
            logger.error("OAuth flow timed out")
            return None
        except Exception as e:
            logger.error(f"OAuth flow error: {e}")
            return None
        finally:
            # Stop server
            await runner.cleanup()
            logger.info("OAuth redirect server stopped")