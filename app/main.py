from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import timedelta
import httpx
from jose import JWTError
from pydantic import BaseModel
import logging

from app.core.config import settings
from app.core.security import create_access_token, decode_access_token, ALGORITHM
from app.schemas.token import Token, TokenData
from app.db.base import SessionLocal, engine
from app.models.user import Base, User
from app.crud.user import authenticate_user, get_user

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="API with JWT authentication using JSON format",
    openapi_tags=[
        {
            "name": "authentication",
            "description": "Authentication operations"
        },
        {
            "name": "user",
            "description": "User operations"
        },
        {
            "name": "admin",
            "description": "Admin operations"
        },
        {
            "name": "health",
            "description": "Health check operations"
        }
    ]
)

security = HTTPBearer()

class LoginData(BaseModel):
    username: str
    password: str

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = credentials.credentials
        logger.debug(f"Received token: {token}")
        
        payload = decode_access_token(token)
        logger.debug(f"Decoded payload: {payload}")
        
        username: str = payload.get("sub")
        role: str = payload.get("role")
        logger.debug(f"Extracted username: {username}, role: {role}")
        
        if username is None or role is None:
            logger.error("Username or role is None")
            raise credentials_exception
            
        token_data = TokenData(username=username, role=role)
        logger.debug(f"Created token data: {token_data}")
        
    except JWTError as e:
        logger.error(f"JWT Error: {str(e)}")
        raise credentials_exception
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise credentials_exception
    
    user = get_user(db, username=token_data.username)
    logger.debug(f"Retrieved user: {user}")
    
    if user is None:
        logger.error("User not found in database")
        raise credentials_exception
        
    if user.role != token_data.role:
        logger.error(f"Role mismatch: token role {token_data.role} != user role {user.role}")
        raise credentials_exception
        
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@app.post("/token", response_model=Token, tags=["authentication"])
async def login_for_access_token(
    login_data: LoginData,
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get token from external API first
    try:
        async with httpx.AsyncClient(verify=False) as client:
            # Log request details
            logger.debug(f"Sending request to external API with params: username={login_data.username}, password={login_data.password}")
            
            # Use query parameters instead of JSON body
            params = {
                "username": login_data.username,
                "password": login_data.password
            }
            response = await client.post(
                f"{settings.FAKE_API_BASE_URL}/token",
                params=params  # Send as query parameters
            )
            
            # Log response details
            logger.debug(f"External API response status: {response.status_code}")
            logger.debug(f"External API response body: {response.text}")
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"{response.status_code}: {response.text}"
                )
            external_token = response.json()["access_token"]
            
            # Create our own token that includes both our user info and the external token
            access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={
                    "sub": user.username,
                    "role": user.role,
                    "ext_token": external_token
                },
                expires_delta=access_token_expires
            )
            return {"access_token": access_token, "token_type": "bearer", "role": user.role}
    except Exception as e:
        logger.error(f"Error during token generation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get("/user", tags=["user"])
async def read_user_route(
    current_user: User = Depends(get_current_active_user),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    if current_user.role not in ["user", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    try:
        # Get the external token from our JWT payload
        payload = decode_access_token(credentials.credentials)
        external_token = payload.get("ext_token")
        if not external_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="External token not found"
            )
            
        async with httpx.AsyncClient(verify=False) as client:
            headers = {"Authorization": f"Bearer {external_token}"}
            response = await client.get(f"{settings.FAKE_API_BASE_URL}/user", headers=headers)
            return response.json()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get("/admin", tags=["admin"])
async def read_admin_route(
    current_user: User = Depends(get_current_active_user),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    try:
        # Get the external token from our JWT payload
        payload = decode_access_token(credentials.credentials)
        external_token = payload.get("ext_token")
        if not external_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="External token not found"
            )
            
        async with httpx.AsyncClient(verify=False) as client:
            headers = {"Authorization": f"Bearer {external_token}"}
            response = await client.get(f"{settings.FAKE_API_BASE_URL}/admin", headers=headers)
            return response.json()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get("/health", tags=["health"])
async def health_check():
    try:
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.get(f"{settings.FAKE_API_BASE_URL}/health")
            return response.json()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
