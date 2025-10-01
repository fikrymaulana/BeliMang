from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from passlib.context import CryptContext
from ..database import get_db
from ..admin.models import User, UserType
from .schemas import UserRegister
from ..admin.utils import create_access_token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

async def create_user(db: AsyncSession, user_data: UserRegister):
    # Check if username exists
    result = await db.execute(select(User).where(User.username == user_data.username))
    if result.scalars().first():
        raise ValueError("Username already exists")

    # Check if email + user_type exists for user
    result = await db.execute(select(User).where(User.email == user_data.email, User.user_type == UserType.user))
    if result.scalars().first():
        raise ValueError("Email already exists for user")

    hashed_password = get_password_hash(user_data.password)
    user = User(
        username=user_data.username,
        password_hash=hashed_password,
        email=user_data.email,
        user_type=UserType.user
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # Generate token
    token = create_access_token({"sub": user.id, "type": user.user_type.value})
    return {"token": token}

async def authenticate_user(db: AsyncSession, username: str, password: str):
    print(f"Authenticating user: {username}")

    # Get raw connection for prepared statements
    connection = await db.connection()

    try:
        # Prepare the statement once (cached on DB server)
        await connection.execute(
            "PREPARE get_user AS "
            "SELECT id, username, password_hash, email, type "
            "FROM users WHERE username = $1 AND type = $2"
        )

        # Execute with parameters
        result = await connection.execute(
            "EXECUTE get_user (%s, %s)",
            username, UserType.user.value
        )

        row = result.first()
        if not row:
            print("User not found or not user")
            raise ValueError("Invalid credentials")

        print("User found")

        # Extract user data from row
        user_id, user_username, password_hash, email, user_type = row

        if not verify_password(password, password_hash):
            print("Password verification failed")
            raise ValueError("Invalid credentials")

        print("Password verified")

        # Generate token
        token = create_access_token({"sub": user_id, "type": user_type})
        print(f"Token generated: {token[:20]}...")
        return {"token": token}

    finally:
        # Clean up prepared statement
        await connection.execute("DEALLOCATE get_user")