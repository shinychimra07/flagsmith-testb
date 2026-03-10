#!/usr/bin/env python
"""
Example script demonstrating how to use the basic feature flag API.

This script shows how to:
1. Create a feature
2. Enable/disable it in different environments
3. Check feature status

Requirements:
- requests library: pip install requests
- A running Flagsmith instance
- Valid authentication token
"""

import requests
import sys


class FeatureFlagClient:
    """Simple client for the basic feature flag API."""

    def __init__(self, base_url: str, auth_token: str):
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "Authorization": f"Token {auth_token}",
            "Content-Type": "application/json",
        }

    def create_feature(
        self, name: str, project_id: int, description: str = "", default_enabled: bool = False
    ) -> dict:  # type: ignore[type-arg]
        """Create a new feature flag."""
        url = f"{self.base_url}/api/v1/features/simple/create/"
        data = {
            "name": name,
            "description": description,
            "project_id": project_id,
            "default_enabled": default_enabled,
        }
        response = requests.post(url, json=data, headers=self.headers)
        response.raise_for_status()
        return response.json()  # type: ignore[no-any-return]

    def toggle_feature(
        self, feature_id: int, environment_id: int, enabled: bool
    ) -> dict:  # type: ignore[type-arg]
        """Enable or disable a feature in an environment."""
        url = f"{self.base_url}/api/v1/features/simple/toggle/"
        data = {
            "feature_id": feature_id,
            "environment_id": environment_id,
            "enabled": enabled,
        }
        response = requests.post(url, json=data, headers=self.headers)
        response.raise_for_status()
        return response.json()  # type: ignore[no-any-return]

    def get_feature_status(
        self, feature_id: int = None, environment_id: int = None, project_id: int = None  # type: ignore[assignment]
    ) -> dict:  # type: ignore[type-arg]
        """Get feature status."""
        url = f"{self.base_url}/api/v1/features/simple/status/"
        params = {}
        if feature_id and environment_id:
            params = {"feature_id": feature_id, "environment_id": environment_id}
        elif project_id:
            params = {"project_id": project_id}
        else:
            raise ValueError("Provide either (feature_id, environment_id) or project_id")

        response = requests.get(url, params=params, headers=self.headers)
        response.raise_for_status()
        return response.json()  # type: ignore[no-any-return]

    def list_features(self, project_id: int) -> dict:  # type: ignore[type-arg]
        """List all features in a project."""
        url = f"{self.base_url}/api/v1/features/simple/list/"
        params = {"project_id": project_id}
        response = requests.get(url, params=params, headers=self.headers)
        response.raise_for_status()
        return response.json()  # type: ignore[no-any-return]


def main() -> None:
    """Run the example."""
    # Configuration - Update these values
    BASE_URL = "http://localhost:8000"
    AUTH_TOKEN = "your-auth-token-here"
    PROJECT_ID = 1
    DEV_ENVIRONMENT_ID = 1
    PROD_ENVIRONMENT_ID = 2

    if AUTH_TOKEN == "your-auth-token-here":
        print("Error: Please update AUTH_TOKEN in the script with your actual token")
        sys.exit(1)

    # Initialize client
    client = FeatureFlagClient(BASE_URL, AUTH_TOKEN)

    try:
        print("=== Feature Flag API Example ===\n")

        # 1. Create a feature
        print("1. Creating a new feature...")
        feature = client.create_feature(
            name="example_feature",
            project_id=PROJECT_ID,
            description="This is an example feature flag",
            default_enabled=False,
        )
        print(f"   ✓ Created feature: {feature['name']} (ID: {feature['id']})")
        feature_id = feature["id"]

        # 2. Enable in development
        print("\n2. Enabling feature in development environment...")
        result = client.toggle_feature(feature_id, DEV_ENVIRONMENT_ID, enabled=True)
        print(f"   ✓ {result['message']}")

        # 3. Check status in development
        print("\n3. Checking feature status in development...")
        status = client.get_feature_status(feature_id, DEV_ENVIRONMENT_ID)
        print(f"   ✓ Feature '{status['feature_name']}' in {status['environment_name']}: {'ENABLED' if status['enabled'] else 'DISABLED'}")

        # 4. Check status in production (should be disabled)
        print("\n4. Checking feature status in production...")
        status = client.get_feature_status(feature_id, PROD_ENVIRONMENT_ID)
        print(f"   ✓ Feature '{status['feature_name']}' in {status['environment_name']}: {'ENABLED' if status['enabled'] else 'DISABLED'}")

        # 5. Enable in production
        print("\n5. Enabling feature in production environment...")
        result = client.toggle_feature(feature_id, PROD_ENVIRONMENT_ID, enabled=True)
        print(f"   ✓ {result['message']}")

        # 6. Get all features in project
        print("\n6. Listing all features in project...")
        features = client.list_features(PROJECT_ID)
        print(f"   ✓ Found {features['count']} feature(s):")
        for f in features["results"]:
            print(f"      - {f['name']}: {f['description']}")

        # 7. Get all feature states for project
        print("\n7. Getting all feature states for project...")
        all_status = client.get_feature_status(project_id=PROJECT_ID)
        print(f"   ✓ Found {all_status['count']} feature state(s):")
        for state in all_status["results"]:
            status_text = "ENABLED" if state["enabled"] else "DISABLED"
            print(f"      - {state['feature_name']} in {state['environment_name']}: {status_text}")

        # 8. Disable feature in production
        print("\n8. Disabling feature in production...")
        result = client.toggle_feature(feature_id, PROD_ENVIRONMENT_ID, enabled=False)
        print(f"   ✓ {result['message']}")

        print("\n=== Example Complete ===\n")

    except requests.exceptions.HTTPError as e:
        print(f"\n✗ HTTP Error: {e}")
        if hasattr(e.response, "json"):
            print(f"   Details: {e.response.json()}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
