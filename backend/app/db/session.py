import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 1. Directly target your production Neon connection environment string
DATABASE_URL = os.getenv("DATABASE_URL")

# 🛠️ AUTOMATIC PREFIX REPAIR: Resolves SQLAlchemy 1.4/2.0 dialect requirements 
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
        pool_size=10,          # Warm connection pool links to accommodate active request streams
        max_overflow=20,       # Bandwidth limits to comfortably handle request spikes
        pool_timeout=15,       # Fast fail-safe value to drop stalled connections early instead of hanging
        pool_recycle=600,      # Recycle stale links to prevent silent idle drops from serverless hosts
        pool_pre_ping=True     # 🛡️ Native lightweight check query run automatically before executing requests
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
