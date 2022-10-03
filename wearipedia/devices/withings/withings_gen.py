import hashlib
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from tqdm import tqdm

# below is for withings scanwatch


def create_synthetic_sleeps_df():

    syn_sleeps = pd.DataFrame()

    syn_sleeps["id"] = np.random.randint(0, 100000000, size=(20,))
    syn_sleeps["timezone"] = "America/Los_Angeles"
    syn_sleeps["model"] = 16
    syn_sleeps["model_id"] = 93
    syn_sleeps[
        "hash_deviceid"
    ] = "d41d8cd98f00b204e9800998ecf8427e"  # randomly generated
    syn_sleeps["date"] = [
        datetime.fromtimestamp(
            datetime.strptime("2022-05-17", "%Y-%m-%d").timestamp() + i * 24 * 3600
        ).strftime("%Y-%m-%d")
        for i in range(20)
    ]

    startdates = []
    enddates = []

    for date in syn_sleeps["date"]:
        sleep_start = np.random.randint(20, 27)
        sleep_time = np.random.randint(4, 9)

        startdate = datetime.strptime(date, "%Y-%m-%d") + timedelta(
            hours=sleep_start + 7
        )

        enddate = startdate + timedelta(hours=sleep_time)

        startdate, enddate = int(startdate.timestamp()), int(enddate.timestamp())

        startdates.append(startdate)
        enddates.append(enddate)

    all_data = []

    for i in range(20):

        data = {
            "wakeupduration": np.random.randint(0, 3000),
            "wakeupcount": np.random.poisson(1),
            "durationtosleep": np.random.randint(120, 180),
            "durationtowakeup": np.random.randint(0, 700),
            "total_timeinbed": np.random.randint(10000, 50000),
            "total_sleep_time": np.random.randint(10000, 50000),
            "sleep_efficiency": np.random.rand() * 0.1 + 0.9,
            "sleep_latency": np.random.randint(120, 130),
            "wakeup_latency": np.random.randint(0, 800),
            "waso": np.random.randint(0, 4000),
            "nb_rem_episodes": 0,
            "out_of_bed_count": 0,
            "lightsleepduration": np.random.randint(6000, 35000),
            "deepsleepduration": np.random.randint(3000, 17000),
            "hr_average": np.random.randint(55, 65),
            "hr_min": np.random.randint(40, 60),
            "hr_max": np.random.randint(70, 120),
            "sleep_score": np.random.randint(30, 80),
        }

        all_data.append(data)

    syn_sleeps["startdate"] = startdates
    syn_sleeps["enddate"] = enddates

    syn_sleeps["data"] = all_data

    syn_sleeps["created"] = enddates
    syn_sleeps["modified"] = enddates

    return syn_sleeps


def create_syn_hr(syn_sleeps):
    start_day = datetime.strptime("2022-05-20", "%Y-%m-%d")

    hour_usage = [0.8] * 3 + [0.9] * 7 + [1.0] * 10 + [0.9] * 4

    datetimes = []

    for day_offset in tqdm(range(20)):
        for hour_offset in range(24):
            for minute_offset in range(0, 60, 10):
                day = start_day + timedelta(days=day_offset)
                hour = day + timedelta(hours=hour_offset)
                minute = hour + timedelta(minutes=minute_offset)

                if np.random.uniform(0, 1) < hour_usage[hour_offset]:
                    datetimes.append(minute)

    hr_measurements = (np.random.randn(len(datetimes)) * 5 + 90).astype("int")

    timestamps = np.array([dt.timestamp() for dt in datetimes])

    for i, (startdate, enddate) in tqdm(
        enumerate(zip(syn_sleeps.startdate, syn_sleeps.enddate))
    ):
        idxes = np.where(np.logical_and(timestamps > startdate, timestamps < enddate))[
            0
        ]
        duration = (enddate - startdate) / 3600
        avg_hr = -5 / 7 * duration + 64.1428571429

        hr_measurements[idxes] = (np.random.randn(idxes.shape[0]) + avg_hr).astype(
            "int"
        )

    syn_hr = pd.DataFrame()
    syn_hr["datetime"] = datetimes
    syn_hr["heart_rate"] = hr_measurements

    syn_hr["model"] = "ScanWatch"
    syn_hr["model_id"] = 93
    syn_hr["deviceid"] = hashlib.md5().hexdigest()

    num_garbage = 1000

    timestamps_garbage = np.random.uniform(
        (start_day - timedelta(days=100)).timestamp(),
        start_day.timestamp(),
        size=num_garbage,
    )

    garbage_df = pd.DataFrame()
    garbage_df["datetime"] = [
        datetime.fromtimestamp(int(ts)) for ts in timestamps_garbage
    ]
    garbage_df["heart_rate"] = (np.random.randn(num_garbage) * 5 + 90).astype("int")

    garbage_df["model"] = None
    garbage_df["model_id"] = 1059
    garbage_df["deviceid"] = None

    syn_hr = pd.concat((garbage_df, syn_hr), ignore_index=True)

    return syn_hr