from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Define the base for SQLAlchemy models
Base = declarative_base()


# Define the Task model
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


# Database setup
DATABASE_PATH = os.path.join(os.path.dirname(__file__), "..", "pytasky_tasks.db")
engine = create_engine(f"sqlite:///{DATABASE_PATH}", echo=False)
Session = sessionmaker(bind=engine)

# Create the tables if they don't exist
Base.metadata.create_all(engine)


def get_session():
    return Session()
