# Feature Flags Quick Reference

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/features/simple/create/` | POST | Create feature |
| `/api/v1/features/simple/toggle/` | POST | Enable/disable |
| `/api/v1/features/simple/status/` | GET | Check status |
| `/api/v1/features/simple/list/` | GET | List features |

## Quick Examples

### Create Feature
```bash
curl -X POST $BASE_URL/api/v1/features/simple/create/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"my_feature","project_id":1}'
```

### Enable Feature
```bash
curl -X POST $BASE_URL/api/v1/features/simple/toggle/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"feature_id":1,"environment_id":1,"enabled":true}'
```

### Check Status
```bash
curl -X GET "$BASE_URL/api/v1/features/simple/status/?feature_id=1&environment_id=1" \
  -H "Authorization: Token $TOKEN"
```

### List Features
```bash
curl -X GET "$BASE_URL/api/v1/features/simple/list/?project_id=1" \
  -H "Authorization: Token $TOKEN"
```

## Python Client

```python
from examples.basic_feature_flags import FeatureFlagClient

client = FeatureFlagClient("http://localhost:8000", "your-token")

# Create
feature = client.create_feature("my_feature", project_id=1)

# Toggle
client.toggle_feature(feature["id"], environment_id=1, enabled=True)

# Status
status = client.get_feature_status(feature["id"], environment_id=1)
print(f"Enabled: {status['enabled']}")
```

## Management Command

```bash
# Run demo
python manage.py demo_feature_flags
```

## Testing

```bash
# Run tests
make test opts="tests/integration/features/test_simple_feature_flags.py"
make test opts="tests/unit/features/test_unit_simple_feature_flags.py"
```

## Common Patterns

### Development → Production Flow
```bash
# 1. Create feature (disabled by default)
curl -X POST .../create/ -d '{"name":"feature","project_id":1}'

# 2. Enable in dev
curl -X POST .../toggle/ -d '{"feature_id":1,"environment_id":1,"enabled":true}'

# 3. Test in dev
# ... test your feature ...

# 4. Enable in prod
curl -X POST .../toggle/ -d '{"feature_id":1,"environment_id":2,"enabled":true}'
```

### Emergency Disable
```bash
# Quickly disable in production
curl -X POST $BASE_URL/api/v1/features/simple/toggle/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"feature_id":1,"environment_id":2,"enabled":false}'
```

### Check All Features
```bash
# Get overview of all features across environments
curl -X GET "$BASE_URL/api/v1/features/simple/status/?project_id=1" \
  -H "Authorization: Token $TOKEN"
```

## Response Formats

### Create Response
```json
{
  "id": 1,
  "name": "feature_name",
  "description": "Description",
  "project_id": 1,
  "default_enabled": false,
  "message": "Feature 'feature_name' created successfully"
}
```

### Toggle Response
```json
{
  "feature_id": 1,
  "feature_name": "feature_name",
  "environment_id": 1,
  "environment_name": "Development",
  "enabled": true,
  "message": "Feature 'feature_name' enabled in Development"
}
```

### Status Response
```json
{
  "feature_id": 1,
  "feature_name": "feature_name",
  "environment_id": 1,
  "environment_name": "Development",
  "enabled": true,
  "description": "Feature description"
}
```

## Error Codes

| Code | Meaning |
|------|---------|
| 400 | Bad request (validation error) |
| 401 | Unauthorised (no/invalid token) |
| 404 | Resource not found |
| 200 | Success |
| 201 | Created |

## Best Practices

✅ **DO:**
- Use descriptive feature names (`new_checkout`, not `feature1`)
- Test in dev before enabling in prod
- Document feature flags
- Clean up old flags

❌ **DON'T:**
- Use special characters in names
- Enable untested features in prod
- Leave flags enabled indefinitely
- Create duplicate feature names

## Documentation

- Full guide: `FEATURE_FLAGS.md`
- Implementation details: `IMPLEMENTATION_SUMMARY.md`
- Examples: `examples/README.md`

## Getting Help

1. Check the full documentation
2. Run the demo command
3. Review example scripts
4. Check test files for usage patterns
