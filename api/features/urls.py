from django.conf import settings
from django.conf.urls import include
from django.urls import path
from rest_framework_nested import routers  # type: ignore[import-untyped]

from features.feature_segments.views import FeatureSegmentViewSet
from features.import_export.views import (
    create_feature_export,
    download_feature_export,
    download_flagsmith_on_flagsmith,
    feature_import,
)
from features.simple_views import (
    create_simple_feature,
    get_feature_status,
    list_simple_features,
    toggle_feature_state,
)
from features.views import (
    SimpleFeatureStateViewSet,
    get_feature_by_uuid,
    get_feature_state_by_uuid,
)

router = routers.DefaultRouter()
router.register(r"featurestates", SimpleFeatureStateViewSet, basename="featurestates")
router.register(r"feature-segments", FeatureSegmentViewSet, basename="feature-segment")

app_name = "features"

urlpatterns = [
    path("", include(router.urls)),
    path("simple/create/", create_simple_feature, name="create-simple-feature"),
    path("simple/toggle/", toggle_feature_state, name="toggle-feature-state"),
    path("simple/status/", get_feature_status, name="get-feature-status"),
    path("simple/list/", list_simple_features, name="list-simple-features"),
    path("get-by-uuid/<uuid:uuid>/", get_feature_by_uuid, name="get-feature-by-uuid"),
    path("create-feature-export/", create_feature_export, name="create-feature-export"),
    path(
        "download-feature-export/<int:feature_export_id>/",
        download_feature_export,
        name="download-feature-export",
    ),
    path(
        "download-flagsmith-on-flagsmith/",
        download_flagsmith_on_flagsmith,
        name="download-flagsmith-on-flagsmith",
    ),
    path(
        "feature-import/<int:environment_id>",
        feature_import,
        name="feature-import",
    ),
    path(
        "featurestates/get-by-uuid/<uuid:uuid>/",
        get_feature_state_by_uuid,
        name="get-feature-state-by-uuid",
    ),
]

if settings.WORKFLOWS_LOGIC_INSTALLED:
    urlpatterns.append(
        path(
            "workflows/",
            include("workflows_logic.urls", namespace="workflows"),
        )
    )
