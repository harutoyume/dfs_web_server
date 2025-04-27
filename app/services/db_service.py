# Import downloaded modules
import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session
import sqlalchemy.ext.declarative as dec
from dotenv import load_dotenv

# Import built-in modules
import os


# Base class for declarative class definitions
SqlAlchemyBase = dec.declarative_base()  

# Private variable to store the session factory
__factory = None  


def create_tables():
    pass

def global_init():
    """Initialize the database connection and create session factory."""
    global __factory

    if __factory:  # If factory already exists, return
        return
    
    dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
    if os.path.exists(dotenv_path):
        # Load environment variables
        load_dotenv(dotenv_path)
    
    user = os.getenv('DB_USER', 'postgres')
    password = os.getenv('DB_USER', 'postgres')
    host = os.getenv('DB_HOST', 'localhost')
    port = os.getenv('DB_PORT', '5432')
    name = os.getenv('DB_NAME', 'postgres')

    # Create connection string for PostgreSQL
    conn_str = f'postgresql://{user}:{password}@{host}:{port}/{name}'
    print(f"Connecting to database on address {conn_str}")

    # Create database engine with the connection string
    engine = sa.create_engine(conn_str, echo=False)
    # Create session factory bound to the engine
    __factory = orm.sessionmaker(bind=engine)
    
    from app.services.db_models import User, File, UserFiles
    # Create all tables in the database that inherit from SqlAlchemyBase
    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    """Create and return a new database session."""
    global __factory
    return __factory()  # Create and return a new session using the factory

