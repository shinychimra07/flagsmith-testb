# Feature Flag Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         User/Client                              │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          │ HTTP Requests
                          │
┌─────────────────────────▼───────────────────────────────────────┐
│                    REST API Layer                                │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │          Simple Feature Flag Endpoints                   │   │
│  │  - POST /api/v1/features/simple/create/                  │   │
│  │  - POST /api/v1/features/simple/toggle/                  │   │
│  │  - GET  /api/v1/features/simple/status/                  │   │
│  │  - GET  /api/v1/features/simple/list/                    │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          │ Validates & Processes
                          │
┌─────────────────────────▼───────────────────────────────────────┐
│                    Service Layer                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              simple_views.py                             │   │
│  │  - SimpleFeatureSerializer                               │   │
│  │  - FeatureStateToggleSerializer                          │   │
│  │  - create_simple_feature()                               │   │
│  │  - toggle_feature_state()                                │   │
│  │  - get_feature_status()                                  │   │
│  │  - list_simple_features()                                │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          │ CRUD Operations
                          │
┌─────────────────────────▼───────────────────────────────────────┐
│                     Data Models                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Feature    │  │ FeatureState │  │ Environment  │          │
│  │              │  │              │  │              │          │
│  │ - id         │  │ - id         │  │ - id         │          │
│  │ - name       │  │ - feature_id │  │ - name       │          │
│  │ - project_id │  │ - env_id     │  │ - project_id │          │
│  │ - enabled    │  │ - enabled    │  │ - api_key    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│         │                  │                   │                 │
│         └──────────────────┴───────────────────┘                 │
│                            │                                     │
└────────────────────────────┼─────────────────────────────────────┘
                             │
                             │ Persists to
                             │
┌────────────────────────────▼─────────────────────────────────────┐
│                        Database                                   │
│                      (PostgreSQL)                                 │
└───────────────────────────────────────────────────────────────────┘
```

## Request Flow

### 1. Create Feature Flow

```
Client                  API                     Service                 Database
  │                      │                         │                       │
  │ POST /create/        │                         │                       │
  ├─────────────────────►│                         │                       │
  │                      │                         │                       │
  │                      │ Validate data           │                       │
  │                      ├────────────────────────►│                       │
  │                      │                         │                       │
  │                      │                         │ Create Feature        │
  │                      │                         ├──────────────────────►│
  │                      │                         │                       │
  │                      │                         │ Create FeatureStates  │
  │                      │                         │ (one per environment) │
  │                      │                         ├──────────────────────►│
  │                      │                         │                       │
  │                      │                         │ Return Feature ID     │
  │                      │                         │◄──────────────────────┤
  │                      │                         │                       │
  │                      │ Return response         │                       │
  │                      │◄────────────────────────┤                       │
  │                      │                         │                       │
  │ Response (201)       │                         │                       │
  │◄─────────────────────┤                         │                       │
  │                      │                         │                       │
```

### 2. Toggle Feature Flow

```
Client                  API                     Service                 Database
  │                      │                         │                       │
  │ POST /toggle/        │                         │                       │
  ├─────────────────────►│                         │                       │
  │                      │                         │                       │
  │                      │ Validate data           │                       │
  │                      ├────────────────────────►│                       │
  │                      │                         │                       │
  │                      │                         │ Find FeatureState     │
  │                      │                         ├──────────────────────►│
  │                      │                         │                       │
  │                      │                         │ Return FeatureState   │
  │                      │                         │◄──────────────────────┤
  │                      │                         │                       │
  │                      │                         │ Update enabled field  │
  │                      │                         ├──────────────────────►│
  │                      │                         │                       │
  │                      │                         │ Confirm update        │
  │                      │                         │◄──────────────────────┤
  │                      │                         │                       │
  │                      │ Return response         │                       │
  │                      │◄────────────────────────┤                       │
  │                      │                         │                       │
  │ Response (200)       │                         │                       │
  │◄─────────────────────┤                         │                       │
  │                      │                         │                       │
```

## Data Relationships

```
Organisation
    │
    │ has many
    ▼
Project
    │
    ├─────────────┬──────────────┐
    │ has many    │ has many     │
    ▼             ▼              │
Feature       Environment        │
    │             │              │
    │             │              │
    └──────┬──────┘              │
           │ creates             │
           ▼                     │
      FeatureState ◄─────────────┘
      (per environment)
```

## Feature State Logic

```
When a Feature is created:
┌─────────────────────────────────────┐
│ 1. Create Feature record            │
│                                     │
│ 2. For each Environment in Project: │
│    ├─ Create FeatureState           │
│    ├─ Set enabled = default_enabled │
│    └─ Set environment reference     │
│                                     │
│ 3. Return Feature ID                │
└─────────────────────────────────────┘

When toggling a Feature:
┌─────────────────────────────────────┐
│ 1. Find FeatureState for:           │
│    ├─ feature_id                    │
│    ├─ environment_id                │
│    ├─ identity = NULL               │
│    └─ feature_segment = NULL        │
│                                     │
│ 2. Update enabled field             │
│                                     │
│ 3. Save changes                     │
└─────────────────────────────────────┘
```

## Component Dependencies

```
┌─────────────────────────────────────────────────────────────┐
│                     simple_views.py                          │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ Depends on:                                           │  │
│  │ - rest_framework (serializers, views, decorators)    │  │
│  │ - features.models (Feature, FeatureState)            │  │
│  │ - environments.models (Environment)                   │  │
│  │ - projects.models (Project)                           │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                 demo_feature_flags.py                        │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ Depends on:                                           │  │
│  │ - django.core.management.base (BaseCommand)           │  │
│  │ - features.models (Feature, FeatureState)            │  │
│  │ - environments.models (Environment)                   │  │
│  │ - organisations.models (Organisation)                 │  │
│  │ - projects.models (Project)                           │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Integration Points

```
┌─────────────────────────────────────────────────────────────┐
│              Simple Feature Flag API                         │
└─────────────┬──────────────────────────────────┬────────────┘
              │                                  │
              │ Creates/Updates                  │ Works with
              │                                  │
┌─────────────▼──────────────┐  ┌───────────────▼────────────┐
│  Core Flagsmith Models      │  │  Existing Flagsmith APIs   │
│  - Feature                  │  │  - Project Features API    │
│  - FeatureState             │  │  - Environment API         │
│  - Environment              │  │  - SDK API                 │
│  - Project                  │  │  - Web UI                  │
└─────────────────────────────┘  └────────────────────────────┘
```

## Security Flow

```
Client Request
    │
    ▼
┌─────────────────────────┐
│ Authentication Required │
│ (Token-based)           │
└─────────┬───────────────┘
          │ Valid token?
          ├── No ──► 401 Unauthorised
          │
          ▼ Yes
┌─────────────────────────┐
│ Permission Check        │
│ (Project access)        │
└─────────┬───────────────┘
          │ Has permission?
          ├── No ──► 403 Forbidden
          │
          ▼ Yes
┌─────────────────────────┐
│ Execute Request         │
└─────────────────────────┘
```

## Environment States

```
Feature: "new_checkout"

Development Environment     Production Environment
┌───────────────────┐      ┌───────────────────┐
│ FeatureState      │      │ FeatureState      │
│ - feature_id: 1   │      │ - feature_id: 1   │
│ - env_id: 1       │      │ - env_id: 2       │
│ - enabled: TRUE   │      │ - enabled: FALSE  │
└───────────────────┘      └───────────────────┘
        ▲                           ▲
        │                           │
        └───────────┬───────────────┘
                    │
            ┌───────▼────────┐
            │ Feature        │
            │ - id: 1        │
            │ - name: "..."  │
            │ - project_id:1 │
            └────────────────┘
```

## Test Architecture

```
┌───────────────────────────────────────────────────────────┐
│                    Integration Tests                       │
│  - test_simple_feature_flags.py                           │
│  - Tests full API endpoints with database                 │
│  - Uses fixtures: admin_client, project, environment      │
└───────────────────────────────────────────────────────────┘
                            │
┌───────────────────────────▼───────────────────────────────┐
│                      Unit Tests                            │
│  - test_unit_simple_feature_flags.py                      │
│  - Tests serialisers and logic in isolation               │
│  - Tests model behaviours                                 │
└────────────────────────────────────────────────────────────┘
```
