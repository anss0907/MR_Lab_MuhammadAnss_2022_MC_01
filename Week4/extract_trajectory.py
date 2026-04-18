#!/usr/bin/env python3
"""
extract_trajectory.py
Reads the rosbag (SQLite3) recorded during Lab 4, extracts /turtle1/cmd_vel
messages, and writes them to trajectory_data.csv with a brief analysis printed
to the console.
"""

import sqlite3
import csv
import struct
import os
import math

BAG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "rosbag2_2026_04_10-12_02_27")
DB_PATH = os.path.join(BAG_DIR, "rosbag2_2026_04_10-12_02_27_0.db3")
OUT_CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "trajectory_data.csv")


def deserialize_twist(data: bytes):
    """
    Deserialize a CDR-encoded geometry_msgs/msg/Twist.
    CDR layout (little-endian):
      4 bytes  – CDR header (0x00 0x01 0x00 0x00)
      6 x float64 – linear.x, linear.y, linear.z, angular.x, angular.y, angular.z
    """
    # Skip 4-byte CDR header
    values = struct.unpack_from('<6d', data, offset=4)
    return {
        'linear_x': values[0],
        'linear_y': values[1],
        'linear_z': values[2],
        'angular_x': values[3],
        'angular_y': values[4],
        'angular_z': values[5],
    }


def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get topic id for /turtle1/cmd_vel
    cursor.execute("SELECT id FROM topics WHERE name = '/turtle1/cmd_vel'")
    row = cursor.fetchone()
    if row is None:
        print("ERROR: /turtle1/cmd_vel topic not found in the bag.")
        return
    topic_id = row[0]

    # Fetch all messages sorted by timestamp
    cursor.execute(
        "SELECT timestamp, data FROM messages WHERE topic_id = ? ORDER BY timestamp",
        (topic_id,))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("No messages found for /turtle1/cmd_vel.")
        return

    t0 = rows[0][0]  # first timestamp in nanoseconds

    # Write CSV
    with open(OUT_CSV, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'time_s', 'linear_x', 'linear_y', 'linear_z',
            'angular_x', 'angular_y', 'angular_z'
        ])

        records = []
        for ts, data in rows:
            t_sec = (ts - t0) / 1e9
            twist = deserialize_twist(data)
            writer.writerow([
                f"{t_sec:.4f}",
                f"{twist['linear_x']:.4f}",
                f"{twist['linear_y']:.4f}",
                f"{twist['linear_z']:.4f}",
                f"{twist['angular_x']:.4f}",
                f"{twist['angular_y']:.4f}",
                f"{twist['angular_z']:.4f}",
            ])
            records.append((t_sec, twist))

    # ---------- Brief Analysis ----------
    total_duration = records[-1][0]
    total_msgs = len(records)

    lin_speeds = [abs(r[1]['linear_x']) for r in records]
    ang_speeds = [abs(r[1]['angular_z']) for r in records]

    avg_linear = sum(lin_speeds) / total_msgs
    max_linear = max(lin_speeds)
    avg_angular = sum(ang_speeds) / total_msgs
    max_angular = max(ang_speeds)

    forward_count = sum(1 for s in lin_speeds if s > 0.01)
    turn_count = sum(1 for s in ang_speeds if s > 0.01)
    idle_count = sum(1 for lx, az in zip(lin_speeds, ang_speeds)
                     if lx < 0.01 and az < 0.01)

    print("=" * 55)
    print("  TRAJECTORY DATA EXTRACTION – BRIEF ANALYSIS")
    print("=" * 55)
    print(f"  Bag duration          : {total_duration:.2f} s")
    print(f"  Total messages        : {total_msgs}")
    print(f"  Avg publish rate      : {total_msgs / total_duration:.1f} Hz")
    print("-" * 55)
    print(f"  Avg linear speed |v|  : {avg_linear:.3f} m/s")
    print(f"  Max linear speed      : {max_linear:.3f} m/s")
    print(f"  Avg angular speed |ω| : {avg_angular:.3f} rad/s")
    print(f"  Max angular speed     : {max_angular:.3f} rad/s")
    print("-" * 55)
    print(f"  Forward commands      : {forward_count} / {total_msgs}")
    print(f"  Turn commands         : {turn_count} / {total_msgs}")
    print(f"  Idle commands         : {idle_count} / {total_msgs}")
    print("=" * 55)
    print(f"\n  CSV saved to: {OUT_CSV}")


if __name__ == '__main__':
    main()
