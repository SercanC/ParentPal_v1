# ParentPal Developer Update - Session 1

## Project Overview

ParentPal is an offline-first baby tracking application designed to help parents reliably track their baby's activities, even without internet connectivity. The project is structured to support multiple caregivers with seamless synchronization and potential future AI capabilities.

### Core Goals

1. **Offline-First Architecture**
   - Complete functionality without internet connection
   - Reliable sync when connection is restored
   - Conflict resolution between multiple caregivers
   - Minimal data usage and battery impact

2. **Essential Tracking Features**
   - Sleep tracking
   - Feeding monitoring
   - Diaper changes
   - Health records

3. **Multi-Caregiver Support**
   - Shared access between parents
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
- **Authentication**: JWT-based with refresh tokens
- **Storage**: Redis for caching (future use)

### Frontend (Planned)

- **Framework**: React Native
- **State Management**: React Query + Redux Toolkit
- **Storage**: AsyncStorage for offline data
- **Sync**: Background sync with retry mechanism

## Current Project Structure

```
ParentPal_v1/
├── backend/
│   ├── alembic/              # Database migrations
│   │   ├── versions/         # Migration versions
│   │   └── env.py            # Migration environment
│   ├── app/
│   │   ├── api/              # API endpoints
│   │   │   ├── v1/           # API version 1
│   │   │   │   ├── endpoints/
│   │   │   │   │   └── auth.py  # Authentication endpoints
│   │   │   │   └── api.py    # API router
│   │   │   └── deps.py       # Dependencies
│   │   ├── core/             # Core functionality
│   │   │   ├── config.py     # Application config
│   │   │   └── security.py   # Security utilities
│   │   ├── db/               # Database
│   │   │   ├── base_class.py # Base SQLAlchemy class
│   │   │   └── session.py    # Database session
│   │   ├── models/           # SQLAlchemy models
│   │   │   ├── activity.py   # Activity model
│   │   │   ├── baby.py       # Baby model
│   │   │   ├── care_team.py  # Care team model
│   │   │   ├── enums.py      # Enum types
│   │   │   └── user.py       # User model
│   │   ├── schemas/          # Pydantic schemas
│   │   │   ├── activity.py   # Activity schemas
│   │   │   ├── auth.py       # Auth schemas
│   │   │   ├── baby.py       # Baby schemas
│   │   │   ├── base.py       # Base schemas
│   │   │   ├── care_team.py  # Care team schemas
│   │   │   └── user.py       # User schemas
│   │   ├── services/         # Business logic
│   │   │   ├── activity.py   # Activity service
│   │   │   ├── baby.py       # Baby service
│   │   │   ├── base.py       # Base service
│   │   │   ├── care_team.py  # Care team service
│   │   │   ├── factory.py    # Service factory
│   │   │   └── user.py       # User service
│   │   └── main.py           # Application entry
│   ├── tests/                # Test directory
│   ├── alembic.ini           # Alembic config
│   ├── requirements.txt      # Python dependencies
│   └── .env.example          # Environment template
├── docs/                     # Documentation
├── sample-ui/                # UI design references
├── dev_log.md                # Development log
├── dev_update_s1.md          # This document
└── README.md                 # Project README
```

## Development Progress

### Completed Features

1. **Project Structure and Configuration**
   - FastAPI application setup
   - Environment configuration
   - Database connection
   - Health check endpoint

2. **Database Models and Migrations**
   - Core entity models (User, Baby, Activity, CareTeam)
   - Sync status tracking for offline support
   - Alembic migrations
   - Efficient indexing

3. **API Schemas**
   - Request/response validation
   - Sync and offline operation support
   - Batch operation schemas
   - Conflict resolution schemas

4. **Service Layer**
   - Generic CRUD operations
   - Entity-specific services
   - Service factory pattern
   - Dependency injection

5. **Authentication System**
   - User registration
   - JWT token generation
   - OAuth2 compatible login
   - Refresh token support
   - Password hashing and verification

### Current API Endpoints

```
GET /health - Health check
POST /api/v1/auth/register - User registration
POST /api/v1/auth/login - OAuth2 compatible login
POST /api/v1/auth/login/access-token - JSON-based login
POST /api/v1/auth/refresh-token - Token refresh
```

## Key Technical Decisions

### 1. Offline-First Architecture

We've implemented an offline-first architecture with the following components:

- **Sync Status Tracking**: Each entity tracks its sync status (pending, synced, conflict, failed)
- **Version Control**: Each record maintains a version number for conflict detection
- **Batch Operations**: API supports batch operations for efficient syncing
- **Conflict Resolution**: Framework for resolving conflicts between devices

```python
# Example: Activity model with sync support
class Activity(Base):
    id = Column(String, primary_key=True, index=True)
    # ... other fields ...
    version = Column(Integer, default=1)
    sync_status = Column(Enum(SyncStatus), default=SyncStatus.PENDING)
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
    token: Annotated[str, Depends(oauth2_scheme)],
    services: Annotated[ServiceFactory, Depends(get_services)]
) -> User:
    """Dependency for getting current authenticated user"""
    # ... token verification ...
    return user
```

## Technical Challenges Encountered

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

### 2. Alembic Migrations with Async Driver

**Challenge**: Alembic migrations weren't compatible with asyncpg driver.

**Solution**:
- Created separate sync and async database URIs
- Used psycopg2 for migrations
- Used asyncpg for application runtime

```python
# Configuration with both sync and async URIs
SQLALCHEMY_DATABASE_URI: str  # async URI for application
SYNC_SQLALCHEMY_DATABASE_URI: str  # sync URI for migrations
```

### 3. FastAPI Route Registration

**Challenge**: Some API endpoints weren't showing up in Swagger UI.

**Solution**:
- Added missing `__init__.py` files
- Fixed import issues
- Properly structured API routers
- Added explicit debug logging of routes

```python
# Print mounted routes for debugging
print("\nMounted routes:")
for route in app.routes:
    print(f"{route.methods} {route.path}")
```

### 4. WSL File Synchronization

**Challenge**: Changes made to files weren't always reflected when running the server due to WSL/Windows file sync issues.

**Solution**:
- Manually verified file contents
- Added debug output to check file paths
- Ensured proper file permissions
- Restarted server after changes

## Upcoming Development Tasks

### 1. Baby Profile Management
- Create baby profile
- Update baby information
- List babies for a user
- Get baby details with recent activities
- Delete baby profile

### 2. Activity Tracking
- Create activities (sleep, feed, diaper)
- Update activities
- List activities by type and date range
- Get activity details
- Delete activities
- Batch operations for sync

### 3. Care Team Management
- Invite caregivers
- Accept/reject invitations
- Update permissions
- Remove caregivers
- List team members

### 4. Offline Sync System
- Background sync queue
- Conflict resolution UI
- Network status monitoring
- Storage optimization

### 5. Frontend Development
- Initial React Native setup
- Authentication screens
- Activity tracking interface
- Offline storage implementation
- Sync mechanism

## Testing Strategy

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

## Development Environment

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

## Issues and Solutions Log

### Issue: Missing Auth Endpoints in Swagger UI

**Problem**: The register endpoint wasn't showing up in Swagger UI.

**Debugging Steps**:
1. Added route debugging to print all registered routes
2. Checked file structure and missing `__init__.py` files
3. Verified file contents and permissions
4. Checked import statements

**Solution**:
- Created missing `__init__.py` files
- Fixed import issues with modules
- Ensured files were properly saved to filesystem
- Restarted server with `--reload` flag

```python
# Debug code added to main.py
print("\nMounted routes:")
for route in app.routes:
    print(f"{route.methods} {route.path}")
```

### Issue: Alembic Migration Errors

**Problem**: Enum type conflicts during migration.

**Debugging Steps**:
1. Checked PostgreSQL for existing types
2. Reviewed migration code
3. Checked SQLAlchemy model definitions

**Solution**:
- Modified migration to use proper SQLAlchemy types
- Removed explicit enum creation in migrations
- Let SQLAlchemy handle type creation
- Added proper downgrade flow

## Next Developer Handoff Notes

As you continue development, keep in mind:

1. **Offline-First Philosophy**:
   - All data mutations go through storage service
   - Always handle offline state
   - Implement retry logic
   - Use optimistic updates

2. **Sync Strategy**:
   - Batch operations when possible
   - Handle conflicts gracefully
   - Implement proper error handling
   - Monitor sync performance

3. **Authentication Flow**:
   - JWT tokens for authentication
   - Refresh tokens for long-term access
   - Token validation without server connection
   - Secure storage of credentials

4. **Testing Priority**:
   - Test offline scenarios thoroughly
   - Verify sync with various network conditions
   - Test multi-user interactions
   - Verify conflict resolution

## Project Roadmap

### Phase 1: Core MVP (Current)
- Basic tracking functionality
- Multi-caregiver support
- Offline-first architecture
- Knowledge base

### Phase 2: AI Assistance (Future)
- Template-based suggestions
- Pattern analysis
- Scheduled reminders
- Basic insights

### Phase 3: Full AI Integration (Future)
- Dynamic AI scheduling
- Personalized recommendations
- Natural language logging
- Advanced insights

## Current Development Focus

We are currently focused on completing the core API endpoints for the MVP. The next immediate tasks are:

1. Implement baby profile management endpoints
2. Create activity tracking endpoints
3. Develop care team management system
4. Implement comprehensive sync system
5. Begin frontend development with React Native