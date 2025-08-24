def interpolate_between_servo_positions(start_pos, end_pos, steps):
    start_angle_hip = start_pos[0]
    start_angle_front = start_pos[1]
    start_angle_rear = start_pos[2]

    end_angle_hip = end_pos[0]
    end_angle_front = end_pos[1]
    end_angle_rear = end_pos[2]

    return [
        (
            int(start_angle_hip + (end_angle_hip - start_angle_hip) * i / steps),
            int(start_angle_front + (end_angle_front - start_angle_front) * i / steps),
            int(start_angle_rear + (end_angle_rear - start_angle_rear) * i / steps)
        )
        for i in range(steps + 1)
    ]
