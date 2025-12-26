from fastapi import FastAPI, Request, Form, Depends, Query, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date
from app.templates_helpers import generate_completion_button
from app.telegram_auth import get_user_id_dependency
from dotenv import load_dotenv
from pathlib import Path


from app.database import (
    get_db, HabitModel, CompletionModel, 
    get_all_habits, get_habit_by_id, get_habits_count_by_user, get_max_habit_number_by_user
)
from app.utils import (
    get_week_days,
    get_week_day_names,
    get_calendar_data,
    get_period_dates,
    format_date_for_display,
    get_habit_color,
)
from app.services import (
    enrich_habits_with_completions,
    calculate_streaks,
    calculate_completion_rate,
    get_completions_batch,
)


BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_FILE if ENV_FILE.exists() else None)

TEMPLATES_DIR = BASE_DIR / "templates"

app = FastAPI(
    title="Habit Tracker",
    description="Habit tracker with calendar and reports",
    version="1.0.0"
)
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@app.middleware("http")
async def log_completions_requests(request: Request, call_next):
    if request.url.path == "/completions" and request.method == "POST":
        import logging
        logger = logging.getLogger(__name__)
        content_type = request.headers.get("content-type", "")
        content_length = request.headers.get("content-length", "")
        logger.info(f"[DEBUG /completions] Request Content-Type: {content_type}")
        logger.info(f"[DEBUG /completions] Request Content-Length: {content_length}")
        logger.info(f"[DEBUG /completions] Request URL: {request.url}")
        logger.info(f"[DEBUG /completions] Request method: {request.method}")
    
    response = await call_next(request)
    return response



@app.get("/", response_class=HTMLResponse)
async def read_root(
    request: Request,
    user_id: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Main page with weekly calendar"""
    if not user_id:
        return HTMLResponse("""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>CloudHabit</title>
            <script src="https://telegram.org/js/telegram-web-app.js"></script>
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                    margin: 0;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                }
                .loader {
                    text-align: center;
                    color: white;
                }
                .spinner {
                    border: 4px solid rgba(255, 255, 255, 0.3);
                    border-top: 4px solid white;
                    border-radius: 50%;
                    width: 40px;
                    height: 40px;
                    animation: spin 1s linear infinite;
                    margin: 0 auto 20px;
                }
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
                .error {
                    margin-top: 20px;
                    padding: 15px;
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 8px;
                    max-width: 300px;
                }
            </style>
        </head>
        <body>
            <div class="loader">
                <div class="spinner"></div>
                <p id="status">Loading CloudHabit...</p>
                <div id="error" class="error" style="display: none;"></div>
            </div>
            <script>
                function getUserId() {
                    try {
                        // Try to get from Telegram WebApp
                        if (window.Telegram && window.Telegram.WebApp) {
                            window.Telegram.WebApp.ready();
                            const initDataUnsafe = window.Telegram.WebApp.initDataUnsafe;
                            if (initDataUnsafe && initDataUnsafe.user && initDataUnsafe.user.id) {
                                return initDataUnsafe.user.id.toString();
                            }
                        }
                    } catch (e) {
                        console.error('Error getting Telegram user ID:', e);
                    }
                    return null;
                }
                
                // Wait for Telegram SDK to initialize
                setTimeout(() => {
                    const userId = getUserId();
                    if (userId) {
                        // Redirect to main page with user_id
                        window.location.href = '/?user_id=' + userId;
                    } else {
                        // Show error message
                        document.getElementById('status').textContent = 'Unable to authenticate';
                        const errorDiv = document.getElementById('error');
                        errorDiv.style.display = 'block';
                        errorDiv.innerHTML = 'Please open this app from Telegram Mini Apps.<br><br>For development: <a href="/?user_id=demo_user" style="color: white; text-decoration: underline;">Click here</a>';
                    }
                }, 800);
            </script>
        </body>
        </html>
        """)
    
    week_days = get_week_days()
    week_names = get_week_day_names()
    habits = get_all_habits(db, user_id)
    
    habits_with_completions = enrich_habits_with_completions(db, user_id, habits, week_days)
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "habits": habits_with_completions,
        "week_days": week_days,
        "week_names": week_names,
        "user_id": user_id,
    })


@app.get("/habits-list", response_class=HTMLResponse)
async def get_habits_list(
    request: Request,
    user_id: str = Depends(get_user_id_dependency),
    db: Session = Depends(get_db)
):
    """Endpoint to get updated habits list (for synchronization)"""
    week_days = get_week_days()
    week_names = get_week_day_names()
    habits = get_all_habits(db, user_id)
    
    habits_with_completions = enrich_habits_with_completions(db, user_id, habits, week_days)
    
    return templates.TemplateResponse("habits_list.html", {
        "request": request,
        "habits": habits_with_completions,
        "week_days": week_days,
        "week_names": week_names,
        "user_id": user_id,
    })


@app.get("/calendar", response_class=HTMLResponse)
async def get_calendar(
    request: Request,
    user_id: str = Depends(get_user_id_dependency),
    year: Optional[int] = None,
    month: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Page with monthly calendar"""
    today = date.today()
    year = year or today.year
    month = month or today.month
    
    cal, month_name = get_calendar_data(year, month)
    today_str = today.strftime("%Y-%m-%d")
    
    month_dates = []
    for week in cal:
        for day in week:
            if day != 0:
                month_dates.append(f"{year}-{month:02d}-{day:02d}")
    
    habits = get_all_habits(db, user_id)
    
    if habits:
        date_strs = month_dates
        habit_ids = [h["id"] for h in habits]
        completions_map = get_completions_batch(db, user_id, habit_ids, date_strs)
        
        day_completions = {}
        for date_str in month_dates:
            completed_count = sum(
                1 for habit_id in habit_ids
                if completions_map.get((habit_id, date_str), False)
            )
            percentage = round((completed_count / len(habits)) * 100) if habits else 0
            day_completions[date_str] = {
                "completed": completed_count,
                "total": len(habits),
                "percentage": percentage
            }
    else:
        day_completions = {date_str: {"completed": 0, "total": 0, "percentage": 0} for date_str in month_dates}
    
    return templates.TemplateResponse("calendar.html", {
        "request": request,
        "habits": habits,
        "calendar": cal,
        "month_name": month_name,
        "year": year,
        "month": month,
        "today": today_str,
        "user_id": user_id,
        "day_completions": day_completions,
    })


@app.get("/reports", response_class=HTMLResponse)
async def get_reports(
    request: Request,
    user_id: str = Depends(get_user_id_dependency),
    period: str = "7days",
    db: Session = Depends(get_db)
):
    """Page with reports and statistics"""
    dates = get_period_dates(period)
    habits = get_all_habits(db, user_id)
    
    if not habits:
        return templates.TemplateResponse("reports.html", {
            "request": request,
            "habits": [],
            "chart_data": [],
            "period": period,
        })
    
    date_strs = [d.strftime("%Y-%m-%d") for d in dates]
    habit_ids = [h["id"] for h in habits]
    completions_map = get_completions_batch(db, user_id, habit_ids, date_strs)
    
    chart_data = []
    for d in dates:
        date_str = d.strftime("%Y-%m-%d")

        total_completed = sum(
            1 for habit in habits 
            if completions_map.get((habit["id"], date_str), False)
        )
        data_point = {
            "date": format_date_for_display(d),
            "total_completed": total_completed
        }

        for habit in habits:
            data_point[habit["name"]] = 1 if completions_map.get((habit["id"], date_str), False) else 0
        chart_data.append(data_point)
    
    habits_with_stats = []
    for habit in habits:
        streaks = calculate_streaks(db, user_id, habit["id"], dates)
        completion_rate = calculate_completion_rate(db, user_id, habit["id"], dates)
        
        habits_with_stats.append({
            **habit,
            "completion_rate": completion_rate,
            "current_streak": streaks["current_streak"],
            "max_streak": streaks["max_streak"],
        })
    
    return templates.TemplateResponse("reports.html", {
        "request": request,
        "habits": habits_with_stats,
        "chart_data": chart_data,
        "period": period,
        "user_id": user_id,
    })

@app.post("/habits")
async def add_habit(
    request: Request,
    name: str = Form(...),
    user_id: str = Form(...),
    db: Session = Depends(get_db)
):
    """Add new habit"""
    import datetime
    
    max_habit_num = get_max_habit_number_by_user(db, user_id)r
    habit_id = f"{user_id}_{max_habit_num + 1}"
    habits_count = get_habits_count_by_user(db, user_id)
    color = get_habit_color(habits_count)
    
    new_habit = HabitModel(
        id=habit_id,
        user_id=user_id,
        name=name,
        color=color,
        created_at=datetime.datetime.now()
    )
    db.add(new_habit)
    db.commit()
    db.refresh(new_habit)
    
    week_days = get_week_days()
    week_names = get_week_day_names()
    habits = get_all_habits(db, user_id)
    habits_with_completions = enrich_habits_with_completions(db, user_id, habits, week_days)
    
    response = templates.TemplateResponse("habits_list.html", {
        "request": request,
        "habits": habits_with_completions,
        "week_days": week_days,
        "week_names": week_names,
        "user_id": user_id,
    })
    response.headers['HX-Trigger'] = 'habitChanged'
    return response


@app.delete("/habits/{habit_id}")
async def delete_habit(
    request: Request,
    habit_id: str,
    user_id: str = Depends(get_user_id_dependency),
    db: Session = Depends(get_db)
):
    """Delete habit"""
    habit = db.query(HabitModel).filter(
        HabitModel.id == habit_id,
        HabitModel.user_id == user_id
    ).first()
    
    if habit:
        db.query(CompletionModel).filter(
            CompletionModel.habit_id == habit_id,
            CompletionModel.user_id == user_id
        ).delete()
        db.delete(habit)
        db.commit()
    
    week_days = get_week_days()
    week_names = get_week_day_names()
    habits = get_all_habits(db, user_id)
    habits_with_completions = enrich_habits_with_completions(db, user_id, habits, week_days)
    
    response = templates.TemplateResponse("habits_list.html", {
        "request": request,
        "habits": habits_with_completions,
        "week_days": week_days,
        "week_names": week_names,
        "user_id": user_id,
    })
    response.headers['HX-Trigger'] = 'habitChanged'
    return response


@app.post("/completions")
async def toggle_completion(
    request: Request,
    db: Session = Depends(get_db)
):
    """Toggle habit completion status"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        content_type = request.headers.get('content-type', '')
        content_length = request.headers.get('content-length', '')
        logger.info(f"[DEBUG /completions] Content-Type: {content_type}")
        logger.info(f"[DEBUG /completions] Content-Length: {content_length}")
        logger.info(f"[DEBUG /completions] Request method: {request.method}")
        logger.info(f"[DEBUG /completions] Request URL: {request.url}")
        logger.info(f"[DEBUG /completions] All headers: {dict(request.headers)}")
        
        habit_id = None
        date = None
        context = "week"
        user_id = None
        
        try:
            body_bytes = await request.body()
            body_str = body_bytes.decode('utf-8') if body_bytes else ""
            logger.info(f"[DEBUG /completions] Request body (raw): '{body_str}'")
            logger.info(f"[DEBUG /completions] Request body length: {len(body_str)}")
            
            if body_str:
                import urllib.parse
                parsed_data = urllib.parse.parse_qs(body_str)
                logger.info(f"[DEBUG /completions] Parsed body: {parsed_data}")
                
                habit_id = parsed_data.get("habit_id", [None])[0]
                date = parsed_data.get("date", [None])[0]
                context = parsed_data.get("context", ["week"])[0]
                user_id = parsed_data.get("user_id", [None])[0]
                
                logger.info(f"[DEBUG /completions] Parsed values: habit_id={habit_id}, date={date}, context={context}, user_id={user_id}")
            else:
                logger.error(f"[DEBUG /completions] Body is empty!")
        except Exception as e:
            logger.error(f"[DEBUG /completions] Error reading/parsing body: {e}")
            import traceback
            logger.error(f"[DEBUG /completions] Traceback: {traceback.format_exc()}")
        
        
        if not habit_id or not date or not user_id:
            logger.error(f"[DEBUG /completions] Missing required fields: habit_id={habit_id}, date={date}, user_id={user_id}")
            raise HTTPException(
                status_code=422,
                detail=f"Missing required fields: habit_id={habit_id}, date={date}, user_id={user_id}"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[DEBUG /completions] Error parsing form: {e}")
        raise HTTPException(
            status_code=422,
            detail=f"Error parsing form data: {str(e)}"
        )
    
    if context is None:
        context = "week"
    
    habit = get_habit_by_id(db, user_id, habit_id)
    if habit is None:
        return HTMLResponse(
            f"<div class='text-red-500'>Habit with id {habit_id} not found</div>",
            status_code=404
        )
    
    existing = db.query(CompletionModel).filter(
        CompletionModel.user_id == user_id,
        CompletionModel.habit_id == habit_id,
        CompletionModel.date == date
    ).first()
    
    if existing:
        db.delete(existing)
        completed = False
    else:
        new_completion = CompletionModel(
            user_id=user_id,
            habit_id=habit_id,
            date=date
        )
        db.add(new_completion)
        completed = True
    
    db.commit()
    
    day_num = int(date.split('-')[2])
    button_html = generate_completion_button(habit_id, date, context, completed, habit, day_num, user_id)
    
    response = HTMLResponse(button_html)
    response.headers['HX-Trigger'] = 'habitChanged'
    return response

