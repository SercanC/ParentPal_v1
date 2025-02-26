# ParentPal Developer Update - Session 2

## Project Overview

ParentPal is an offline-first baby tracking application designed to help parents reliably track their baby's activities, even without internet connectivity. The project emphasizes reliability, multi-caregiver coordination, and a foundation for future AI-powered features.

### Core Goals

1. **Offline-First Architecture**
   - Complete functionality without internet connection
   - Reliable sync when connection is restored
   - Conflict resolution between multiple caregivers
   - Minimal data usage and battery impact

2. **Essential Tracking Features**
   - Sleep tracking (time, quality, location)
   - Feeding monitoring (type, amount, duration)
   - Diaper changes (type, notes)
   - Health records (temperature, symptoms, medications)

3. **Multi-Caregiver Support**
   - Shared access between parents and other caregivers
   - Role-based permissions
   - Activity synchronization
   - Real-time updates when online

4. **Future AI Integration (Phased)**
   - Template-based foundations (current phase)
   - Basic pattern recognition (future phase)
   - Personalized recommendations (future phase)

## Technical Architecture

### Backend

- **Framework**: FastAPI with async support
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT-based with refresh tokens and token expiration
- **Caching**: Redis for future use

### Frontend (Planned)

- **Framework**: React Native
- **State Management**: React Query + Redux Toolkit
- **Offline Storage**: AsyncStorage for local data
- **Sync**: Background sync with retry mechanism

## Current Project Structure

```
ParentPal_v1/
├── backend/
│   ├── alembic/              # Database migrations
│   │   ├── versions/
│   │   │   ├── initial_migration.py
│   │   │   └── fix_enum_issue.py
│   │   └── env.py
│   ├── app/
│   │   ├── api/
│   │   │   ├── v1/
│   │   │   │   ├── endpoints/
│   │   │   │   │   ├── auth.py       # Authentication endpoints
│   │   │   │   │   ├── baby.py       # Baby profile endpoints
│   │   │   │   │   └── __init__.py
│   │   │   │   ├── api.py            # API router
│   │   │   │   └── __init__.py
│   │   │   ├── deps.py               # Dependencies
│   │   │   └── __init__.py
│   │   ├── core/
│   │   │   ├── config.py             # Application config
│   │   │   ├── security.py           # Security utilities
│   │   │   └── __init__.py
│   │   ├── db/
│   │   │   ├── base_class.py         # Base SQLAlchemy class
│   │   │   ├── session.py            # Database session
│   │   │   └── __init__.py
│   │   ├── models/                   # SQLAlchemy models
│   │   │   ├── activity.py
│   │   │   ├── baby.py
│   │   │   ├── care_team.py
│   │   │   ├── enums.py
│   │   │   ├── user.py
│   │   │   └── __init__.py
│   │   ├── schemas/                  # Pydantic schemas
│   │   │   ├── activity.py
│   │   │   ├── auth.py
│   │   │   ├── baby.py
│   │   │   ├── base.py
│   │   │   ├── care_team.py
│   │   │   ├── user.py
│   │   │   └── __init__.py
│   │   ├── services/                 # Business logic
│   │   │   ├── activity.py
│   │   │   ├── baby.py
│   │   │   ├── base.py
│   │   │   ├── care_team.py
│   │   │   ├── factory.py
│   │   │   ├── user.py
│   │   │   └── __init__.py
│   │   ├── main.py                   # Application entry
│   │   └── __init__.py
│   ├── tests/
│   ├── requirements.txt
│   └── .env
├── docs/
├── frontend/                      # Not yet implemented
├── sample-ui/
├── dev_log.md
├── dev_update_s1.md
├── dev_update_s2.md               # This document
└── README.md
```

## Development Progress

### Completed Features

1. **Authentication System**
   - User registration with email/password
   - JWT-based authentication with refresh tokens
   - OAuth2-compatible login endpoint
   - JSON-based login endpoint
   - Token refresh functionality
   - Secure password handling with bcrypt

2. **Baby Profile Management**
   - Create baby profile (primary caregiver assignment)
   - List all babies for authenticated user
   - Get detailed baby profile with recent activities
   - Update baby profile with permission checks
   - Delete baby profile (primary caregiver only)
   - Update development data with flexible JSON structure

3. **Database and ORM**
   - SQLAlchemy models with proper relationships
   - PostgreSQL database integration
   - Alembic migrations
   - Optimized queries and indexing
   - Transaction management

4. **API Structure and Validation**
   - OpenAPI documentation with Swagger UI
   - Request/response validation with Pydantic
   - Error handling and custom exceptions
   - Rate limiting setup (not yet enabled)

### Current API Endpoints

```
/health - Health check

/api/v1/auth/register - Register a new user
/api/v1/auth/login - OAuth2 compatible login
/api/v1/auth/login/access-token - JSON-based login
/api/v1/auth/refresh-token - Token refresh endpoint

/api/v1/babies - Create and list baby profiles
/api/v1/babies/{baby_id} - Get, update, and delete baby profiles
/api/v1/babies/{baby_id}/development - Update development data
```

## Key Technical Decisions

### 1. Offline-First Architecture

We've implemented an offline-first architecture with the following components:

- **Sync Status Tracking**: Each entity (Baby, Activity, CareTeam) tracks its sync status (pending, synced, conflict, failed)
- **Version Control**: Each record maintains a version number for conflict detection
- **Batch Operations**: API supports batch operations for efficient syncing
- **Conflict Resolution**: Framework for detecting and resolving conflicts between devices

```python
# Example: Activity model with sync support
class Activity(Base):
    id = Column(String, primary_key=True, index=True)
    # ... other fields ...
    version = Column(Integer, default=1)
    sync_status = Column(Enum("pending", "synced", "conflict", "failed", name="syncstatus"), default="pending")
    sync_attempts = Column(Integer, default=0)
    last_sync_attempt = Column(DateTime, nullable=True)
```

### 2. Authentication Strategy

We chose JWT-based authentication with refresh tokens for:

- **Offline Support**: Tokens can be validated without server connection
- **Security**: Short-lived access tokens with refresh capability
- **Multi-Device**: Supports multiple devices per user
- **Revocation**: Refresh tokens can be revoked for security

```python
# Token generation
def create_access_token(subject: str, expires_delta: timedelta = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {"exp": expire, "sub": str(subject)}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
```

### 3. Service Layer Pattern

We implemented a service layer pattern for:

- **Code Organization**: Clean separation of concerns
- **Reusability**: Common operations in base class
- **Testability**: Easy to mock for testing
- **Consistency**: Standardized approach to data access

```python
# Generic service base class
class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def get(self, id: Any) -> Optional[ModelType]:
        """Get a single record by id"""
        query = select(self.model).where(self.model.id == id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    # ... other methods ...
```

### 4. Dependency Injection

We use FastAPI's dependency injection system for:

- **Database Sessions**: Automatic session management
- **Authentication**: Current user extraction from tokens
- **Services**: Service factory instantiation
- **Permission Checking**: Role-based access control

```python
# Service factory dependency
async def get_services(db: Annotated[AsyncSession, Depends(get_db)]) -> ServiceFactory:
    """Dependency for getting service factory"""
    return ServiceFactory(db)

# Current user dependency
async def get_current_user(
    token: Annotated[str, Depends(security)],
    services: Annotated[ServiceFactory, Depends(get_services)]
) -> User:
    """Dependency for getting current authenticated user"""
    # ... token verification ...
    return user
```

## Technical Challenges and Solutions

### 1. SQLAlchemy with FastAPI Integration

**Challenge**: Setting up async SQLAlchemy with FastAPI while maintaining proper session management.

**Solution**: 
- Used AsyncSession with context manager
- Implemented dependency injection for database sessions
- Created custom service layer for database operations

```python
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

### 2. Enum Type Handling in PostgreSQL

**Challenge**: PostgreSQL enum types weren't properly handled by SQLAlchemy leading to type mismatch errors.

**Solution**:
- Created a database migration to fix enum handling
- Updated models to use string values for enum fields
- Ensured consistent enum value usage throughout the codebase

```python
# Baby model with fixed enum handling
class Baby(Base):
    # ...
    sync_status = Column(Enum("pending", "synced", "conflict", "failed", name="syncstatus"), default="pending")
```

```python
# Migration fix
def upgrade() -> None:
    # Work around the enum issue by using text for sync_status temporarily
    op.execute("ALTER TABLE baby ALTER COLUMN sync_status TYPE VARCHAR USING sync_status::VARCHAR")
    
    # Then ALTER it back to the enum but with default value as a string
    op.execute("ALTER TABLE baby ALTER COLUMN sync_status TYPE syncstatus USING sync_status::syncstatus")
    op.execute("ALTER TABLE baby ALTER COLUMN sync_status SET DEFAULT 'pending'")
```

### 3. Token Validation in Swagger UI

**Challenge**: Swagger UI wasn't properly handling Bearer token authorization.

**Solution**:
- Updated the OpenAPI schema with custom security schemes
- Implemented HTTPBearer security for token validation
- Added persistAuthorization parameter to Swagger UI

```python
def custom_openapi():
    # ...
    openapi_schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    
    # Apply security globally
    openapi_schema["security"] = [{"bearerAuth": []}]
    # ...
```

### 4. Development Data Update Logic

**Challenge**: Updating nested JSON data structures while preserving existing data was complex.

**Solution**:
- Implemented a specialized method for development data updates
- Used a direct SQL update query for better control
- Created a specific endpoint for development data updates

```python
async def update_development_data(
    self,
    *,
    baby_id: str,
    data: dict
) -> Baby:
    """Update baby's development data"""
    # Get the baby record
    baby = await self.get(baby_id)
    if not baby:
        return None
        
    # Create updated development data by merging existing with new
    new_development_data = dict(baby.development_data or {})
    new_development_data.update(data)
    
    # Use direct update query for better control
    stmt = (
        update(Baby)
        .where(Baby.id == baby_id)
        .values(
            development_data=new_development_data,
            sync_status="pending"
        )
    )
    await self.db.execute(stmt)
    await self.db.commit()
    
    # Reload the baby to get updated data
    return await self.get(baby_id)
```

## Upcoming Development Tasks

### 1. Activity Tracking Endpoints

The next major feature is implementing activity tracking for:

- **Sleep tracking**
  - Record sleep start/end times
  - Track sleep quality and location
  - Support for naps and overnight sleep

- **Feeding tracking**
  - Support for different feeding types (breast, bottle, solids)
  - Track amount, duration, and sides (for breastfeeding)
  - Notes and reactions

- **Diaper tracking**
  - Track diaper changes with type (wet, dirty, both)
  - Record consistency and color
  - Add notes for unusual observations

These endpoints will follow the same pattern as the baby endpoints:
- Create activity
- List activities with filtering (date range, type)
- Get activity details
- Update activity
- Delete activity
- Batch operations for sync

### 2. Care Team Management

After activity tracking, we'll implement care team features:

- Invite caregivers by email
- Accept/reject invitations
- Manage caregiver permissions
- Remove caregivers
- View activity by caregiver

### 3. Sync System

The sync system will include:

- Background sync queue
- Conflict detection
- Conflict resolution UI flows
- Retry logic for failed syncs
- Storage optimization

### 4. Frontend Development

Once the backend API is complete, we'll start on the React Native frontend with:

- Authentication screens
- Baby profile management
- Activity tracking interface
- Care team management
- Offline storage implementation
- Sync mechanism

## Development Environment Setup

### Required Software

- Node.js (≥ 18.0.0)
- Python (≥ 3.9)
- PostgreSQL (≥ 14)
- Redis (≥ 6.2)

### Setup Steps

1. **Clone Repository**
```bash
git clone https://github.com/SercanC/ParentPal_v1.git
cd ParentPal_v1
```

2. **Backend Setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env  # Update with your database credentials
```

3. **Database Setup**
```bash
createdb -U parentpal parentpal_dev
alembic upgrade head
```

4. **Run Development Server**
```bash
uvicorn app.main:app --reload
```

5. **API Access**
- API will be available at: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Common Development Tasks

### Creating a New Endpoint

1. Create a new file in `app/api/v1/endpoints/` for the endpoint group
2. Add the endpoint to the API router in `app/api/v1/api.py`
3. Implement the endpoint logic using the service layer
4. Add appropriate authentication and permission checks
5. Test the endpoint with Swagger UI

### Database Migrations

If you modify the database schema:

```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Revert migrations
alembic downgrade -1
```

### Authentication

To authenticate API requests:

1. Get a token using the `/api/v1/auth/login/access-token` endpoint
2. Include the token in the Authorization header:
   - `Authorization: Bearer <token>`

## Testing Strategy

We follow a comprehensive testing approach:

### 1. Unit Testing
- Test individual services and utilities
- Mock database operations
- Test authentication logic

### 2. Integration Testing
- Test API endpoints
- Test database operations
- Test sync mechanisms

### 3. End-to-End Testing
- Test complete user flows
- Test offline capabilities
- Test multi-user scenarios

## Recent Changes and Updates

Our latest development work has focused on:

1. **Baby Profile Management**
   - Implemented all CRUD operations for baby profiles
   - Added support for development data updates
   - Ensured proper permission checks
   - Fixed issues with relationship loading

2. **Authentication Improvements**
   - Enhanced token validation
   - Fixed Swagger UI authorization
   - Updated token refresh logic
   - Added proper error handling

3. **Database Fixes**
   - Resolved PostgreSQL enum type issues
   - Created migrations for schema fixes
   - Improved query efficiency
   - Enhanced relationship loading

4. **General Improvements**
   - Added detailed logging
   - Enhanced error messages
   - Improved API documentation
   - Fixed schema validation issues

## Common Questions and Answers

### Q: How does the offline-first approach work?
A: The system uses a combination of local storage and sync status tracking. Each entity has sync_status and version fields to track changes. When offline, all data is stored locally. When the connection is restored, changes are synced to the server with proper conflict resolution.

### Q: How are permissions handled?
A: We use a role-based permission system. Each baby has a primary caregiver and can have multiple care team members with different roles. Permissions are checked in the API endpoints using the current user's relationship to the baby profile.

### Q: How do I test the API?
A: You can use the built-in Swagger UI at http://localhost:8000/docs. First, authenticate using the login endpoint, then use the "Authorize" button to add your token. After that, you can test any endpoint.

### Q: What's the database schema migration process?
A: We use Alembic for migrations. When you change a model, create a new migration with `alembic revision --autogenerate`. Apply migrations with `alembic upgrade head`.

### Q: How is the authentication system structured?
A: We use JWT tokens with a short-lived access token and a longer-lived refresh token. The access token is used for API authentication, while the refresh token is used to get new access tokens without requiring the user to log in again.

### Q: How will multi-caregiver support work?
A: The care team system allows multiple caregivers to access a baby's data with different permission levels. All caregivers can log activities, but only those with appropriate permissions can modify baby profiles.

### Q: How do we handle conflicts during sync?
A: We use version numbers to detect conflicts. If a conflict is detected, we'll use a "last write wins" approach by default, but provide a UI for manually resolving conflicts in complex cases.

## Contributors

- Sercan Ceyhan (Project Lead)

## Next Development Session

In the next development session, we'll focus on:

1. Implementing activity tracking endpoints
2. Creating care team management features
3. Starting the frontend development
4. Enhancing the testing infrastructure

This will involve:
- Creating new API endpoints for activities
- Implementing filtering and query functionality
- Setting up the care team invitation system
- Starting the React Native project setup
- Implementing the frontend authentication flow