import time
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from ..schemas import response
from ..db import models, database


router = APIRouter()


@router.get("/timezone", responses=response.general_responses)
def get_timezone(skip: int = 0, limit: int = 20, search: str = None):
    """Get all timezone data."""
    try:
        db = database.SessionLocal()
        store_timezones = None
        if search:
            store_timezones = (
                db.query(models.StoreTimezone)
                .filter(models.StoreTimezone.timezone_str.like(f"%{search}%"))
                .offset(skip)
                .limit(limit)
                .all()
            )
        else:
            store_timezones = (
                db.query(models.StoreTimezone).offset(skip).limit(limit).all()
            )
        if not store_timezones:
            return JSONResponse(status_code=404, content={"message": "Not Found"})
        timezone_list = []
        for store_timezone in store_timezones:
            timezone_list.append(
                {
                    "store_id": store_timezone.store_id,
                    "timezone_str": store_timezone.timezone_str,
                }
            )
        return JSONResponse(
            status_code=200, content={"message": "success", "data": timezone_list}
        )

    except Exception as e:
        print("Error in get_timezone: ", e)
        return JSONResponse(
            status_code=500, content={"message": "Internal Server Error"}
        )
    finally:
        db.close()


@router.get("/timezone/{id}", responses=response.general_responses)
def get_timezone_by_id(id):
    """Get timezone data by id."""
    try:
        db = database.SessionLocal()
        store_timezones = (
            db.query(models.StoreTimezone)
            .filter(models.StoreTimezone.store_id == id)
            .first()
        )

        if not store_timezones:
            return JSONResponse(status_code=404, content={"message": "Not Found"})
        timezone_list = []
        for store_timezone in store_timezones:
            timezone_list.append(
                {
                    "store_id": store_timezone.store_id,
                    "timezone_str": store_timezone.timezone_str,
                }
            )
        return JSONResponse(
            status_code=200, content={"message": "success", "data": timezone_list}
        )

    except Exception as e:
        print("Error in get_timezone_by_id: ", e)
        return JSONResponse(
            status_code=500, content={"message": "Internal Server Error"}
        )
    finally:
        db.close()


@router.get("/logs", responses=response.general_responses)
def get_logs(skip: int = 0, limit: int = 20):
    """Get all logs."""
    try:
        db = database.SessionLocal()
        store_timezones = db.query(models.StoreLogs).offset(
            skip).limit(limit).all()

        if not store_timezones:
            return JSONResponse(status_code=404, content={"message": "Not Found"})
        timezone_list = []
        for store_timezone in store_timezones:
            timezone_str = (
                store_timezone.timestamp.strftime(
                    "%Y-%m-%d %H:%M:%S.%f %z") + " UTC"
            )

            timezone_list.append(
                {"store_id": store_timezone.store_id, "timezone_str": timezone_str}
            )
        return JSONResponse(
            status_code=200, content={"message": "success", "data": timezone_list}
        )

    except Exception as e:
        print("Error in get_logs: ", e)
        return JSONResponse(
            status_code=500, content={"message": "Internal Server Error"}
        )
    finally:
        db.close()


@router.get("/logs/{id}", responses=response.general_responses)
def get_logs_by_id(id):
    """Get logs by id."""
    try:
        db = database.SessionLocal()
        store_timezones = (
            db.query(models.StoreLogs).filter(
                models.StoreLogs.store_id == id).first()
        )

        if not store_timezones:
            return JSONResponse(status_code=404, content={"message": "Not Found"})
        timezone_list = []
        for store_timezone in store_timezones:
            timezone_str = (
                store_timezone.timestamp.strftime(
                    "%Y-%m-%d %H:%M:%S.%f %z") + " UTC"
            )

            timezone_list.append(
                {"store_id": store_timezone.store_id, "timezone_str": timezone_str}
            )
        return JSONResponse(
            status_code=200, content={"message": "success", "data": timezone_list}
        )

    except Exception as e:
        print("Error in get_logs_by_id: ", e)
        return JSONResponse(
            status_code=500, content={"message": "Internal Server Error"}
        )
    finally:
        db.close()


@router.get("/business_hours", responses=response.general_responses)
def get_business_hours(
    skip: int = 0, limit: int = 20,  searchDay: str = None
):
    """Get all business_hours."""
    try:
        db = database.SessionLocal()

        store_timezones = None
        if searchDay:
            store_timezones = (
                db.query(models.BusinessHours)
                .filter(models.BusinessHours.day_of_week == int(searchDay))
                .offset(skip)
                .limit(limit)
                .all()
            )
        else:
            store_timezones = (
                db.query(models.BusinessHours).offset(skip).limit(limit).all()
            )

        if not store_timezones:
            return JSONResponse(status_code=404, content={"message": "Not Found"})
        timezone_list = []
        for store_timezone in store_timezones:
            open_time = store_timezone.open_time.strftime("%H:%M:%S")
            close_time = store_timezone.close_time.strftime("%H:%M:%S")

            timezone_list.append(
                {
                    "store_id": store_timezone.store_id,
                    "day_of_week": store_timezone.day_of_week,
                    "open_time": open_time,
                    "close_time": close_time,
                }
            )
        return JSONResponse(
            status_code=200, content={"message": "success", "data": timezone_list}
        )

    except Exception as e:
        print("Error in get_business_hours: ", e)
        return JSONResponse(
            status_code=500, content={"message": "Internal Server Error"}
        )
    finally:
        db.close()


@router.get("/business_hours/{id}", responses=response.general_responses)
def get_business_hours_by_id(id):
    """Get business_hours by id."""
    try:
        db = database.SessionLocal()
        store_hours = (
            db.query(models.BusinessHours)
            .filter(models.BusinessHours.store_id == id)
            .all()
        )
        if not store_hours:
            return JSONResponse(status_code=404, content={"message": "Not Found"})
        store_hours_list = []
        for store_hour in store_hours:
            open_time = store_hour.open_time.strftime("%H:%M:%S")
            close_time = store_hour.close_time.strftime("%H:%M:%S")

            store_hours_list.append(
                {
                    "store_id": store_hour.store_id,
                    "day_of_week": store_hour.day_of_week,
                    "open_time": open_time,
                    "close_time": close_time,
                }
            )
        return JSONResponse(
            status_code=200, content={"message": "success", "data": store_hours_list}
        )

    except Exception as e:
        print("Error in get_business_hours_by_id: ", e)
        return JSONResponse(
            status_code=500, content={"message": "Internal Server Error"}
        )
    finally:
        db.close()


@router.post("/drop/logs", responses=response.general_responses)
def drop_logs():
    """Drop logs data."""
    try:
        db = database.SessionLocal()
        db.query(models.StoreLogs).delete()
        db.commit()
        return JSONResponse(status_code=200, content={"message": "success"})

    except Exception as e:
        print("Error in drop_logs: ", e)
        return JSONResponse(
            status_code=500, content={"message": "Internal Server Error"}
        )
    finally:
        db.close()


@router.post("/drop/timezone", responses=response.general_responses)
def drop_timezone():
    """Drop timezone data."""
    try:
        db = database.SessionLocal()
        db.query(models.StoreTimezone).delete()
        db.commit()
        return JSONResponse(status_code=200, content={"message": "success"})

    except Exception as e:
        print("Error in drop_timezone: ", e)
        return JSONResponse(
            status_code=500, content={"message": "Internal Server Error"}
        )
    finally:
        db.close()


@router.post("/drop/business_hours", responses=response.general_responses)
def drop_business_hours():
    """Drop business_hours data."""
    try:
        db = database.SessionLocal()
        db.query(models.BusinessHours).delete()
        db.commit()
        return JSONResponse(status_code=200, content={"message": "success"})

    except Exception as e:
        print("Error in drop_business_hours: ", e)
        return JSONResponse(
            status_code=500, content={"message": "Internal Server Error"}
        )
    finally:
        db.close()
