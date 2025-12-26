"""Helper functions for HTML generation"""

from typing import Dict
from datetime import date as date_type
import datetime


def generate_completion_button(
    habit_id: str,
    date: str,
    context: str,
    completed: bool,
    habit: Dict,
    day_num: int,
    user_id: str = None,
) -> str:
    """Generates HTML for habit completion button"""
    today = datetime.date.today().strftime("%Y-%m-%d")
    is_today = date == today

    habit_id_escaped = habit_id.replace('"', "&quot;")
    date_escaped = date.replace('"', "&quot;")
    user_id_escaped = (user_id or "").replace('"', "&quot;")

    if context == "week":
        cls = "text-white" if completed else "bg-gray-200 hover:bg-gray-300"
        style = f'background-color: {habit["color"]}' if completed else ""
        content = (
            '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">'
            '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>'
            "</svg>"
            if completed
            else str(day_num)
        )
        return (
            f'<form hx-post="/completions" hx-target="this" hx-swap="outerHTML" hx-params="*" enctype="application/x-www-form-urlencoded" style="display: inline-block; margin: 0;">'
            f'<input type="hidden" name="habit_id" value="{habit_id_escaped}">'
            f'<input type="hidden" name="date" value="{date_escaped}">'
            f'<input type="hidden" name="context" value="week">'
            f'<input type="hidden" name="user_id" value="{user_id_escaped}">'
            f'<button type="submit" '
            f'class="w-10 h-10 rounded-lg flex items-center justify-center text-xs transition-all {cls}" '
            f'style="{style}">{content}</button>'
            f"</form>"
        )
    else:
        cls = "text-white" if completed else "hover:bg-gray-100"
        style = f'background-color: {habit["color"]}' if completed else ""
        ring_class = "ring-2 ring-blue-500" if is_today else ""
        return (
            f'<form hx-post="/completions" hx-target="this" hx-swap="outerHTML" hx-params="*" enctype="application/x-www-form-urlencoded" style="display: inline-block; margin: 0;">'
            f'<input type="hidden" name="habit_id" value="{habit_id_escaped}">'
            f'<input type="hidden" name="date" value="{date_escaped}">'
            f'<input type="hidden" name="context" value="month">'
            f'<input type="hidden" name="user_id" value="{user_id_escaped}">'
            f'<button type="submit" '
            f'class="aspect-square p-2 rounded-lg text-sm transition-all {ring_class} {cls}" '
            f'style="{style}">{day_num}</button>'
            f"</form>"
        )
