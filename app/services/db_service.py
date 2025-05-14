# Import downloaded modules
import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session
import sqlalchemy.ext.declarative as dec

# Import built-in modules
import logging

# Import project files
from config import Config


# Setup logger
logger = logging.getLogger(__name__)

# Base class for declarative class definitions
SqlAlchemyBase = dec.declarative_base()  

# Private variable to store the session factory
__factory = None  


def global_init():
    """Initialize the database connection and create session factory."""
    global __factory

    if __factory:  # If factory already exists, return
        return
    
    user = Config.DB_USER
    password = Config.DB_PASSWORD
    host = Config.DB_HOST
    port = Config.DB_PORT
    name = Config.DB_NAME

    # Create connection string for PostgreSQL
    conn_str = f'postgresql://{user}:{password}@{host}:{port}/{name}'
    logger.info(f"Connecting to database on address {conn_str}")

    try:
        # Create database engine with the connection string
        engine = sa.create_engine(conn_str, echo=False)
        # Create session factory bound to the engine
        __factory = orm.sessionmaker(bind=engine)
        
        from app.services.db_models import User, File
        # Create all tables in the database that inherit from SqlAlchemyBase
        SqlAlchemyBase.metadata.create_all(engine)
    except Exception as e:
        logger.error(f"Error when connecting to database: {e}")


def create_session() -> Session:
    """Create and return a new database session."""
    global __factory
    if __factory == None:
        global_init()
        
    return __factory()  # Create and return a new session using the factory

