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
async def trigger_report(background_tasks: BackgroundTasks):
    try:
        db = database.SessionLocal()
        
        report_id = None
        report_id = str(random.randint(1000, 9999))
        while db.query(models.Report).filter_by(id=report_id).first():
            report_id = str(random.randint(1000, 9999))
        report =   models.Report(id=report_id)
        db.add(report)
        db.commit()

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
        print("Generating report for timestamp: ", timestamp)
        db = database.SessionLocal()
        restaurants = db.query(models.StoreTimezone).all()
    
        report = []
        for restaurant in restaurants:
            print("Generating report for restaurant: ", restaurant.store_id)
            re = generateReportForRestaurant(
                restaurant.store_id, timestamp, report_id)
            report.append(re)
        print("Report generated: ", report)
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
            print("Generating report for day: ", i)
            # fetch logs for that day
            storeLogs = db.query(models.StoreLogs).filter(
                    models.StoreLogs.timestamp >= timestamp -
                    datetime.timedelta(days=i) , models.StoreLogs.timestamp <= timestamp,
                    models.StoreLogs.store_id == restaurant_id
                    ).all()

            businessHours = db.query(models.BusinessHours).filter_by(
                store_id=restaurant_id, day_of_week=day).all()
            if i == 1:
                # firstDay, consider only hours till timestamp
                uptime_minutes, downtime_minutes, upTimelastHour, downTimelastHour = generateDayRecord(
                    storeLogs, businessHours, None, timestamp)
                uptime_last_hour = upTimelastHour
                downtime_last_hour = downTimelastHour
                uptime_last_day = uptime_minutes
                downtime_last_day = downtime_minutes
                update_last_week += uptime_minutes
                downtime_last_week += downtime_minutes
            elif i == 7:
                # lastDay, consider only hours from timestamp
                uptime_minutes, downtime_minutes, upTimelastHour, downTimelastHour = generateDayRecord(
                    storeLogs, businessHours, timestamp, None)
                update_last_week += uptime_minutes
                downtime_last_week += downtime_minutes

            else:
                uptime_minutes, downtime_minutes, upTimelastHour, downTimelastHour = generateDayRecord(
                    storeLogs, businessHours)
                update_last_week += uptime_minutes
                downtime_last_week += downtime_minutes
            if (day == 0):
                day = 6
            else:
                day = day - 1

        return {
            "id":report_id,
            "store_id":restaurant_id,
            "timestamp":timestamp,
            "uptime_last_hour":uptime_last_hour,
            "uptime_last_day":uptime_last_day,
            "uptime_last_week":update_last_week,
            "downtime_last_hour":downtime_last_hour,
            "downtime_last_day":downtime_last_day,
            "downtime_last_week":downtime_last_week
        }

        

    except Exception as e:
        print("Error in generateReportForRestaurant: ", e)
        return None
    finally:
        db.close()


def generateDayRecord(logs: [models.StoreLogs],
                      hours: [models.BusinessHours],
                      fromTime: datetime.datetime | None = None,
                      till: datetime.datetime | None = None):
    try:
        print("Generating day record for logs: ")
        # generate array of 24 hours
        dayRecord = [0] * 24
        for log in logs:
            hour = log.timestamp.hour
            dayRecord[hour] = 1

        # sort hours by start time
        hours.sort(key=lambda x: x.open_time)

        hours_stack = []

        # merge overlapping hours
        for i in hours[1:]:
            if hours_stack[-1][0] <= i[0] <= hours_stack[-1][-1]:
                hours_stack[-1][-1] = max(hours_stack[-1][-1], i[-1])
            else:
                hours_stack.append(i)

        filtered_hours = []

        # only consider hours till "till"
        if till:
            for hour in hours_stack:
                if hour.open_time.hour >= till.hour:
                    if hour.close_time.hour >= till.hour:
                        hour.close_time = till
                    filtered_hours.append(hour)
        else:
            filtered_hours = hours_stack
        upTimelastHour = 0
        downTimelastHour = 0
        # only consider hours from "fromTime" & consider last hour
        if fromTime:
            for hour in filtered_hours:
                if hour.close_time.hour <= fromTime.hour:
                    filtered_hours.remove(hour)
                else:
                    if hour.open_time.hour <= fromTime.hour:
                        hour.open_time = fromTime
            # check if last hour is in filtered hours
            intervals = []
            mins = 60
            for hour in filtered_hours:
                if hour.open_time.hour <= fromTime.hour:
                    if hour.close_time.minutes >= fromTime.hour.minutes + mins:
                        intervals.append({
                            "start_time": fromTime,
                            "end_time": fromTime + datetime.timedelta(minutes=mins)
                        })
                        break
                    else:
                        intervals.append({
                            "start_time": fromTime,
                            "end_time": hour.close_time
                        })
                        fromTime = hour.close_time
                        mins = 60 - fromTime.minutes

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
