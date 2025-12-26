from sqlalchemy import create_engine, Column, String, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import List
import datetime
import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "habits.db"

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH}")
connect_args = {"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class HabitModel(Base):
    __tablename__ = "habits"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    color = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class CompletionModel(Base):
    __tablename__ = "completions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String, nullable=False, index=True)
    habit_id = Column(String, nullable=False, index=True)
    date = Column(String, nullable=False, index=True)

    __table_args__ = ({"sqlite_autoincrement": True},)


Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def is_completed(db: Session, user_id: str, habit_id: str, date_str: str) -> bool:
    """Checks if habit is completed for user on specified date"""
    completion = (
        db.query(CompletionModel)
        .filter(
            CompletionModel.user_id == user_id,
            CompletionModel.habit_id == habit_id,
            CompletionModel.date == date_str,
        )
        .first()
    )
    return completion is not None


def get_all_habits(db: Session, user_id: str) -> List[dict]:
    """Gets all user habits from database"""
    habits = db.query(HabitModel).filter(HabitModel.user_id == user_id).all()
    return [
        {
            "id": habit.id,
            "name": habit.name,
            "color": habit.color,
            "created_at": (
                habit.created_at.isoformat()
                if habit.created_at
                else datetime.datetime.now().isoformat()
            ),
        }
        for habit in habits
    ]


def get_habit_by_id(db: Session, user_id: str, habit_id: str) -> dict:
    """Gets habit by ID for specific user"""
    habit = (
        db.query(HabitModel)
        .filter(HabitModel.id == habit_id, HabitModel.user_id == user_id)
        .first()
    )
    if habit:
        return {
            "id": habit.id,
            "name": habit.name,
            "color": habit.color,
            "created_at": (
                habit.created_at.isoformat()
                if habit.created_at
                else datetime.datetime.now().isoformat()
            ),
        }
    return None


def get_habits_count_by_user(db: Session, user_id: str) -> int:
    """Gets count of user habits"""
    return db.query(HabitModel).filter(HabitModel.user_id == user_id).count()


def get_max_habit_number_by_user(db: Session, user_id: str) -> int:
    """Gets maximum habit number for user to generate unique ID"""
    habits = db.query(HabitModel).filter(HabitModel.user_id == user_id).all()
    if not habits:
        return 0

    max_num = 0
    prefix = f"{user_id}_"
    for habit in habits:
        if habit.id.startswith(prefix):
            try:
                num = int(habit.id[len(prefix) :])
                max_num = max(max_num, num)
            except ValueError:
                continue

    return max_num
