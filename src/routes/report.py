import datetime
import random
from turtle import down
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from ..schemas import response
from ..db import models, database
from fastapi import BackgroundTasks


router = APIRouter()


@router.get("/get_report/{report_id}", responses=response.general_responses)
def get_report(report_id):
    try:
        db = database.SessionLocal()
        report = db.query(models.Report).filter_by(id=report_id).first()
        if not report:
            return JSONResponse(status_code=404,
                                content={"message": "Report not found"})
        # get report file
        with open(f"report_{report_id}.txt", "w") as f:
            report = f.read()
        if report:
            return JSONResponse(status_code=200,
                                content={"message": "Report fetched successfully", "report": report})
        else:
            return JSONResponse(status_code=404,
                                content={"message": "Running report generation"})
    except Exception as e:
        print("Error in get_report: ", e)
        return JSONResponse(status_code=500,
                            content={"message": "Internal Server Error"})
    finally:
        db.close()


@router.post("/trigger_report", responses=response.general_responses)
async def trigger_report(background_tasks: BackgroundTasks, date=None):
    try:
        db = database.SessionLocal()

        report_id = None
        report_id = str(random.randint(1000, 9999))
        while db.query(models.Report).filter_by(id=report_id).first():
            report_id = str(random.randint(1000, 9999))
        report = models.Report(id=report_id)
        db.add(report)
        db.commit()
        if date:
            date = datetime.datetime.strptime(date, "%d-%m-%Y")
            print("Date: ", date)
            background_tasks.add_task(
                generateReport, date, report_id)
        else:
            background_tasks.add_task(
                generateReport, datetime.datetime.now(), report_id)

        return JSONResponse(status_code=200,
                            content={"message": "Report triggered successfully", "report_id": report_id})
    except Exception as e:
        print("Error in trigger_report: ", e)
        db.rollback()
        return JSONResponse(status_code=500,
                            content={"message": "Internal Server Error"})
    finally:
        db.close()


def generateReport(timestamp: datetime.datetime, report_id: str):
    try:
        db = database.SessionLocal()
        restaurants = db.query(models.StoreTimezone).all()

        report = []
        for restaurant in restaurants:
            re = generateReportForRestaurant(
                restaurant.store_id, timestamp, report_id)
            report.append(re)
        # save report in root directory
        with open(f"report_{report_id}.txt", "w") as f:
            f.write(str(report))
    except Exception as e:
        print("Error in generateReport: ", e)
    finally:
        db.close()


def generateReportForRestaurant(restaurant_id: str, timestamp: datetime.datetime, report_id: str):
    try:
        db = database.SessionLocal()
        day = timestamp.weekday()
        uptime_last_hour = 0
        uptime_last_day = 0
        update_last_week = 0
        downtime_last_hour = 0
        downtime_last_day = 0
        downtime_last_week = 0
        # fetch data for last 7 days
        for i in range(1, 8):
            # fetch logs for that day
            storeLogs = db.query(models.StoreLogs).filter(
                models.StoreLogs.timestamp + datetime.timedelta(days=i-1) >= timestamp -
                datetime.timedelta(
                    days=i), models.StoreLogs.timestamp <= timestamp,
                models.StoreLogs.store_id == restaurant_id
            ).all()

            businessHours = db.query(models.BusinessHours).filter_by(
                store_id=restaurant_id, day_of_week=day).all()
            if i == 1:
                # firstDay, consider only hours till timestamp
                uptime_minutes, downtime_minutes, upTimelastHour, downTimelastHour = generateDayRecord(
                    storeLogs, businessHours, None, timestamp, restaurant_id)
                uptime_last_hour = upTimelastHour
                downtime_last_hour = downTimelastHour
                uptime_last_day = uptime_minutes
                downtime_last_day = downtime_minutes
                update_last_week += uptime_minutes
                downtime_last_week += downtime_minutes
            elif i == 7:
                # lastDay, consider only hours from timestamp
                uptime_minutes, downtime_minutes, upTimelastHour, downTimelastHour = generateDayRecord(
                    storeLogs, businessHours, timestamp, None, restaurant_id)
                update_last_week += uptime_minutes
                downtime_last_week += downtime_minutes

            else:
                uptime_minutes, downtime_minutes, upTimelastHour, downTimelastHour = generateDayRecord(
                    storeLogs, businessHours, restaurant_id)
                update_last_week += uptime_minutes
                downtime_last_week += downtime_minutes
            if (day == 0):
                day = 6
            else:
                day = day - 1

        return {
            "id": report_id,
            "store_id": restaurant_id,
            "timestamp": timestamp,
            "uptime_last_hour": uptime_last_hour,
            "uptime_last_day": uptime_last_day,
            "uptime_last_week": update_last_week,
            "downtime_last_hour": downtime_last_hour,
            "downtime_last_day": downtime_last_day,
            "downtime_last_week": downtime_last_week
        }

    except Exception as e:
        print("Error in generateReportForRestaurant: ", e)
        return None
    finally:
        db.close()


def generateDayRecord(logs: [models.StoreLogs],
                      hours: [models.BusinessHours],
                      fromTime: datetime.datetime | None = None,
                      till: datetime.datetime | None = None,
                      store_id: str = None):
    try:
        # generate array of 24 hours
        dayRecord = [0] * 24
        for log in logs:
            hour = log.timestamp.hour
            print("Hour: ", hour)
            if log.status == "active":
                dayRecord[hour] = 1
        hours_stack = []
        if len(hours) == 0:

            open_time = datetime.time.fromisoformat("00:00:00")
            close_time = datetime.time.fromisoformat("23:59:59")
            obj = {"open_time": open_time,
                   "close_time": close_time, "store_id": store_id, "day_of_week": 0}
            hours_stack.append(obj)
            print(obj)

        else:
            # sort hours by start time
            hours.sort(key=lambda x: x.open_time)

            if len(hours) > 0:
                # merge overlapping hours
                for i in hours[1:]:
                    if hours_stack[-1][0] <= i[0] <= hours_stack[-1][-1]:
                        hours_stack[-1][-1] = max(hours_stack[-1][-1], i[-1])
                    else:
                        hours_stack.append(i)

        filtered_hours = []

        # only consider hours till "till"
        if fromTime:
            for hour in hours_stack:
                if hour.open_time.hour >= fromTime.hour:
                    filtered_hours.append(hour)
                elif hour.close_time.hour > fromTime.hour:
                    hour.open_time = fromTime
                    filtered_hours.append(hour)
        else:
            filtered_hours = hours_stack

        upTimelastHour = 0
        downTimelastHour = 0
        # only consider hours from "fromTime" & consider last hour
        if till:
            for hour in filtered_hours:
                if hour.open_time.hour >= till.hour:
                    filtered_hours.remove(hour)
                else:
                    if hour.close_time.hour > till.hour:
                        hour.close_time = till
            # check if last hour is in filtered hours
            intervals = []
            mins = 60
            # todo: fix last hour logic
            for hour in filtered_hours:
                if hour.open_time.hour <= till.hour:
                    if hour.close_time.minutes >= till.hour.minutes + mins:
                        intervals.append({
                            "start_time": till,
                            "end_time": till + datetime.timedelta(minutes=mins)
                        })
                        break
                    else:
                        intervals.append({
                            "start_time": till,
                            "end_time": hour.close_time
                        })
                        till = hour.close_time
                        mins = 60 - till.minutes

            for hour in intervals:
                start_time_hour = hour.open_time.hour
                end_time_hour = hour.close_time.hour
                for i in range(start_time_hour, end_time_hour):
                    mins = 60
                    if i == start_time_hour:
                        mins = 60 - hour.open_time.minute
                    elif i == end_time_hour:
                        mins = hour.close_time.minute
                    if dayRecord[i] == 1:
                        upTimelastHour += mins
                    else:
                        downTimelastHour += mins

        uptime_minutes = 0
        downtime_minutes = 0

        # calculate uptime and downtime
        for hour in filtered_hours:
            start_time_hour = hour.open_time.hour
            end_time_hour = hour.close_time.hour
            for i in range(start_time_hour, end_time_hour):
                mins = 60
                if i == start_time_hour:
                    mins = 60 - hour.open_time.minute
                elif i == end_time_hour:
                    mins = hour.close_time.minute
                if dayRecord[i] == 1:
                    uptime_minutes += mins
                else:
                    downtime_minutes += mins

        return uptime_minutes, downtime_minutes, upTimelastHour, downTimelastHour

    except Exception as e:
        print("Error in generateDayRecord: ", e)
    finally:
        pass
