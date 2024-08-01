# from django.db.models import (
#     OuterRef,
#     Subquery,
#     F,
#     ExpressionWrapper,
#     DurationField,
#     Count,
# )
# from django.db.models.functions import TruncMonth
# from django.utils import timezone
# from base.models import *

# pickup_time = RideEvent.objects.filter(
#     id_ride=OuterRef("pk"), description="Status changed to pickup"
# ).values("created_at")[:1]

# # Subquery to get the dropoff time
# dropoff_time = RideEvent.objects.filter(
#     id_ride=OuterRef("pk"), description="Status changed to dropoff"
# ).values("created_at")[:1]

# # Annotate each ride with its pickup and dropoff times
# rides_with_times = Ride.objects.annotate(
#     time_of_pickup=Subquery(pickup_time), time_of_dropoff=Subquery(dropoff_time)
# )

# # Calculate the duration of each ride
# rides_with_duration = rides_with_times.annotate(
#     duration=ExpressionWrapper(
#         F("time_of_dropoff") - F("time_of_pickup"), output_field=DurationField()
#     )
# )

# # Filter rides that took more than 1 hour
# long_rides = rides_with_duration.filter(duration__gt=timezone.timedelta(hours=1))

# # Annotate month and count rides by month and driver
# rides_count = (
#     long_rides.annotate(month=TruncMonth("pickup_time"))
#     .values("id_driver", "month")
#     .annotate(ride_count=Count("id_ride"))
#     .order_by("id_driver", "month")
# )


# with connection.cursor() as cursor:
#     cursor.execute(
#         """
#         WITH RideTimes AS (
#             SELECT r.id_ride,
#                    (SELECT created_at
#                     FROM base_rideevent
#                     WHERE id_ride = r.id_ride
#                       AND description = 'Status changed to pickup'
#                     ORDER BY created_at
#                     LIMIT 1) AS time_of_pickup,
#                    (SELECT created_at
#                     FROM base_rideevent
#                     WHERE id_ride = r.id_ride
#                       AND description = 'Status changed to dropoff'
#                     ORDER BY created_at
#                     LIMIT 1) AS time_of_dropoff
#             FROM base_ride r
#         ),
#         RideDurations AS (
#             SELECT id_ride,
#                    time_of_pickup,
#                    time_of_dropoff,
#                    (julianday(time_of_dropoff) - julianday(time_of_pickup)) * 86400 AS duration_seconds
#             FROM RideTimes
#             WHERE time_of_pickup IS NOT NULL AND time_of_dropoff IS NOT NULL
#         )
#         SELECT COUNT(id_ride) AS ride_count
#         FROM RideDurations rd
#         WHERE rd.duration_seconds > 3600
#     """
#     )
#     rows = cursor.fetchall()
#     for row in rows:
#         print(row)


# from django.db import connection

# with connection.cursor() as cursor:
#     cursor.execute(
#         """
#         WITH RideTimes AS (
#             SELECT r.id_ride,
#                    (SELECT created_at
#                     FROM base_rideevent
#                     WHERE id_ride = r.id_ride
#                       AND description = 'Status changed to pickup'
#                     ORDER BY created_at
#                     LIMIT 1) AS time_of_pickup,
#                    (SELECT created_at
#                     FROM base_rideevent
#                     WHERE id_ride = r.id_ride
#                       AND description = 'Status changed to dropoff'
#                     ORDER BY created_at
#                     LIMIT 1) AS time_of_dropoff
#             FROM base_ride r
#         ),
#         RideDurations AS (
#             SELECT id_ride,
#                    time_of_pickup,
#                    time_of_dropoff,
#                    (julianday(time_of_dropoff) - julianday(time_of_pickup)) * 86400 AS duration_seconds
#             FROM RideTimes
#             WHERE time_of_pickup IS NOT NULL AND time_of_dropoff IS NOT NULL
#         )
#         SELECT u.first_name || ' ' || u.last_name AS driver_name,
#                strftime('%Y-%m', rd.time_of_pickup) AS month,
#                COUNT(rd.id_ride) AS ride_count
#         FROM base_ride r
#         JOIN RideDurations rd ON r.id_ride = rd.id_ride
#         JOIN base_user u ON r.id_driver = u.id_user
#         WHERE rd.duration_seconds > 3600
#         GROUP BY driver_name, month
#         ORDER BY driver_name, month;
#     """
#     )
#     rows = cursor.fetchall()
#     for row in rows:
#         print(f"{row[1]} {row[0]} {row[2]}")


# with connection.cursor() as cursor:
#     cursor.execute(
#         """
#         WITH RideTimes AS (
#             SELECT r.id_ride,
#                    (SELECT created_at
#                     FROM base_rideevent
#                     WHERE id_ride = r.id_ride
#                       AND description = 'Status changed to pickup'
#                     ORDER BY created_at
#                     LIMIT 1) AS time_of_pickup,
#                    (SELECT created_at
#                     FROM base_rideevent
#                     WHERE id_ride = r.id_ride
#                       AND description = 'Status changed to dropoff'
#                     ORDER BY created_at
#                     LIMIT 1) AS time_of_dropoff
#             FROM base_ride r
#         ),
#         RideDurations AS (
#             SELECT id_ride,
#                    time_of_pickup,
#                    time_of_dropoff,
#                    (julianday(time_of_dropoff) - julianday(time_of_pickup)) * 86400 AS duration_seconds
#             FROM RideTimes
#             WHERE time_of_pickup IS NOT NULL AND time_of_dropoff IS NOT NULL
#         )
#         SELECT strftime('%Y-%m', rd.time_of_pickup) AS month,
#                COUNT(rd.id_ride) AS ride_count
#         FROM RideDurations rd
#         WHERE rd.duration_seconds > 3600
#         GROUP BY month
#         ORDER BY month;
#     """
#     )
#     rows = cursor.fetchall()
#     for row in rows:
#         print(f"{row[0]} {row[1]}")


# with connection.cursor() as cursor:
#     cursor.execute(
#         """
#     WITH RideTimes AS (
#         SELECT r.id_ride,
#             r.id_driver_id,
#             (SELECT created_at
#                 FROM base_rideevent
#                 WHERE id_ride = r.id_ride
#                 AND description = 'Status changed to pickup'
#                 ORDER BY created_at
#                 LIMIT 1) AS time_of_pickup,
#             (SELECT created_at
#                 FROM base_rideevent
#                 WHERE id_ride = r.id_ride
#                 AND description = 'Status changed to dropoff'
#                 ORDER BY created_at
#                 LIMIT 1) AS time_of_dropoff
#         FROM base_ride r
#     ),
#     RideDurations AS (
#         SELECT id_ride,
#             id_driver_id,
#             time_of_pickup,
#             time_of_dropoff,
#             (julianday(time_of_dropoff) - julianday(time_of_pickup)) * 86400 AS duration_seconds
#         FROM RideTimes
#         WHERE time_of_pickup IS NOT NULL AND time_of_dropoff IS NOT NULL
#     )
#     SELECT  strftime('%Y-%m', rd.time_of_pickup) AS month,
#     u.first_name || ' ' || u.last_name AS driver_name,
#     COUNT(rd.id_ride) AS ride_count,
#     rd.duration_seconds AS duration
#     FROM RideDurations rd
#     JOIN base_user u ON rd.id_driver_id = u.id_user
#     WHERE rd.duration_seconds > 3600
#     GROUP BY driver_name, month
#     ORDER BY driver_name, month;
#     """
#     )
#     rows = cursor.fetchall()
#     for row in rows:
#         print(f"{row[0]} {row[1]} {row[2]} ")
