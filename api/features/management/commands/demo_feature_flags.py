"""
Management command to demonstrate basic feature flag functionality.

Usage:
    python manage.py demo_feature_flags
"""

from django.core.management.base import BaseCommand

from environments.models import Environment
from features.models import Feature, FeatureState
from organisations.models import Organisation
from projects.models import Project


class Command(BaseCommand):
    help = "Demonstrates basic feature flag functionality: create features and enable/disable them per environment"

    def handle(self, *args, **options):  # type: ignore[no-untyped-def]
        self.stdout.write(self.style.SUCCESS("\n=== Feature Flag Demo ===\n"))

        # Create or get test organisation
        org, created = Organisation.objects.get_or_create(
            name="Demo Organisation", defaults={"name": "Demo Organisation"}
        )
        self.stdout.write(
            f"{'Created' if created else 'Using existing'} organisation: {org.name}"
        )

        # Create or get test project
        project, created = Project.objects.get_or_create(
            name="Demo Project", organisation=org, defaults={"organisation": org}
        )
        self.stdout.write(
            f"{'Created' if created else 'Using existing'} project: {project.name}"
        )

        # Create or get test environments
        dev_env, created = Environment.objects.get_or_create(
            name="Development",
            project=project,
            defaults={"name": "Development", "project": project},
        )
        self.stdout.write(
            f"{'Created' if created else 'Using existing'} environment: {dev_env.name}"
        )

        prod_env, created = Environment.objects.get_or_create(
            name="Production",
            project=project,
            defaults={"name": "Production", "project": project},
        )
        self.stdout.write(
            f"{'Created' if created else 'Using existing'} environment: {prod_env.name}"
        )

        # Create demo features
        self.stdout.write(
            self.style.SUCCESS("\n--- Creating Feature Flags ---\n")
        )

        # Feature 1: new_dashboard
        new_dashboard, created = Feature.objects.get_or_create(
            name="new_dashboard",
            project=project,
            defaults={
                "name": "new_dashboard",
                "project": project,
                "description": "Enable the new dashboard UI",
                "default_enabled": False,
            },
        )
        self.stdout.write(
            f"{'Created' if created else 'Using existing'} feature: {new_dashboard.name}"
        )

        # Feature 2: beta_features
        beta_features, created = Feature.objects.get_or_create(
            name="beta_features",
            project=project,
            defaults={
                "name": "beta_features",
                "project": project,
                "description": "Enable beta features for testing",
                "default_enabled": False,
            },
        )
        self.stdout.write(
            f"{'Created' if created else 'Using existing'} feature: {beta_features.name}"
        )

        # Feature 3: dark_mode
        dark_mode, created = Feature.objects.get_or_create(
            name="dark_mode",
            project=project,
            defaults={
                "name": "dark_mode",
                "project": project,
                "description": "Enable dark mode theme",
                "default_enabled": False,
            },
        )
        self.stdout.write(
            f"{'Created' if created else 'Using existing'} feature: {dark_mode.name}"
        )

        # Feature 4: api_endpoint (with string value)
        api_endpoint, created = Feature.objects.get_or_create(
            name="api_endpoint",
            project=project,
            defaults={
                "name": "api_endpoint",
                "project": project,
                "description": "API endpoint URL configuration",
                "default_enabled": True,
            },
        )
        self.stdout.write(
            f"{'Created' if created else 'Using existing'} feature: {api_endpoint.name}"
        )

        # Feature 5: max_retries (with integer value)
        max_retries, created = Feature.objects.get_or_create(
            name="max_retries",
            project=project,
            defaults={
                "name": "max_retries",
                "project": project,
                "description": "Maximum number of API retries",
                "default_enabled": True,
            },
        )
        self.stdout.write(
            f"{'Created' if created else 'Using existing'} feature: {max_retries.name}"
        )

        # Feature 6: use_cache (with boolean value)
        use_cache, created = Feature.objects.get_or_create(
            name="use_cache",
            project=project,
            defaults={
                "name": "use_cache",
                "project": project,
                "description": "Enable caching for API responses",
                "default_enabled": True,
            },
        )
        self.stdout.write(
            f"{'Created' if created else 'Using existing'} feature: {use_cache.name}"
        )

        # Configure feature states per environment
        self.stdout.write(
            self.style.SUCCESS("\n--- Configuring Feature States per Environment ---\n")
        )

        # Development environment: Enable new_dashboard and beta_features
        for feature in [new_dashboard, beta_features]:
            fs = FeatureState.objects.filter(
                feature=feature,
                environment=dev_env,
                identity__isnull=True,
                feature_segment__isnull=True,
            ).first()
            if fs:
                fs.enabled = True
                fs.save()
                self.stdout.write(
                    f"Development: Enabled '{feature.name}' - Status: {fs.enabled}"
                )

        # Development environment: Disable dark_mode
        fs = FeatureState.objects.filter(
            feature=dark_mode,
            environment=dev_env,
            identity__isnull=True,
            feature_segment__isnull=True,
        ).first()
        if fs:
            fs.enabled = False
            fs.save()
            self.stdout.write(
                f"Development: Disabled '{dark_mode.name}' - Status: {fs.enabled}"
            )

        # Production environment: Only enable new_dashboard
        fs = FeatureState.objects.filter(
            feature=new_dashboard,
            environment=prod_env,
            identity__isnull=True,
            feature_segment__isnull=True,
        ).first()
        if fs:
            fs.enabled = True
            fs.save()
            self.stdout.write(
                f"Production: Enabled '{new_dashboard.name}' - Status: {fs.enabled}"
            )

        # Production environment: Disable beta_features and dark_mode
        for feature in [beta_features, dark_mode]:
            fs = FeatureState.objects.filter(
                feature=feature,
                environment=prod_env,
                identity__isnull=True,
                feature_segment__isnull=True,
            ).first()
            if fs:
                fs.enabled = False
                fs.save()
                self.stdout.write(
                    f"Production: Disabled '{feature.name}' - Status: {fs.enabled}"
                )

        # Configure feature values
        self.stdout.write(
            self.style.SUCCESS("\n--- Setting Feature Values ---\n")
        )

        from features.value_types import BOOLEAN, INTEGER, STRING

        # Set string value for api_endpoint
        for env, url in [(dev_env, "https://dev-api.example.com"), (prod_env, "https://api.example.com")]:
            fs = FeatureState.objects.filter(
                feature=api_endpoint,
                environment=env,
                identity__isnull=True,
                feature_segment__isnull=True,
            ).first()
            if fs:
                try:
                    fsv = fs.feature_state_value
                    fsv.type = STRING
                    fsv.string_value = url
                    fsv.integer_value = None
                    fsv.boolean_value = None
                    fsv.save()
                    self.stdout.write(
                        f"{env.name}: Set '{api_endpoint.name}' = '{url}' (string)"
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f"Failed to set value for {api_endpoint.name}: {e}")
                    )

        # Set integer value for max_retries
        for env, retries in [(dev_env, 5), (prod_env, 3)]:
            fs = FeatureState.objects.filter(
                feature=max_retries,
                environment=env,
                identity__isnull=True,
                feature_segment__isnull=True,
            ).first()
            if fs:
                try:
                    fsv = fs.feature_state_value
                    fsv.type = INTEGER
                    fsv.integer_value = retries
                    fsv.string_value = None
                    fsv.boolean_value = None
                    fsv.save()
                    self.stdout.write(
                        f"{env.name}: Set '{max_retries.name}' = {retries} (integer)"
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f"Failed to set value for {max_retries.name}: {e}")
                    )

        # Set boolean value for use_cache
        for env, enabled in [(dev_env, False), (prod_env, True)]:
            fs = FeatureState.objects.filter(
                feature=use_cache,
                environment=env,
                identity__isnull=True,
                feature_segment__isnull=True,
            ).first()
            if fs:
                try:
                    fsv = fs.feature_state_value
                    fsv.type = BOOLEAN
                    fsv.boolean_value = enabled
                    fsv.string_value = None
                    fsv.integer_value = None
                    fsv.save()
                    self.stdout.write(
                        f"{env.name}: Set '{use_cache.name}' = {enabled} (boolean)"
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f"Failed to set value for {use_cache.name}: {e}")
                    )

        # Summary
        self.stdout.write(
            self.style.SUCCESS("\n--- Feature Flag Status Summary ---\n")
        )
        self.stdout.write("\nDevelopment Environment:")
        for feature in Feature.objects.filter(project=project):
            fs = FeatureState.objects.filter(
                feature=feature,
                environment=dev_env,
                identity__isnull=True,
                feature_segment__isnull=True,
            ).first()
            status = "✓ ENABLED" if fs and fs.enabled else "✗ DISABLED"
            
            # Try to get value
            value_str = ""
            if fs:
                try:
                    fsv = fs.feature_state_value
                    if fsv.value is not None:
                        type_map = {STRING: "string", INTEGER: "integer", BOOLEAN: "boolean"}
                        value_type = type_map.get(fsv.type, "string")
                        value_str = f" | Value: {fsv.value} ({value_type})"
                except Exception:
                    pass
            
            self.stdout.write(f"  {feature.name}: {status}{value_str}")

        self.stdout.write("\nProduction Environment:")
        for feature in Feature.objects.filter(project=project):
            fs = FeatureState.objects.filter(
                feature=feature,
                environment=prod_env,
                identity__isnull=True,
                feature_segment__isnull=True,
            ).first()
            status = "✓ ENABLED" if fs and fs.enabled else "✗ DISABLED"
            
            # Try to get value
            value_str = ""
            if fs:
                try:
                    fsv = fs.feature_state_value
                    if fsv.value is not None:
                        type_map = {STRING: "string", INTEGER: "integer", BOOLEAN: "boolean"}
                        value_type = type_map.get(fsv.type, "string")
                        value_str = f" | Value: {fsv.value} ({value_type})"
                except Exception:
                    pass
            
            self.stdout.write(f"  {feature.name}: {status}{value_str}")

        self.stdout.write(
            self.style.SUCCESS("\n=== Demo Complete ===\n")
        )
        self.stdout.write(
            f"\nDevelopment API Key: {dev_env.api_key}"
        )
        self.stdout.write(
            f"Production API Key: {prod_env.api_key}"
        )
        self.stdout.write(
            "\nUse these API keys to query feature flags via the SDK or API endpoints.\n"
        )
