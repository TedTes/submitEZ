from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Get database configuration from environment variables
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_DB_PASSWORD = os.getenv('SUPABASE_DB_PASSWORD')
SUPABASE_DB_HOST = os.getenv('SUPABASE_DB_HOST')
SUPABASE_DB_PORT = os.getenv('SUPABASE_DB_PORT', '5432')
SUPABASE_DB_USER = os.getenv('SUPABASE_DB_USER', 'postgres')
SUPABASE_DB_NAME = os.getenv('SUPABASE_DB_NAME', 'postgres')

# Build database URL from environment variables
if SUPABASE_DB_PASSWORD:
    # Option 1: Use explicit host/port/user/password from env
    if SUPABASE_DB_HOST:
        db_url = f"postgresql://{SUPABASE_DB_USER}:{SUPABASE_DB_PASSWORD}@{SUPABASE_DB_HOST}:{SUPABASE_DB_PORT}/{SUPABASE_DB_NAME}"
    # Option 2: Extract from SUPABASE_URL and use password from env
    elif SUPABASE_URL:
        # Extract project ID from SUPABASE_URL
        # Format: https://xxxxx.supabase.co -> db.xxxxx.supabase.co
        project_id = SUPABASE_URL.split('//')[1].split('.')[0]
        db_url = f"postgresql://{SUPABASE_DB_USER}:{SUPABASE_DB_PASSWORD}@db.{project_id}.supabase.co:{SUPABASE_DB_PORT}/{SUPABASE_DB_NAME}"
    else:
        raise ValueError(
            "Missing database configuration. Please set either:\n"
            "1. SUPABASE_DB_HOST, SUPABASE_DB_PASSWORD\n"
            "2. SUPABASE_URL, SUPABASE_DB_PASSWORD"
        )
    
    config.set_main_option('sqlalchemy.url', db_url)
else:
    raise ValueError(
        "SUPABASE_DB_PASSWORD is required for database migrations. "
        "Get it from Supabase Dashboard -> Settings -> Database -> Connection String"
    )

target_metadata = None


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()