import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool
from dotenv import load_dotenv

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
  fileConfig(config.config_file_name)

# Load env vars (DB_DSN) from .env if present
load_dotenv()

# Override sqlalchemy.url from env or fallback to alembic.ini default.
# Ensure the psycopg3 driver is used (sqlalchemy default wäre psycopg2).
db_url = os.getenv("DB_DSN")
if db_url and db_url.startswith("postgresql://"):
  db_url = db_url.replace("postgresql://", "postgresql+psycopg://", 1)
if db_url:
  config.set_main_option("sqlalchemy.url", db_url)

# We don't use ORM metadata here; migrations are manual.
target_metadata = None


def run_migrations_offline():
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


def run_migrations_online():
  """Run migrations in 'online' mode."""
  connectable = engine_from_config(
    config.get_section(config.config_ini_section),
    prefix="sqlalchemy.",
    poolclass=pool.NullPool,
  )

  with connectable.connect() as connection:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
      context.run_migrations()


if context.is_offline_mode():
  run_migrations_offline()
else:
  run_migrations_online()
