import csv
from datetime import datetime, time
from pytz import timezone

from fastapi import APIRouter, UploadFile
from fastapi.responses import JSONResponse
from ..schemas import response
from ..db import models, database
router = APIRouter()


@router.post("/timezone", responses=response.general_responses)
def sync_timezone(file: UploadFile):
    """Sync timezone data."""
    try:
        db = database.SessionLocal()

        csv_text = file.file.read().decode("utf-8")

        # Read CSV file
        csv_reader = csv.reader(csv_text.splitlines(), delimiter=",")

        # Skip the header row
        next(csv_reader)

        # Parse and insert CSV data into the database
        for row in csv_reader:
            store_id, timezone_str = row
            store_timezone = models.StoreTimezone(
                store_id=store_id, timezone_str=timezone_str)
            db.add(store_timezone)

        db.commit()
        return JSONResponse(status_code=200,
                            content={"message": "Data synced successfully"})

    except Exception as e:
        print("Error in sync_timezone: ", e)
        db.rollback()
        return JSONResponse(status_code=500,
                            content={"message": "Internal Server Error"})
    finally:
        db.close()


@router.post("/logs", responses=response.general_responses)
def sync_logs(file: UploadFile):
    """Sync logs data."""
    try:
        db = database.SessionLocal()

        csv_text = file.file.read().decode("utf-8")

        # Read CSV file
        csv_reader = csv.reader(csv_text.splitlines(), delimiter=",")

        # Skip the header row
        next(csv_reader)

        # Fetch all store ids with their timezone
        store_timezones = db.query(models.StoreTimezone).all()

        # Parse and insert CSV data into the database
        for row in csv_reader:
            store_id, status, timestamp_utc = row

            # Convert UTC timestamp to store timezone timestamp
            time_zone = "America/Chicago"
            for store_timezone in store_timezones:
                if store_timezone.store_id == store_id:
                    time_zone = store_timezone.timezone_str
                    break
            timestamp_utc = timestamp_utc.replace("UTC", "").strip()

            if timestamp_utc.find(".") != -1:
                timestamp_utc = datetime.strptime(
                    timestamp_utc, "%Y-%m-%d %H:%M:%S.%f").replace(tzinfo=timezone(time_zone))
            else:
                timestamp_utc = datetime.strptime(
                    timestamp_utc, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone(time_zone))

            status_type = models.StoreStatus.ACTIVE if status == "ACTIVE" else models.StoreStatus.INACTIVE
            store_log = models.StoreLogs(
                store_id=store_id, status=status_type, timestamp=timestamp_utc)

            db.add(store_log)
        print("Done")
        db.commit()
        return JSONResponse(status_code=200,
                            content={"message": "Data synced successfully"})

    except Exception as e:
        print("Error in sync_logs: ", e)
        db.rollback()
        return JSONResponse(status_code=500,
                            content={"message": "Internal Server Error"})
    finally:
        db.close()


@router.post("/business_hours", responses=response.general_responses)
def sync_business_hours(file: UploadFile):
    """Sync business hours data."""
    try:
        db = database.SessionLocal()

        csv_text = file.file.read().decode("utf-8")

        # Read CSV file
        csv_reader = csv.reader(csv_text.splitlines(), delimiter=",")

        # Skip the header row
        next(csv_reader)

        # Parse and insert CSV data into the database
        for row in csv_reader:
            store_id, day_of_week, open_time, close_time = row
            open_time = time.fromisoformat(open_time)
            close_time = time.fromisoformat(close_time)
            business_hours = models.BusinessHours(
                store_id=store_id, day_of_week=day_of_week, open_time=open_time, close_time=close_time)
            db.add(business_hours)

        db.commit()
        return JSONResponse(status_code=200,
                            content={"message": "Data synced successfully"})

    except Exception as e:
        print("Error in sync_business_hours: ", e)
        db.rollback()
        return JSONResponse(status_code=500,
                            content={"message": "Internal Server Error"})
    finally:
        db.close()
