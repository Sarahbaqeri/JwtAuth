import sqlalchemy as _sqlalchemy 
import sqlalchemy.ext.declarative as declarative
import sqlalchemy.orm as orm  



DB_URL = 'sqlite:///./dbfile.db'
engine = _sqlalchemy.create_engine(DB_URL,connect_args = {'check_same_thread':False})


SessionLocal = orm.sessionmaker(autocommit=False,autoflush=False,bind=engine)

Base = _sqlalchemy.orm.declarative_base()


