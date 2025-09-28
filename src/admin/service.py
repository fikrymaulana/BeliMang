from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from passlib.context import CryptContext
from ..database import get_db
from .models import User, UserType
from .schemas import AdminRegister
from .utils import create_access_token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

async def create_admin(db: AsyncSession, admin_data: AdminRegister):
    # Check if username exists
    result = await db.execute(select(User).where(User.username == admin_data.username))
    if result.scalars().first():
        raise ValueError("Username already exists")

    # Check if email + user_type exists for admin
    result = await db.execute(select(User).where(User.email == admin_data.email, User.user_type == UserType.admin))
    if result.scalars().first():
        raise ValueError("Email already exists for admin")

    hashed_password = get_password_hash(admin_data.password)
    user = User(
        username=admin_data.username,
        password_hash=hashed_password,
        email=admin_data.email,
        user_type=UserType.admin
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # Generate token
    token = create_access_token({"sub": user.id, "type": user.user_type.value})
    return {"token": token}

async def authenticate_admin(db: AsyncSession, username: str, password: str):
    print(f"Authenticating admin: {username}")
    result = await db.execute(select(User).where(User.username == username, User.user_type == UserType.admin))
    user = result.scalars().first()
    if not user:
        print("User not found or not admin")
        raise ValueError("Invalid credentials")
    print("User found")
    if not verify_password(password, user.password_hash):
        print("Password verification failed")
        raise ValueError("Invalid credentials")
    print("Password verified")

    # Generate token
    token = create_access_token({"sub": user.id, "type": user.user_type.value})
    print(f"Token generated: {token[:20]}...")
    return {"token": token}