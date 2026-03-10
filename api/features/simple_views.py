"""
Simple API views for basic feature flag operations.

These views provide a simplified interface for:
- Creating features
- Enabling/disabling features per environment
- Setting feature values (string, number, or boolean)
- Checking feature status
"""

from rest_framework import serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from environments.models import Environment
from features.models import Feature, FeatureState
from features.value_types import BOOLEAN, INTEGER, STRING
from projects.models import Project


class SimpleFeatureSerializer(serializers.Serializer):  # type: ignore[type-arg]
    """Serialiser for creating simple features."""

    name = serializers.CharField(max_length=2000)
    description = serializers.CharField(required=False, allow_blank=True)
    project_id = serializers.IntegerField()
    default_enabled = serializers.BooleanField(default=False)


class FeatureStateToggleSerializer(serializers.Serializer):  # type: ignore[type-arg]
    """Serialiser for toggling feature states."""

    feature_id = serializers.IntegerField()
    environment_id = serializers.IntegerField()
    enabled = serializers.BooleanField()


class FeatureValueSerializer(serializers.Serializer):  # type: ignore[type-arg]
    """Serialiser for setting feature values."""

    feature_id = serializers.IntegerField()
    environment_id = serializers.IntegerField()
    value = serializers.CharField(allow_blank=True, allow_null=True, required=False)
    value_type = serializers.ChoiceField(
        choices=["string", "integer", "boolean"],
        default="string",
        required=False
    )


class FeatureStatusSerializer(serializers.Serializer):  # type: ignore[type-arg]
    """Serialiser for feature status response."""

    feature_id = serializers.IntegerField()
    feature_name = serializers.CharField()
    environment_id = serializers.IntegerField()
    environment_name = serializers.CharField()
    enabled = serializers.BooleanField()
    description = serializers.CharField()
    value = serializers.CharField(allow_null=True, required=False)
    value_type = serializers.CharField(allow_null=True, required=False)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_simple_feature(request):  # type: ignore[no-untyped-def]
    """
    Create a simple feature flag.

    POST /api/v1/features/simple/create/
    {
        "name": "feature_name",
        "description": "Feature description",
        "project_id": 1,
        "default_enabled": false
    }
    """
    serializer = SimpleFeatureSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data

    # Verify project exists and user has access
    try:
        project = Project.objects.get(id=data["project_id"])
    except Project.DoesNotExist:
        return Response(
            {"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND
        )

    # Check if feature already exists
    if Feature.objects.filter(
        name__iexact=data["name"], project=project
    ).exists():
        return Response(
            {"error": f"Feature '{data['name']}' already exists in this project"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Create feature
    feature = Feature.objects.create(
        name=data["name"],
        description=data.get("description", ""),
        project=project,
        default_enabled=data.get("default_enabled", False),
    )

    return Response(
        {
            "id": feature.id,
            "name": feature.name,
            "description": feature.description,
            "project_id": project.id,
            "default_enabled": feature.default_enabled,
            "message": f"Feature '{feature.name}' created successfully",
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def toggle_feature_state(request):  # type: ignore[no-untyped-def]
    """
    Enable or disable a feature in a specific environment.

    POST /api/v1/features/simple/toggle/
    {
        "feature_id": 1,
        "environment_id": 1,
        "enabled": true
    }
    """
    serializer = FeatureStateToggleSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data

    # Verify feature exists
    try:
        feature = Feature.objects.get(id=data["feature_id"])
    except Feature.DoesNotExist:
        return Response(
            {"error": "Feature not found"}, status=status.HTTP_404_NOT_FOUND
        )

    # Verify environment exists
    try:
        environment = Environment.objects.get(id=data["environment_id"])
    except Environment.DoesNotExist:
        return Response(
            {"error": "Environment not found"}, status=status.HTTP_404_NOT_FOUND
        )

    # Verify feature and environment belong to same project
    if feature.project_id != environment.project_id:
        return Response(
            {"error": "Feature and environment must belong to the same project"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Get or create feature state for this environment
    feature_state = FeatureState.objects.filter(
        feature=feature,
        environment=environment,
        identity__isnull=True,
        feature_segment__isnull=True,
    ).first()

    if not feature_state:
        return Response(
            {"error": "Feature state not found for this environment"},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Update enabled status
    feature_state.enabled = data["enabled"]
    feature_state.save()

    return Response(
        {
            "feature_id": feature.id,
            "feature_name": feature.name,
            "environment_id": environment.id,
            "environment_name": environment.name,
            "enabled": feature_state.enabled,
            "message": f"Feature '{feature.name}' {'enabled' if feature_state.enabled else 'disabled'} in {environment.name}",
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def set_feature_value(request):  # type: ignore[no-untyped-def]
    """
    Set a feature value in a specific environment.

    POST /api/v1/features/simple/set-value/
    {
        "feature_id": 1,
        "environment_id": 1,
        "value": "some_value",
        "value_type": "string"  // or "integer" or "boolean"
    }
    """
    serializer = FeatureValueSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data

    # Verify feature exists
    try:
        feature = Feature.objects.get(id=data["feature_id"])
    except Feature.DoesNotExist:
        return Response(
            {"error": "Feature not found"}, status=status.HTTP_404_NOT_FOUND
        )

    # Verify environment exists
    try:
        environment = Environment.objects.get(id=data["environment_id"])
    except Environment.DoesNotExist:
        return Response(
            {"error": "Environment not found"}, status=status.HTTP_404_NOT_FOUND
        )

    # Verify feature and environment belong to same project
    if feature.project_id != environment.project_id:
        return Response(
            {"error": "Feature and environment must belong to the same project"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Get feature state for this environment
    feature_state = FeatureState.objects.filter(
        feature=feature,
        environment=environment,
        identity__isnull=True,
        feature_segment__isnull=True,
    ).first()

    if not feature_state:
        return Response(
            {"error": "Feature state not found for this environment"},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Get or create feature state value
    try:
        feature_state_value = feature_state.feature_state_value
    except Exception:
        return Response(
            {"error": "Feature state value not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Set the value based on type
    value = data.get("value", "")
    value_type = data.get("value_type", "string")

    try:
        if value_type == "string":
            feature_state_value.type = STRING
            feature_state_value.string_value = value
            feature_state_value.integer_value = None
            feature_state_value.boolean_value = None
        elif value_type == "integer":
            try:
                int_value = int(value) if value else 0
            except ValueError:
                return Response(
                    {"error": f"'{value}' is not a valid integer"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            feature_state_value.type = INTEGER
            feature_state_value.integer_value = int_value
            feature_state_value.string_value = None
            feature_state_value.boolean_value = None
        elif value_type == "boolean":
            if value.lower() not in ("true", "false", "1", "0", ""):
                return Response(
                    {"error": f"'{value}' is not a valid boolean (use 'true' or 'false')"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            bool_value = value.lower() in ("true", "1")
            feature_state_value.type = BOOLEAN
            feature_state_value.boolean_value = bool_value
            feature_state_value.string_value = None
            feature_state_value.integer_value = None
        else:
            return Response(
                {"error": f"'{value_type}' is not a valid type (use 'string', 'integer', or 'boolean')"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        feature_state_value.save()

    except Exception as e:
        return Response(
            {"error": f"Failed to set value: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # Get the actual value for response
    actual_value = feature_state_value.value

    return Response(
        {
            "feature_id": feature.id,
            "feature_name": feature.name,
            "environment_id": environment.id,
            "environment_name": environment.name,
            "value": actual_value,
            "value_type": value_type,
            "message": f"Feature '{feature.name}' value set to '{actual_value}' ({value_type}) in {environment.name}",
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_feature_status(request):  # type: ignore[no-untyped-def]
    """
    Get the status of features across environments.

    GET /api/v1/features/simple/status/?feature_id=1&environment_id=1
    or
    GET /api/v1/features/simple/status/?project_id=1
    """
    feature_id = request.query_params.get("feature_id")
    environment_id = request.query_params.get("environment_id")
    project_id = request.query_params.get("project_id")

    if feature_id and environment_id:
        # Get specific feature state
        try:
            feature = Feature.objects.get(id=feature_id)
            environment = Environment.objects.get(id=environment_id)
        except (Feature.DoesNotExist, Environment.DoesNotExist):
            return Response(
                {"error": "Feature or environment not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        feature_state = FeatureState.objects.filter(
            feature=feature,
            environment=environment,
            identity__isnull=True,
            feature_segment__isnull=True,
        ).first()

        if not feature_state:
            return Response(
                {"error": "Feature state not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Get feature value information
        value = None
        value_type = None
        try:
            feature_state_value = feature_state.feature_state_value
            value = feature_state_value.value
            # Map internal type constants to user-friendly strings
            type_map = {STRING: "string", INTEGER: "integer", BOOLEAN: "boolean"}
            value_type = type_map.get(feature_state_value.type, "string")
        except Exception:
            pass

        return Response(
            {
                "feature_id": feature.id,
                "feature_name": feature.name,
                "environment_id": environment.id,
                "environment_name": environment.name,
                "enabled": feature_state.enabled,
                "description": feature.description or "",
                "value": value,
                "value_type": value_type,
            }
        )

    elif project_id:
        # Get all features and their states for a project
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response(
                {"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND
            )

        features = Feature.objects.filter(project=project)
        environments = Environment.objects.filter(project=project)

        results = []
        for feature in features:
            for environment in environments:
                feature_state = FeatureState.objects.filter(
                    feature=feature,
                    environment=environment,
                    identity__isnull=True,
                    feature_segment__isnull=True,
                ).first()

                if feature_state:
                    # Get feature value information
                    value = None
                    value_type = None
                    try:
                        feature_state_value = feature_state.feature_state_value
                        value = feature_state_value.value
                        # Map internal type constants to user-friendly strings
                        type_map = {STRING: "string", INTEGER: "integer", BOOLEAN: "boolean"}
                        value_type = type_map.get(feature_state_value.type, "string")
                    except Exception:
                        pass

                    results.append(
                        {
                            "feature_id": feature.id,
                            "feature_name": feature.name,
                            "environment_id": environment.id,
                            "environment_name": environment.name,
                            "enabled": feature_state.enabled,
                            "description": feature.description or "",
                            "value": value,
                            "value_type": value_type,
                        }
                    )

        return Response({"results": results, "count": len(results)})

    return Response(
        {"error": "Please provide either feature_id and environment_id, or project_id"},
        status=status.HTTP_400_BAD_REQUEST,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_simple_features(request):  # type: ignore[no-untyped-def]
    """
    List all features for a project.

    GET /api/v1/features/simple/list/?project_id=1
    """
    project_id = request.query_params.get("project_id")

    if not project_id:
        return Response(
            {"error": "project_id parameter is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        return Response(
            {"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND
        )

    features = Feature.objects.filter(project=project)

    results = [
        {
            "id": feature.id,
            "name": feature.name,
            "description": feature.description or "",
            "default_enabled": feature.default_enabled,
            "is_archived": feature.is_archived,
            "created_date": feature.created_date,
        }
        for feature in features
    ]

    return Response({"results": results, "count": len(results)})
