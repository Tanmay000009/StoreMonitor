import csv
from fastapi import APIRouter, UploadFile
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
        return {"message": "Success"}
    except Exception as e:
        db.rollback()
        return {"message": "Error", "detail": str(e)}
    finally:
        db.close()
