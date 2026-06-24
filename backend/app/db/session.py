import os
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 1. Directly target your production Neon connection environment string
DATABASE_URL = os.getenv("DATABASE_URL")

# 🛠️ AUTOMATIC PREFIX REPAIR: Resolves SQLAlchemy 1.4/2.0 requirements 
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# 2. Establish fallback parameters if the cloud configuration is missing entirely
if not DATABASE_URL:
    print("⚠️ DATABASE_URL variable not detected in environment. Defaulting to local workspace fallback.")
    DATABASE_URL = "sqlite:///./platform_persistence.db"

# 3. Compile the structural engine with serverless-optimized connection configurations
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(
        DATABASE_URL,
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=1800,
        pool_pre_ping=True  # 🛡️ Forces an active verification ping before firing requests
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 4. Thread-safe execution dependency container mapping
def get_db():
    """
    Scoped resource lifecycle dependency generator loop.
    Guarantees clean transaction check-ins and connection pool releases.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_cloud_handshake(max_retries: int = 5, delay_seconds: int = 3) -> bool:
    """
    Executes an explicit startup verification handshake against Neon PostgreSQL.
    Bypasses environmental latency races without breaking application boot.
    """
    print("📡 Testing production database connection pool parameters...")
    for attempt in range(1, max_retries + 1):
        try:
            # Execute an ultra-lightweight check query to confirm backend responsiveness
            with engine.connect() as connection:
                connection.execute("SELECT 1")
            print("🚀 PostgreSQL Server Handshake Complete. Relational Schema Active.")
            return True
        except Exception as e:
            print(f"⏳ Connection attempt ({attempt}/{max_retries}) unfulfilled: {str(e)}")
            if attempt < max_retries:
                time.sleep(delay_seconds)
                
    print("❌ Critical Path Failure: Cloud database framework completely unreachable.")
    return False
