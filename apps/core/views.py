from django.http import HttpResponse
from django.views import View

class HomeView(View):
    def get(self, request, *args, **kwargs):
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>ALX Project Nexus</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    margin: 0;
                    padding: 20px;
                    background-color: #f5f5f5;
                }
                .container {
                    max-width: 1200px;
                    margin: 0 auto;
                    background: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                h1 {
                    color: #333;
                    text-align: center;
                }
                .api-info {
                    margin-top: 30px;
                    padding: 15px;
                    background-color: #f8f9fa;
                    border-radius: 4px;
                }
                .endpoints {
                    margin-top: 20px;
                }
                .endpoint {
                    background: #e9ecef;
                    padding: 10px;
                    margin: 10px 0;
                    border-radius: 4px;
                    font-family: monospace;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Welcome to ALX Project Nexus</h1>
                <p>This is the home page of the ALX Project Nexus API.</p>
                
                <div class="api-info">
                    <h2>API Endpoints</h2>
                    <div class="endpoints">
                        <div class="endpoint">
                            <strong>GET /api/v1/trending/</strong> - Get trending movies
                        </div>
                        <div class="endpoint">
                            <strong>GET /api/v1/movies/</strong> - Browse movies
                        </div>
                        <div class="endpoint">
                            <strong>GET /api/v1/movies/search/?q=query</strong> - Search for movies
                        </div>
                        <div class="endpoint">
                            <strong>POST /api/v1/auth/register/</strong> - Register a new user
                        </div>
                        <div class="endpoint">
                            <strong>POST /api/v1/auth/login/</strong> - Login and get JWT tokens
                        </div>
                    </div>
                </div>
                
                <div style="margin-top: 30px; text-align: center; color: #666;">
                    <p>For more information, please refer to the API documentation.</p>
                </div>
            </div>
        </body>
        </html>
        """
        return HttpResponse(html)
