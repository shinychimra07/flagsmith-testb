"""
Integration tests for basic feature flag functionality.

Tests the simple API views for creating features and toggling them per environment.
"""

import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestSimpleFeatureFlagAPI:
    """Test simple feature flag API endpoints."""

    def test_create_simple_feature__valid_data__creates_feature(
        self, admin_client, project  # type: ignore[no-untyped-def]
    ):
        # Given
        url = reverse("api-v1:features:create-simple-feature")
        data = {
            "name": "test_feature",
            "description": "Test feature description",
            "project_id": project,
            "default_enabled": False,
        }

        # When
        response = admin_client.post(url, data=data, format="json")

        # Then
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "test_feature"
        assert response.data["description"] == "Test feature description"
        assert response.data["default_enabled"] is False
        assert "id" in response.data

    def test_create_simple_feature__duplicate_name__returns_error(
        self, admin_client, project, feature  # type: ignore[no-untyped-def]
    ):
        # Given
        url = reverse("api-v1:features:create-simple-feature")
        data = {
            "name": feature.name,  # Using existing feature name
            "project_id": project,
        }

        # When
        response = admin_client.post(url, data=data, format="json")

        # Then
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response.data["error"]

    def test_create_simple_feature__invalid_project__returns_error(
        self, admin_client  # type: ignore[no-untyped-def]
    ):
        # Given
        url = reverse("api-v1:features:create-simple-feature")
        data = {
            "name": "test_feature",
            "project_id": 99999,  # Non-existent project
        }

        # When
        response = admin_client.post(url, data=data, format="json")

        # Then
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Project not found" in response.data["error"]

    def test_toggle_feature_state__enable_feature__updates_state(
        self, admin_client, feature, environment  # type: ignore[no-untyped-def]
    ):
        # Given
        url = reverse("api-v1:features:toggle-feature-state")
        data = {
            "feature_id": feature.id,
            "environment_id": environment.id,
            "enabled": True,
        }

        # When
        response = admin_client.post(url, data=data, format="json")

        # Then
        assert response.status_code == status.HTTP_200_OK
        assert response.data["enabled"] is True
        assert response.data["feature_name"] == feature.name
        assert "enabled" in response.data["message"].lower()

    def test_toggle_feature_state__disable_feature__updates_state(
        self, admin_client, feature, environment  # type: ignore[no-untyped-def]
    ):
        # Given
        url = reverse("api-v1:features:toggle-feature-state")
        data = {
            "feature_id": feature.id,
            "environment_id": environment.id,
            "enabled": False,
        }

        # When
        response = admin_client.post(url, data=data, format="json")

        # Then
        assert response.status_code == status.HTTP_200_OK
        assert response.data["enabled"] is False
        assert "disabled" in response.data["message"].lower()

    def test_toggle_feature_state__invalid_feature__returns_error(
        self, admin_client, environment  # type: ignore[no-untyped-def]
    ):
        # Given
        url = reverse("api-v1:features:toggle-feature-state")
        data = {
            "feature_id": 99999,  # Non-existent feature
            "environment_id": environment.id,
            "enabled": True,
        }

        # When
        response = admin_client.post(url, data=data, format="json")

        # Then
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Feature not found" in response.data["error"]

    def test_toggle_feature_state__invalid_environment__returns_error(
        self, admin_client, feature  # type: ignore[no-untyped-def]
    ):
        # Given
        url = reverse("api-v1:features:toggle-feature-state")
        data = {
            "feature_id": feature.id,
            "environment_id": 99999,  # Non-existent environment
            "enabled": True,
        }

        # When
        response = admin_client.post(url, data=data, format="json")

        # Then
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Environment not found" in response.data["error"]

    def test_get_feature_status__specific_feature__returns_status(
        self, admin_client, feature, environment  # type: ignore[no-untyped-def]
    ):
        # Given
        url = reverse("api-v1:features:get-feature-status")
        params = {"feature_id": feature.id, "environment_id": environment.id}

        # When
        response = admin_client.get(url, params)

        # Then
        assert response.status_code == status.HTTP_200_OK
        assert response.data["feature_id"] == feature.id
        assert response.data["feature_name"] == feature.name
        assert response.data["environment_id"] == environment.id
        assert "enabled" in response.data

    def test_get_feature_status__all_features_in_project__returns_all(
        self, admin_client, project, feature, environment  # type: ignore[no-untyped-def]
    ):
        # Given
        url = reverse("api-v1:features:get-feature-status")
        params = {"project_id": project}

        # When
        response = admin_client.get(url, params)

        # Then
        assert response.status_code == status.HTTP_200_OK
        assert "results" in response.data
        assert response.data["count"] >= 1
        assert any(
            result["feature_id"] == feature.id for result in response.data["results"]
        )

    def test_get_feature_status__no_parameters__returns_error(
        self, admin_client  # type: ignore[no-untyped-def]
    ):
        # Given
        url = reverse("api-v1:features:get-feature-status")

        # When
        response = admin_client.get(url)

        # Then
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Please provide" in response.data["error"]

    def test_list_simple_features__valid_project__returns_features(
        self, admin_client, project, feature  # type: ignore[no-untyped-def]
    ):
        # Given
        url = reverse("api-v1:features:list-simple-features")
        params = {"project_id": project}

        # When
        response = admin_client.get(url, params)

        # Then
        assert response.status_code == status.HTTP_200_OK
        assert "results" in response.data
        assert response.data["count"] >= 1
        feature_names = [f["name"] for f in response.data["results"]]
        assert feature.name in feature_names

    def test_list_simple_features__no_project_id__returns_error(
        self, admin_client  # type: ignore[no-untyped-def]
    ):
        # Given
        url = reverse("api-v1:features:list-simple-features")

        # When
        response = admin_client.get(url)

        # Then
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "project_id parameter is required" in response.data["error"]

    def test_list_simple_features__invalid_project__returns_error(
        self, admin_client  # type: ignore[no-untyped-def]
    ):
        # Given
        url = reverse("api-v1:features:list-simple-features")
        params = {"project_id": 99999}

        # When
        response = admin_client.get(url, params)

        # Then
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Project not found" in response.data["error"]


@pytest.mark.django_db
class TestFeatureFlagWorkflow:
    """Test complete feature flag workflow."""

    def test_complete_feature_flag_workflow(
        self, admin_client, project, environment  # type: ignore[no-untyped-def]
    ):
        """Test creating a feature and toggling it across environments."""
        # Given - Create a new feature
        create_url = reverse("api-v1:features:create-simple-feature")
        create_data = {
            "name": "workflow_test_feature",
            "description": "Testing complete workflow",
            "project_id": project,
            "default_enabled": False,
        }

        # When - Create feature
        create_response = admin_client.post(
            create_url, data=create_data, format="json"
        )

        # Then - Feature created successfully
        assert create_response.status_code == status.HTTP_201_CREATED
        feature_id = create_response.data["id"]

        # When - Check initial status
        status_url = reverse("api-v1:features:get-feature-status")
        status_params = {"feature_id": feature_id, "environment_id": environment.id}
        status_response = admin_client.get(status_url, status_params)

        # Then - Feature is initially disabled
        assert status_response.status_code == status.HTTP_200_OK
        assert status_response.data["enabled"] is False

        # When - Enable the feature
        toggle_url = reverse("api-v1:features:toggle-feature-state")
        toggle_data = {
            "feature_id": feature_id,
            "environment_id": environment.id,
            "enabled": True,
        }
        toggle_response = admin_client.post(
            toggle_url, data=toggle_data, format="json"
        )

        # Then - Feature is enabled
        assert toggle_response.status_code == status.HTTP_200_OK
        assert toggle_response.data["enabled"] is True

        # When - Check status again
        status_response_2 = admin_client.get(status_url, status_params)

        # Then - Feature remains enabled
        assert status_response_2.status_code == status.HTTP_200_OK
        assert status_response_2.data["enabled"] is True

        # When - Disable the feature
        toggle_data["enabled"] = False
        toggle_response_2 = admin_client.post(
            toggle_url, data=toggle_data, format="json"
        )

        # Then - Feature is disabled
        assert toggle_response_2.status_code == status.HTTP_200_OK
        assert toggle_response_2.data["enabled"] is False

        # When - List all features
        list_url = reverse("api-v1:features:list-simple-features")
        list_params = {"project_id": project}
        list_response = admin_client.get(list_url, list_params)

        # Then - Our feature is in the list
        assert list_response.status_code == status.HTTP_200_OK
        feature_names = [f["name"] for f in list_response.data["results"]]
        assert "workflow_test_feature" in feature_names
