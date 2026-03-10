# Examples

This directory contains example scripts demonstrating how to use Flagsmith's features.

## Basic Feature Flags

The `basic_feature_flags.py` script demonstrates the simple feature flag API:

### Prerequisites

1. Install required dependencies:
   ```bash
   pip install requests
   ```

2. Ensure Flagsmith is running (e.g., `http://localhost:8000`)

3. Obtain an authentication token:
   - Log in to Flagsmith
   - Go to your user settings
   - Generate an API token

### Usage

1. Edit `basic_feature_flags.py` and update the configuration:
   ```python
   BASE_URL = "http://localhost:8000"
   AUTH_TOKEN = "your-auth-token-here"
   PROJECT_ID = 1
   DEV_ENVIRONMENT_ID = 1
   PROD_ENVIRONMENT_ID = 2
   ```

2. Run the script:
   ```bash
   python examples/basic_feature_flags.py
   ```

### What the Script Does

The script demonstrates a complete feature flag workflow:

1. Creates a new feature flag
2. Enables it in the development environment
3. Checks the status in both development and production
4. Enables it in production
5. Lists all features in the project
6. Gets all feature states across environments
7. Disables the feature in production

### Expected Output

```
=== Feature Flag API Example ===

1. Creating a new feature...
   ✓ Created feature: example_feature (ID: 123)

2. Enabling feature in development environment...
   ✓ Feature 'example_feature' enabled in Development

3. Checking feature status in development...
   ✓ Feature 'example_feature' in Development: ENABLED

4. Checking feature status in production...
   ✓ Feature 'example_feature' in Production: DISABLED

5. Enabling feature in production environment...
   ✓ Feature 'example_feature' enabled in Production

6. Listing all features in project...
   ✓ Found 3 feature(s):
      - example_feature: This is an example feature flag
      - feature_a: Description
      - feature_b: Description

7. Getting all feature states for project...
   ✓ Found 6 feature state(s):
      - example_feature in Development: ENABLED
      - example_feature in Production: ENABLED
      - feature_a in Development: DISABLED
      - feature_a in Production: DISABLED
      - feature_b in Development: ENABLED
      - feature_b in Production: DISABLED

8. Disabling feature in production...
   ✓ Feature 'example_feature' disabled in Production

=== Example Complete ===
```

## Using as a Library

You can also import and use the `FeatureFlagClient` class in your own scripts:

```python
from examples.basic_feature_flags import FeatureFlagClient

client = FeatureFlagClient("http://localhost:8000", "your-token")

# Create a feature
feature = client.create_feature(
    name="my_feature",
    project_id=1,
    description="My feature description"
)

# Toggle it
client.toggle_feature(
    feature_id=feature["id"],
    environment_id=1,
    enabled=True
)

# Check status
status = client.get_feature_status(
    feature_id=feature["id"],
    environment_id=1
)
print(f"Feature is {'enabled' if status['enabled'] else 'disabled'}")
```

## Additional Resources

- [Feature Flags Documentation](../FEATURE_FLAGS.md)
- [API Documentation](../api/README.md)
- [Flagsmith SDK Documentation](https://docs.flagsmith.com/)
