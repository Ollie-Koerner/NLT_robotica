from microbit import sleep
from Cutebot import Cutebot, LEFT_LIGHT_ADDR, RIGHT_LIGHT_ADDR

ct = Cutebot()

# States
E_STOP, DRIVE_FORWARD, DRIVE_LEFT, DRIVE_RIGHT, LINE_SEARCH, OBSTACLE_AVOIDANCE = 1, 3, 4, 5, 6, 7
OA_FIRST_TURN, OA_TURN, OA_DRIVE_FORWARD = 10, 11, 12

state, prev_state, sub_state = 0, 0, 0
t, t_in_state, t_in_sub_state = 0, 0, 0
oa_t_c = 0

offset = 0  # left motor offset
SPD = 40
T_LOW, T_HIGH = 0, 30
T_S_TIME = 380

def set_state(s):
    global state, prev_state, t_in_state
    prev_state, state, t_in_state = state, s, 0

def set_motor(l, r):
    ct.set_motors_speed(round(l * (1 - offset)), round(r * (1 + offset)))

while state != E_STOP:
    dist = float(ct.get_distance())
    track = ct.get_tracking()
    print(dist)

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
        if t_in_state == 1:
            sub_state = OA_FIRST_TURN
        elif sub_state in (0, DRIVE_LEFT, DRIVE_RIGHT):
            sub_state = 0

        if track == 11:
            set_state(DRIVE_LEFT)

    # Execute state
    if state == DRIVE_FORWARD:
        ct.set_car_light(LEFT_LIGHT_ADDR, 0, 255, 0)
        ct.set_car_light(RIGHT_LIGHT_ADDR, 0, 0 , 0)
        set_motor(SPD, SPD)
    elif state == DRIVE_LEFT:
        ct.set_car_light(LEFT_LIGHT_ADDR, 0, 255, 0)
        ct.set_car_light(RIGHT_LIGHT_ADDR, 255, 0 , 0)
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
            oa_t_c = 0

        elif sub_state == OA_TURN:
            ct.set_car_light(RIGHT_LIGHT_ADDR, 0, 0, 255)
            set_motor(T_HIGH, -T_HIGH)
            sleep(T_S_TIME)
            set_motor(0, 0)
            
            dist = float(ct.get_distance())
            if 0 < dist < 25:
                ct.set_car_light(RIGHT_LIGHT_ADDR, 255, 0, 0)
                set_motor(-T_HIGH, T_HIGH)
                sleep(T_S_TIME)
            else:
                oa_t_c += 1
            sub_state = OA_DRIVE_FORWARD
            t_in_sub_state = 0
            
        elif sub_state == OA_DRIVE_FORWARD:
            ct.set_car_light(RIGHT_LIGHT_ADDR, 0, 255, 0)
            set_motor(SPD, SPD)
            tracking = ct.get_tracking()
            drive_lenght = 8 if oa_t_c < 1 else 16
            if t_in_sub_state > drive_lenght and tracking != 11:
                set_motor(0, 0)
                sub_state = OA_TURN
                t_in_sub_state = 0

    t += 1
    t_in_state += 1
    t_in_sub_state += 1
    sleep(50)

# E_stop
ct.set_motors_speed(0, 0)
ct.set_car_light(RIGHT_LIGHT_ADDR, 255, 0, 0)
ct.set_car_light(LEFT_LIGHT_ADDR, 255, 0, 0)