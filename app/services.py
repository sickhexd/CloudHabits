"""Services for application business logic"""
from typing import List, Dict, Set
from datetime import date
from sqlalchemy.orm import Session
from app.database import HabitModel, CompletionModel, get_all_habits


def get_completions_batch(
    db: Session,
    user_id: str,
    habit_ids: List[str],
    dates: List[str]
) -> Dict[tuple, bool]:
    """
    Optimized function to get completions in one query.
    Returns dictionary {(habit_id, date): True/False}
    """
    if not habit_ids or not dates:
        return {}
    
    completions = db.query(CompletionModel).filter(
        CompletionModel.user_id == user_id,
        CompletionModel.habit_id.in_(habit_ids),
        CompletionModel.date.in_(dates)
    ).all()
    
    completion_set = {(c.habit_id, c.date) for c in completions}
    
    result = {}
    for habit_id in habit_ids:
        for date_str in dates:
            result[(habit_id, date_str)] = (habit_id, date_str) in completion_set
    
    return result


def enrich_habits_with_completions(
    db: Session,
    user_id: str,
    habits: List[Dict],
    dates: List[str]
) -> List[Dict]:
    
    if not habits:
        return []
    
    habit_ids = [h["id"] for h in habits]
    completions_map = get_completions_batch(db, user_id, habit_ids, dates)
    
    enriched_habits = []
    for habit in habits:
        habit_completions = {
            date_str: completions_map.get((habit["id"], date_str), False)
            for date_str in dates
        }
        enriched_habits.append({**habit, "completions": habit_completions})
    
    return enriched_habits


def calculate_streaks(
    db: Session,
    user_id: str,
    habit_id: str,
    dates: List[date]
) -> Dict[str, int]:
    """
    Calculates current and maximum streaks for habit.
    Returns {'current_streak': int, 'max_streak': int}
    """
    if not dates:
        return {"current_streak": 0, "max_streak": 0}
    
    date_strs = [d.strftime("%Y-%m-%d") for d in dates]
    completions = db.query(CompletionModel).filter(
        CompletionModel.user_id == user_id,
        CompletionModel.habit_id == habit_id,
        CompletionModel.date.in_(date_strs)
    ).all()
    
    completion_set = {c.date for c in completions}
    
    sorted_dates = sorted(dates, reverse=True)
    
    current_streak = 0
    for d in sorted_dates:
        date_str = d.strftime("%Y-%m-%d")
        if date_str in completion_set:
            current_streak += 1
        else:
            break
    
    max_streak = 0
    temp_streak = 0
    for d in sorted_dates:
        date_str = d.strftime("%Y-%m-%d")
        if date_str in completion_set:
            temp_streak += 1
            max_streak = max(max_streak, temp_streak)
        else:
            temp_streak = 0
    
    return {"current_streak": current_streak, "max_streak": max_streak}


def calculate_completion_rate(
    db: Session,
    user_id: str,
    habit_id: str,
    dates: List[date]
) -> int:
    """Calculates habit completion rate for period"""
    if not dates:
        return 0
    
    date_strs = [d.strftime("%Y-%m-%d") for d in dates]
    completed_count = db.query(CompletionModel).filter(
        CompletionModel.user_id == user_id,
        CompletionModel.habit_id == habit_id,
        CompletionModel.date.in_(date_strs)
    ).count()
    
    return round((completed_count / len(dates)) * 100)

