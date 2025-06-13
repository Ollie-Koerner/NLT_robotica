from microbit import sleep
from Cutebot import Cutebot, LEFT_LIGHT_ADDR, RIGHT_LIGHT_ADDR

ct = Cutebot()

# States
E_STOP, DRIVE_FORWARD, DRIVE_LEFT, DRIVE_RIGHT, LINE_SEARCH, OBSTACLE_AVOIDANCE = 1, 3, 4, 5, 6, 7
OA_FIRST_TURN, OA_TURN, OA_DRIVE_FORWARD = 10, 11, 12

state, prev_state, sub_state = 0, 0, 0
t, t_in_state, t_in_sub_state = 0, 0, 0

offset = 0  # left motor offset
SPD = 40
T_LOW, T_HIGH = 0, 30
T_S_TIME = 470

def set_state(s):
    global state, prev_state, t_in_state, sub_state
    prev_state, state, t_in_state = state, s, 0
    if s == OBSTACLE_AVOIDANCE:
        sub_state = OA_FIRST_TURN

def set_motor(l, r):
    ct.set_motors_speed(round(l * (1 - offset)), round(r * (1 + offset)))

while state != E_STOP:
    dist = float(ct.get_distance())
    dist_s = float(ct.get_distance_side())
    track = ct.get_tracking()
    print(dist)
    print("Side:",dist_s)

    if 0 < dist <= 8.0:
        sleep(50)
        if 0 < float(ct.get_distance()) <= 5.0:
            set_state(E_STOP)
            break

    elif state != OBSTACLE_AVOIDANCE:
        if 0 < dist < 15:
            set_state(OBSTACLE_AVOIDANCE)
        elif track == 0:
            set_state(LINE_SEARCH)
        elif track == 11:
            set_state(DRIVE_FORWARD)
        elif track == 10:
            set_state(DRIVE_LEFT)
        elif track == 1:
            set_state(DRIVE_RIGHT)

    elif state == OBSTACLE_AVOIDANCE:
        if sub_state in (0, DRIVE_LEFT, DRIVE_RIGHT):
            sub_state = 0

        if track == 11 or track == 10:
            set_state(DRIVE_LEFT)
        elif track == 1:
            set_state(DRIVE_RIGHT)

    # Execute state
    if state == DRIVE_FORWARD:
        ct.set_car_light(LEFT_LIGHT_ADDR, 0, 255, 0)
        ct.set_car_light(RIGHT_LIGHT_ADDR, 0, 0 , 0)
        set_motor(SPD, SPD)
    elif state == DRIVE_LEFT:
        ct.set_car_light(LEFT_LIGHT_ADDR, 0, 255, 0)
        ct.set_car_light(RIGHT_LIGHT_ADDR, 0, 0 , 0)
        set_motor(T_LOW, T_HIGH)
    elif state == DRIVE_RIGHT:
        ct.set_car_light(LEFT_LIGHT_ADDR, 0, 255, 0)
        ct.set_car_light(RIGHT_LIGHT_ADDR, 0, 0 , 0)
        set_motor(T_HIGH, T_LOW)
    elif state == LINE_SEARCH:
        ct.set_car_light(LEFT_LIGHT_ADDR, 0, 255, 255)
        ct.set_car_light(RIGHT_LIGHT_ADDR, 0, 0 , 255)
        if prev_state == DRIVE_LEFT:
            sub_state = DRIVE_LEFT
        elif prev_state == DRIVE_RIGHT:
            sub_state = DRIVE_RIGHT
        elif prev_state == DRIVE_FORWARD:
            sub_state = DRIVE_LEFT

        if sub_state == DRIVE_LEFT:
            set_motor(T_LOW, T_HIGH)
        elif sub_state == DRIVE_RIGHT:
            set_motor(T_HIGH, T_LOW)

    elif state == OBSTACLE_AVOIDANCE:
        ct.set_car_light(LEFT_LIGHT_ADDR, 0, 0, 255)
        ct.set_car_light(RIGHT_LIGHT_ADDR, 0, 0 , 0)
        if sub_state == OA_FIRST_TURN:
            ct.set_car_light(RIGHT_LIGHT_ADDR, 0, 255, 255)
            set_motor(-T_HIGH, T_HIGH)
            sleep(T_S_TIME)
            set_motor(0, 0)
            sub_state = OA_DRIVE_FORWARD
            t_in_sub_state = 0

        elif sub_state == OA_TURN:
            ct.set_car_light(RIGHT_LIGHT_ADDR, 0, 0, 255)
            set_motor(T_HIGH, -T_HIGH)
            sleep(T_S_TIME)
            set_motor(0, 0)
            sub_state = OA_DRIVE_FORWARD
            t_in_sub_state = 0
            
        elif sub_state == OA_DRIVE_FORWARD:
            ct.set_car_light(RIGHT_LIGHT_ADDR, 0, 255, 0)
            tracking = ct.get_tracking()
            dist = ct.get_distance_side()
            if (t_in_sub_state <= 6 or dist <= 25):
                set_motor(SPD, SPD)
            elif tracking == 0:
                set_motor(0, 0)
                sub_state = OA_TURN
                t_in_sub_state = 0
            else:
                sleep(250)
                set_motor(0, 0)
                sub_state = OA_TURN
                t_in_sub_state = 0

    t += 1
    t_in_state += 1
    t_in_sub_state += 1
    ct.set_car_light(LEFT_LIGHT_ADDR, 0, 0, 0)
    ct.set_car_light(RIGHT_LIGHT_ADDR, 0, 0 , 0)
    sleep(50)

# E_stop
ct.set_motors_speed(0, 0)
ct.set_car_light(RIGHT_LIGHT_ADDR, 255, 0, 0)
ct.set_car_light(LEFT_LIGHT_ADDR, 255, 0, 0)
