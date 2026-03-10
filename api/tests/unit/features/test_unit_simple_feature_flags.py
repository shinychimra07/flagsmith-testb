"""
Unit tests for basic feature flag views and serialisers.
"""

import pytest
from rest_framework.exceptions import ValidationError

from features.simple_views import (
    FeatureStateToggleSerializer,
    SimpleFeatureSerializer,
)


class TestSimpleFeatureSerializer:
    """Test the SimpleFeatureSerializer."""

    def test_valid_data__serializer_is_valid(self):  # type: ignore[no-untyped-def]
        # Given
        data = {
            "name": "test_feature",
            "description": "Test description",
            "project_id": 1,
            "default_enabled": False,
        }

        # When
        serializer = SimpleFeatureSerializer(data=data)

        # Then
        assert serializer.is_valid()
        assert serializer.validated_data["name"] == "test_feature"
        assert serializer.validated_data["description"] == "Test description"
        assert serializer.validated_data["project_id"] == 1
        assert serializer.validated_data["default_enabled"] is False

    def test_missing_required_field__serializer_invalid(self):  # type: ignore[no-untyped-def]
        # Given
        data = {
            "description": "Test description",
            # Missing 'name' and 'project_id'
        }

        # When
        serializer = SimpleFeatureSerializer(data=data)

        # Then
        assert not serializer.is_valid()
        assert "name" in serializer.errors
        assert "project_id" in serializer.errors

    def test_optional_fields__serializer_valid(self):  # type: ignore[no-untyped-def]
        # Given
        data = {
            "name": "test_feature",
            "project_id": 1,
            # 'description' and 'default_enabled' are optional
        }

        # When
        serializer = SimpleFeatureSerializer(data=data)

        # Then
        assert serializer.is_valid()
        assert serializer.validated_data["name"] == "test_feature"
        assert serializer.validated_data["project_id"] == 1
        assert serializer.validated_data.get("description", "") == ""
        assert serializer.validated_data.get("default_enabled", False) is False


class TestFeatureStateToggleSerializer:
    """Test the FeatureStateToggleSerializer."""

    def test_valid_data__serializer_is_valid(self):  # type: ignore[no-untyped-def]
        # Given
        data = {
            "feature_id": 1,
            "environment_id": 1,
            "enabled": True,
        }

        # When
        serializer = FeatureStateToggleSerializer(data=data)

        # Then
        assert serializer.is_valid()
        assert serializer.validated_data["feature_id"] == 1
        assert serializer.validated_data["environment_id"] == 1
        assert serializer.validated_data["enabled"] is True

    def test_disable_feature__serializer_valid(self):  # type: ignore[no-untyped-def]
        # Given
        data = {
            "feature_id": 1,
            "environment_id": 1,
            "enabled": False,
        }

        # When
        serializer = FeatureStateToggleSerializer(data=data)

        # Then
        assert serializer.is_valid()
        assert serializer.validated_data["enabled"] is False

    def test_missing_required_fields__serializer_invalid(self):  # type: ignore[no-untyped-def]
        # Given
        data = {
            "feature_id": 1,
            # Missing 'environment_id' and 'enabled'
        }

        # When
        serializer = FeatureStateToggleSerializer(data=data)

        # Then
        assert not serializer.is_valid()
        assert "environment_id" in serializer.errors
        assert "enabled" in serializer.errors

    def test_invalid_data_types__serializer_invalid(self):  # type: ignore[no-untyped-def]
        # Given
        data = {
            "feature_id": "not_an_integer",
            "environment_id": 1,
            "enabled": "not_a_boolean",
        }

        # When
        serializer = FeatureStateToggleSerializer(data=data)

        # Then
        assert not serializer.is_valid()
        assert "feature_id" in serializer.errors
        assert "enabled" in serializer.errors


@pytest.mark.django_db
class TestFeatureFlagLogic:
    """Test feature flag business logic."""

    def test_feature_creation__creates_feature_states_automatically(
        self, project, environment  # type: ignore[no-untyped-def]
    ):
        """Test that creating a feature automatically creates feature states."""
        # Given
        from features.models import Feature, FeatureState

        initial_feature_state_count = FeatureState.objects.count()

        # When - Create a feature
        feature = Feature.objects.create(
            name="auto_feature_state_test",
            project=project,
            default_enabled=False,
        )

        # Then - Feature states should be created automatically
        feature_states = FeatureState.objects.filter(feature=feature)
        assert feature_states.count() > 0

        # Verify feature state was created for the environment
        environment_feature_state = FeatureState.objects.filter(
            feature=feature,
            environment=environment,
            identity__isnull=True,
            feature_segment__isnull=True,
        ).first()
        assert environment_feature_state is not None
        assert environment_feature_state.enabled == feature.default_enabled

    def test_feature_state_toggle__changes_enabled_status(
        self, feature, environment  # type: ignore[no-untyped-def]
    ):
        """Test that toggling a feature state changes its enabled status."""
        # Given
        from features.models import FeatureState

        feature_state = FeatureState.objects.filter(
            feature=feature,
            environment=environment,
            identity__isnull=True,
            feature_segment__isnull=True,
        ).first()

        initial_enabled = feature_state.enabled

        # When
        feature_state.enabled = not initial_enabled
        feature_state.save()

        # Then
        feature_state.refresh_from_db()
        assert feature_state.enabled != initial_enabled

    def test_multiple_environments__feature_states_independent(
        self, feature, project  # type: ignore[no-untyped-def]
    ):
        """Test that feature states are independent across environments."""
        # Given
        from environments.models import Environment
        from features.models import FeatureState

        env1 = Environment.objects.filter(project=project).first()
        env2 = Environment.objects.create(
            name="Test Environment 2",
            project=project,
        )

        # When - Enable in env1, disable in env2
        fs1 = FeatureState.objects.filter(
            feature=feature,
            environment=env1,
            identity__isnull=True,
            feature_segment__isnull=True,
        ).first()
        fs1.enabled = True
        fs1.save()

        fs2 = FeatureState.objects.filter(
            feature=feature,
            environment=env2,
            identity__isnull=True,
            feature_segment__isnull=True,
        ).first()
        fs2.enabled = False
        fs2.save()

        # Then - States should be independent
        fs1.refresh_from_db()
        fs2.refresh_from_db()
        assert fs1.enabled is True
        assert fs2.enabled is False
