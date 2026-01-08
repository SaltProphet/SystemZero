# System//Zero API Reference

Version: 0.7.0

## Endpoints

### /

- **GET**: Root
  - Responses:
- 200: Successful Response

### /auth/keys

- **GET**: List Keys
  - Parameters:
- api_key (query, object, optional): 
  - Responses:
- 200: Successful Response
- 422: Validation Error

### /auth/token

- **POST**: Create Token
  - Parameters:
- api_key (query, object, optional): 
  - Request Body:
- media: application/json (required)
  - Responses:
- 200: Successful Response
- 422: Validation Error

### /auth/validate

- **POST**: Validate Token
  - Parameters:
- api_key (query, object, optional): 
  - Responses:
- 200: Successful Response
- 422: Validation Error

### /captures

- **POST**: Create Capture
  - Parameters:
- api_key (query, object, optional): 
  - Request Body:
- media: application/json (required)
  - Responses:
- 200: Successful Response
- 422: Validation Error

### /dashboard

- **GET**: Get Dashboard Data
  - Responses:
- 200: Successful Response

### /health

- **GET**: Health Check
  - Responses:
- 200: Successful Response

### /logs

- **GET**: Get Logs
  - Parameters:
- limit (query, integer, optional): 
- offset (query, integer, optional): 
  - Responses:
- 200: Successful Response
- 422: Validation Error

### /logs/export

- **GET**: Export Logs
  - Parameters:
- format (query, string, optional): 
  - Responses:
- 200: Successful Response
- 422: Validation Error

### /metrics

- **GET**: Get Metrics Endpoint
  - Responses:
- 200: Successful Response

### /openapi.yaml

- **GET**: Openapi Yaml
  - Responses:
- 200: Successful Response

### /status

- **GET**: Get Status
  - Responses:
- 200: Successful Response

### /templates

- **GET**: List Templates
  - Responses:
- 200: Successful Response
- **POST**: Build Template
  - Parameters:
- capture_path (query, string, required): 
- screen_id (query, string, required): 
- app (query, string, optional): 
- api_key (query, object, optional): 
  - Responses:
- 200: Successful Response
- 422: Validation Error

### /templates/{screen_id}

- **GET**: Get Template
  - Parameters:
- screen_id (path, string, required): 
  - Responses:
- 200: Successful Response
- 422: Validation Error

