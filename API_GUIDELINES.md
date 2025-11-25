# Movie API Documentation

## Table of Contents
- [API Endpoints](#api-endpoints)
  - [Movies](#movies)
  - [Trending](#trending)
  - [Popular](#popular)
  - [Search](#search)
- [Authentication](#authentication)
- [Pagination](#pagination)
- [Rate Limiting](#rate-limiting)
- [Error Handling](#error-handling)
- [Example Requests](#example-requests)
- [Response Format](#response-format)
- [Best Practices](#best-practices)

## API Endpoints

### Movies
- `GET /api/v1/movies/` - List all movies (paginated)
  - Query Params: `page`, `page_size`
- `GET /api/v1/movies/{tmdb_id}/` - Get movie details by TMDb ID
- `POST /api/v1/movies/{tmdb_id}/favorite/` - Add movie to favorites
  - Required Headers: `Authorization: Bearer <token>`
  - Request Body: `{"notes": "Optional notes about this favorite"}`
- `DELETE /api/v1/movies/{tmdb_id}/favorite/` - Remove movie from favorites
  - Required Headers: `Authorization: Bearer <token>`

### Trending
- `GET /api/v1/trending/` - Get trending movies (default: daily)
  - Query Params: 
    - `time_window`: `day` or `week` (default: `day`)
    - `page`: Page number (default: 1)
    - `language`: ISO 639-1 language code (e.g., `en-US`)

### Popular
- `GET /api/v1/popular/` - Get popular movies
  - Query Params:
    - `page`: Page number (default: 1)
    - `language`: ISO 639-1 language code
    - `region`: ISO 3166-1 region code

### Search
- `GET /api/v1/search/` - Search for movies
  - Required Query Params:
    - `query`: Search query string
  - Optional Query Params:
    - `page`: Page number (default: 1)
    - `include_adult`: Include adult content (default: false)
    - `year`: Filter by year of release
    - `language`: ISO 639-1 language code

## Authentication
- JWT token authentication is used for protected endpoints
- Include token in request headers: 
  ```
  Authorization: Bearer your_jwt_token_here
  ```
- To obtain a token:
  1. Register at `/api/auth/register/`
  2. Login at `/api/auth/login/`
  3. Use the returned `access` token in the Authorization header

## Pagination
All list endpoints return paginated results with the following structure:
```json
{
  "count": 100,
  "next": "https://api.example.com/endpoint/?page=2",
  "previous": null,
  "results": [
    // Array of items
  ]
}
```

## Rate Limiting
- Public endpoints: 100 requests per minute per IP
- Authenticated endpoints: 1000 requests per minute per user
- Headers included in rate-limited responses:
  - `X-RateLimit-Limit`: Request limit per time window
  - `X-RateLimit-Remaining`: Remaining requests in current window
  - `X-RateLimit-Reset`: Time when the rate limit resets (UTC timestamp)

## Error Handling
Standard HTTP status codes are used:
- `200 OK`: Successful request
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

Error responses include a JSON object with error details:
```json
{
  "error": {
    "code": "error_code",
    "message": "Human-readable error message",
    "details": {
      // Additional error details
    }
  }
}
```

## Example Requests

### Get Trending Movies
```http
GET /api/v1/trending/?time_window=week&page=1
Authorization: Bearer your_jwt_token_here
Accept: application/json
```

### Search for Movies
```http
GET /api/v1/search/?query=inception&page=1&language=en-US
Authorization: Bearer your_jwt_token_here
Accept: application/json
```

### Add Movie to Favorites
```http
POST /api/v1/movies/12345/favorite/
Authorization: Bearer your_jwt_token_here
Content-Type: application/json

{
  "notes": "One of my favorite movies!"
}
```

## Response Format
All successful responses are in JSON format with the following structure:
```json
{
  "data": {
    // Response data
  },
  "meta": {
    "timestamp": "2023-11-23T12:00:00Z",
    "version": "1.0"
  }
}
```

## Best Practices

### Caching
- Responses are cached based on user authentication status
- Public data: 15 minutes cache
- Authenticated data: 5 minutes cache
- Cache is automatically invalidated on data modification

### Security
- Always use HTTPS
- Never expose API keys in client-side code
- Validate all user input
- Use environment variables for sensitive data

### Performance
- Implemented query optimization
- Database indexes for frequently queried fields
- Selective field loading
- Connection pooling for database connections

### Development
- Include detailed logging
- Comprehensive test coverage
- API versioning in URL
- Consistent error handling
- Detailed API documentation (this document)

## Versioning
API versioning is handled through the URL path (e.g., `/api/v1/...`).

## Support
For support, please contact [support@example.com](mailto:support@example.com) or visit our [developer portal](https://developer.example.com).
