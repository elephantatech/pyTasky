import os
import sys
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    notes = Column(String)
    tag = Column(String)
    status = Column(String, default="todo")
    created_at = Column(DateTime)
    completed_at = Column(DateTime)
    last_updated = Column(DateTime)

    def __repr__(self):
        return f"<Task(id={self.id}, title='{self.title}', status='{self.status}')>"


def get_database_path():
    """Get the database path, adjusting for PyInstaller bundling"""
    if hasattr(sys, "_MEIPASS"):
        # When bundled, place the database next to the executable
        return os.path.join(os.path.dirname(sys.executable), "pytasky_tasks.db")
    # When running as a script, place it in the project root
    return os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "pytasky_tasks.db"
    )


DATABASE_PATH = get_database_path()
engine = create_engine(f"sqlite:///{DATABASE_PATH}", echo=False)
Session = sessionmaker(bind=engine)


def get_session():
    return Session()


# Create the tables if they don't exist
Base.metadata.create_all(engine)
