# Services API Documentation

## Overview

The Services API provides comprehensive functionality for managing services offered by providers in the Banister platform. This module allows providers to create, update, and manage their services, while customers can browse and search through available services.

## Base URL

```
/api/v1/services/
```

## Authentication

All endpoints that modify data (POST, PUT, PATCH, DELETE) require authentication. Use JWT tokens in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

## User Roles

- **provider**: Can create, update, and delete their own services
- **customer**: Can view and search services (read-only access)
- **management**: Can view all services (read-only access)

## API Endpoints

### 1. Create Service

**POST** `/api/v1/services/`

Creates a new service. Only providers can create services.

**Request Body:**
```json
{
    "title": "Web Development",
    "description": "Professional web development services including frontend and backend development",
    "price": 150.00
}
```

**Required Fields:**
- `title` (string, max 100 characters): Service title
- `description` (text): Detailed service description
- `price` (decimal): Service price with up to 2 decimal places

**Response (201 Created):**
```json
{
    "success": true,
    "message": "Service created successfully",
    "data": {
        "id": 1,
        "provider_id": 5,
        "title": "Web Development",
        "description": "Professional web development services including frontend and backend development",
        "price": "150.00",
        "created_at": "2024-01-15T10:30:00Z"
    }
}
```

**Error Responses:**
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Only providers can create services
- `400 Bad Request`: Validation errors

### 2. List Services

**GET** `/api/v1/services/`

Retrieves a list of all available services with optional filtering and search.

**Query Parameters:**
- `search` (optional): Search in title and description fields
- `ordering` (optional): Sort by `price` or `created_at` (use `-` prefix for descending)
- `page` (optional): Page number for pagination
- `page_size` (optional): Number of items per page

**Example Requests:**
```
GET /api/v1/services/?search=web&ordering=-price
GET /api/v1/services/?ordering=created_at
GET /api/v1/services/?page=1&page_size=10
```

**Response (200 OK):**
```json
{
    "success": true,
    "message": "List of services obtained successfully",
    "data": [
        {
            "id": 1,
            "provider_id": 5,
            "title": "Web Development",
            "description": "Professional web development services",
            "price": "150.00",
            "created_at": "2024-01-15T10:30:00Z"
        },
        {
            "id": 2,
            "provider_id": 7,
            "title": "Mobile App Development",
            "description": "iOS and Android app development",
            "price": "200.00",
            "created_at": "2024-01-14T15:20:00Z"
        }
    ]
}
```

### 3. Get Service Details

**GET** `/api/v1/services/{id}/`

Retrieves detailed information about a specific service.

**Response (200 OK):**
```json
{
    "success": true,
    "message": "Service information obtained successfully",
    "data": {
        "id": 1,
        "provider_id": 5,
        "title": "Web Development",
        "description": "Professional web development services including frontend and backend development",
        "price": "150.00",
        "created_at": "2024-01-15T10:30:00Z"
    }
}
```

**Error Responses:**
- `404 Not Found`: Service not found

### 4. Update Service

**PUT** `/api/v1/services/{id}/`

Updates a service completely. Only the service owner can update it.

**Request Body:**
```json
{
    "title": "Updated Web Development",
    "description": "Updated web development services with modern technologies",
    "price": 175.00
}
```

**Response (200 OK):**
```json
{
    "success": true,
    "message": "Service updated successfully",
    "data": {
        "id": 1,
        "provider_id": 5,
        "title": "Updated Web Development",
        "description": "Updated web development services with modern technologies",
        "price": "175.00",
        "created_at": "2024-01-15T10:30:00Z"
    }
}
```

**Error Responses:**
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: No permission to update this service
- `404 Not Found`: Service not found
- `400 Bad Request`: Validation errors

### 5. Partial Update Service

**PATCH** `/api/v1/services/{id}/`

Partially updates a service. Only the service owner can update it.

**Request Body:**
```json
{
    "price": 180.00
}
```

**Response (200 OK):**
```json
{
    "success": true,
    "message": "Service updated successfully",
    "data": {
        "id": 1,
        "provider_id": 5,
        "title": "Updated Web Development",
        "description": "Updated web development services with modern technologies",
        "price": "180.00",
        "created_at": "2024-01-15T10:30:00Z"
    }
}
```

**Error Responses:**
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: No permission to update this service
- `404 Not Found`: Service not found
- `400 Bad Request`: Validation errors

### 6. Delete Service

**DELETE** `/api/v1/services/{id}/`

Deletes a service. Only the service owner can delete it.

**Response (200 OK):**
```json
{
    "success": true,
    "message": "Service deleted successfully"
}
```

**Error Responses:**
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: No permission to delete this service
- `404 Not Found`: Service not found

## Data Models

### Service Model

```python
class Service(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    provider = models.ForeignKey(User, on_delete=models.CASCADE, related_name='services')
    title = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
```

**Fields:**
- `id`: Primary key (auto-generated)
- `created_at`: Timestamp when service was created
- `provider`: Foreign key to User model (service owner)
- `title`: Service title (max 100 characters)
- `description`: Service description (unlimited text)
- `price`: Service price (decimal with 2 decimal places)

## Error Handling

All endpoints use the standardized error response format:

```json
{
    "success": false,
    "error_number": "ERROR_CODE",
    "error_message": "Human-readable error message"
}
```

**Common Error Codes:**
- `AUTHENTICATION_REQUIRED`: User not authenticated
- `PERMISSION_DENIED`: User lacks required permissions
- `SERVICE_NOT_FOUND`: Service with specified ID not found
- `SERVICE_CREATE_ERROR`: Error creating service
- `SERVICE_UPDATE_ERROR`: Error updating service
- `SERVICE_DELETE_ERROR`: Error deleting service
- `SERVICE_LIST_ERROR`: Error retrieving service list
- `SERVICE_RETRIEVE_ERROR`: Error retrieving service details

## Search and Filtering

### Search Functionality
- Search is performed across `title` and `description` fields
- Case-insensitive partial matching
- Multiple words are supported

### Ordering Options
- `price`: Sort by price (ascending)
- `-price`: Sort by price (descending)
- `created_at`: Sort by creation date (ascending)
- `-created_at`: Sort by creation date (descending)

## Security Features

1. **Authentication Required**: All write operations require valid JWT token
2. **Role-Based Access**: Only providers can create/update/delete services
3. **Ownership Validation**: Users can only modify their own services
4. **Input Validation**: All input data is validated before processing
5. **Database Transactions**: All write operations are wrapped in transactions

## Usage Examples

### For Providers

1. **Create a new service:**
```bash
curl -X POST http://localhost:8000/api/v1/services/ \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Graphic Design",
    "description": "Professional graphic design services",
    "price": 75.00
  }'
```

2. **Update your service:**
```bash
curl -X PUT http://localhost:8000/api/v1/services/1/ \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Graphic Design",
    "description": "Updated graphic design services",
    "price": 85.00
  }'
```

### For Customers

1. **Browse all services:**
```bash
curl -X GET http://localhost:8000/api/v1/services/
```

2. **Search for specific services:**
```bash
curl -X GET "http://localhost:8000/api/v1/services/?search=design&ordering=-price"
```

3. **Get service details:**
```bash
curl -X GET http://localhost:8000/api/v1/services/1/
```

## Integration Notes

- Services are automatically linked to the authenticated provider when created
- All timestamps are in UTC format
- Price values are stored as decimal numbers with 2 decimal places
- The API supports CORS for frontend integration
- All responses include standardized success/error indicators

## Testing

The API includes comprehensive Swagger documentation available at:
```
http://localhost:8000/swagger/
```

This provides an interactive interface for testing all endpoints with proper authentication and request/response examples. 