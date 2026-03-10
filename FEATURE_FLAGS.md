# Basic Feature Flag Functionality

This document describes the basic feature flag functionality added to Flagsmith, providing simple APIs for creating features and enabling/disabling them per environment.

## Overview

The basic feature flag functionality includes:

1. **Simple API Endpoints** - Easy-to-use REST API endpoints for common feature flag operations
2. **Management Command** - A demo command to showcase feature flag creation and management
3. **Comprehensive Tests** - Full test coverage for all functionality

## Quick Start

### Using the Management Command

Run the demo to see feature flags in action:

```bash
python manage.py demo_feature_flags
```

This command will:
- Create a demo organisation and project
- Create development and production environments
- Create three feature flags: `new_dashboard`, `beta_features`, and `dark_mode`
- Configure different states for each environment
- Display the API keys for testing

### Using the API Endpoints

All endpoints require authentication and are prefixed with `/api/v1/features/simple/`.

#### 1. Create a Feature

```bash
POST /api/v1/features/simple/create/
Content-Type: application/json

{
  "name": "new_feature",
  "description": "Description of the feature",
  "project_id": 1,
  "default_enabled": false
}
```

**Response:**
```json
{
  "id": 1,
  "name": "new_feature",
  "description": "Description of the feature",
  "project_id": 1,
  "default_enabled": false,
  "message": "Feature 'new_feature' created successfully"
}
```

#### 2. Enable/Disable a Feature

```bash
POST /api/v1/features/simple/toggle/
Content-Type: application/json

{
  "feature_id": 1,
  "environment_id": 1,
  "enabled": true
}
```

**Response:**
```json
{
  "feature_id": 1,
  "feature_name": "new_feature",
  "environment_id": 1,
  "environment_name": "Development",
  "enabled": true,
  "message": "Feature 'new_feature' enabled in Development"
}
```

#### 3. Check Feature Status

**Get specific feature status:**
```bash
GET /api/v1/features/simple/status/?feature_id=1&environment_id=1
```

**Response:**
```json
{
  "feature_id": 1,
  "feature_name": "new_feature",
  "environment_id": 1,
  "environment_name": "Development",
  "enabled": true,
  "description": "Description of the feature"
}
```

**Get all features for a project:**
```bash
GET /api/v1/features/simple/status/?project_id=1
```

**Response:**
```json
{
  "results": [
    {
      "feature_id": 1,
      "feature_name": "new_feature",
      "environment_id": 1,
      "environment_name": "Development",
      "enabled": true,
      "description": "Description of the feature"
    },
    {
      "feature_id": 1,
      "feature_name": "new_feature",
      "environment_id": 2,
      "environment_name": "Production",
      "enabled": false,
      "description": "Description of the feature"
    }
  ],
  "count": 2
}
```

#### 4. List All Features

```bash
GET /api/v1/features/simple/list/?project_id=1
```

**Response:**
```json
{
  "results": [
    {
      "id": 1,
      "name": "new_feature",
      "description": "Description of the feature",
      "default_enabled": false,
      "is_archived": false,
      "created_date": "2026-03-09T10:30:00Z"
    }
  ],
  "count": 1
}
```

## Architecture

### Models

The functionality uses existing Flagsmith models:

- **Feature** - Represents a feature flag
- **FeatureState** - Represents the state of a feature in a specific environment
- **Environment** - Represents different deployment environments (dev, staging, production)
- **Project** - Groups features and environments together

### API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/features/simple/create/` | POST | Create a new feature |
| `/api/v1/features/simple/toggle/` | POST | Enable/disable a feature |
| `/api/v1/features/simple/status/` | GET | Get feature status |
| `/api/v1/features/simple/list/` | GET | List all features |

### Files Created

```
api/
├── features/
│   ├── management/
│   │   └── commands/
│   │       └── demo_feature_flags.py
│   ├── simple_views.py
│   └── urls.py (modified)
├── tests/
│   └── integration/
│       └── features/
│           └── test_simple_feature_flags.py
└── FEATURE_FLAGS.md (this file)
```

## Testing

Run the tests:

```bash
# Run all tests
make test

# Run specific test file
pytest api/tests/integration/features/test_simple_feature_flags.py

# Run with coverage
pytest --cov=api/features api/tests/integration/features/test_simple_feature_flags.py
```

## Use Cases

### Use Case 1: Feature Development

1. Create a feature flag for your new feature
2. Enable it in development environment only
3. Test the feature
4. When ready, enable in production

```bash
# Create feature
curl -X POST http://localhost:8000/api/v1/features/simple/create/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "new_checkout", "project_id": 1, "description": "New checkout flow"}'

# Enable in development
curl -X POST http://localhost:8000/api/v1/features/simple/toggle/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"feature_id": 1, "environment_id": 1, "enabled": true}'

# Later, enable in production
curl -X POST http://localhost:8000/api/v1/features/simple/toggle/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"feature_id": 1, "environment_id": 2, "enabled": true}'
```

### Use Case 2: A/B Testing

Create feature flags for different variations and enable them in specific environments for testing.

### Use Case 3: Emergency Kill Switch

Quickly disable a problematic feature in production without deploying code:

```bash
curl -X POST http://localhost:8000/api/v1/features/simple/toggle/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"feature_id": 1, "environment_id": 2, "enabled": false}'
```

## Integration with Flagsmith SDK

After creating and configuring features through the simple API, you can use them with the Flagsmith SDK in your application:

```python
from flagsmith import Flagsmith

flagsmith = Flagsmith(environment_key="YOUR_ENVIRONMENT_KEY")

# Check if feature is enabled
if flagsmith.is_feature_enabled("new_checkout"):
    # Show new checkout flow
    pass
else:
    # Show old checkout flow
    pass
```

## Error Handling

All endpoints return appropriate HTTP status codes:

- `200 OK` - Successful operation
- `201 Created` - Feature created successfully
- `400 Bad Request` - Invalid input data
- `404 Not Found` - Resource not found
- `401 Unauthorized` - Authentication required

Error responses include a descriptive message:

```json
{
  "error": "Feature not found"
}
```

## Best Practices

1. **Naming Convention** - Use descriptive, lowercase names with underscores (e.g., `new_dashboard`, `beta_feature`)
2. **Default State** - Start with features disabled by default
3. **Environment Progression** - Enable features in development first, then staging, finally production
4. **Cleanup** - Archive features that are no longer needed
5. **Documentation** - Use the description field to document what the feature flag controls

## Future Enhancements

Potential additions to the basic feature flag functionality:

- Bulk operations (enable/disable multiple features at once)
- Scheduled feature toggles
- Percentage rollouts
- User targeting
- Feature flag analytics
- Audit logging

## Related Documentation

- [Flagsmith Main Documentation](../README.md)
- [API Documentation](../api/README.md)
- [Testing Guidelines](../api/README.md#code-guidelines-testing)
