#!/usr/bin/env python3

import tkinter as tk
import RPi.GPIO as GPIO
from threading import Thread
import time

# GPIO Setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

motor_pins = [
    {'step': 27, 'direction': 21, 'enable': 4},
    {'step': 26, 'direction': 23, 'enable': 13},
    {'step': 12, 'direction': 20, 'enable': 22},
    {'step': 24, 'direction': 25, 'enable': 19},
    {'step': 16, 'direction': 6, 'enable': 5},
    {'step': 17, 'direction': 18, 'enable': 10}
]

motor_speed = [100, 100, 100, 100, 100, 100]
motor_threads = [None] * len(motor_pins)
speed_sliders = []

# Add a list to keep track of the direction of each motor
motor_direction = [GPIO.HIGH] * len(motor_pins)  # Default direction for all motors

for pin_set in motor_pins:
    for pin in pin_set.values():
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.LOW)

def start_motor(index):
    global motor_threads
    if motor_threads[index] is None or not motor_threads[index].is_alive():
        motor_threads[index] = Thread(target=run_motor, args=(index,))
        motor_threads[index].start()

def stop_motor(index):
    GPIO.output(motor_pins[index]['enable'], GPIO.HIGH)
    if motor_threads[index] is not None:
        motor_threads[index].join()
        motor_threads[index] = None

def stop_all_motors():
    for index in range(len(motor_pins)):
        GPIO.output(motor_pins[index]['enable'], GPIO.HIGH)
        if motor_threads[index] is not None:
            motor_threads[index].join()
            motor_threads[index] = None

def quit_program():
    stop_all_motors()
    root.destroy()

def run_motor(index):
    step_pin = motor_pins[index]['step']
    dir_pin = motor_pins[index]['direction']
    en_pin = motor_pins[index]['enable']

    GPIO.output(en_pin, GPIO.LOW)
    GPIO.output(dir_pin, motor_direction[index])  # Use the direction from the motor_direction list

    while GPIO.input(en_pin) == GPIO.LOW:
        speed = motor_speed[index]  # Get the speed value each iteration
        
        # Run the motor for 0.5 seconds
        end_time = time.time() + 0.5
        while time.time() < end_time:
            GPIO.output(step_pin, GPIO.HIGH)
            time.sleep(1.0 / speed / 2)
            GPIO.output(step_pin, GPIO.LOW)
            time.sleep(1.0 / speed / 5)
        
        # Stop the motor for 0.5 seconds
        time.sleep(0.5)

def toggle_direction(index):
    """Toggle the direction of the motor."""
    if motor_direction[index] == GPIO.HIGH:
        motor_direction[index] = GPIO.LOW
    else:
        motor_direction[index] = GPIO.HIGH

    # Update the direction immediately if the motor is running
    if motor_threads[index] is not None and motor_threads[index].is_alive():
        GPIO.output(motor_pins[index]['direction'], motor_direction[index])

def create_motor_control(page, motor_index, row):
    motor_frame = tk.Frame(page, bg='black')
    motor_frame.grid(row=row, column=0, padx=10, pady=10)

    def update_speed(index, value):
        motor_speed[index] = int(value)
        if motor_threads[index] is not None and motor_threads[index].is_alive():
            stop_motor(index)
            start_motor(index)

    start_button = tk.Button(motor_frame, text=f"Start Motor {motor_index+1}", command=lambda idx=motor_index: start_motor(idx), bg='green', fg='white', font=("Arial", 12, "bold"))
    start_button.grid(row=0, column=0, padx=1, pady=1)

    stop_button = tk.Button(motor_frame, text=f"Stop Motor {motor_index+1}", command=lambda idx=motor_index: stop_motor(idx), bg='red', fg='white', font=("Arial", 12, "bold"))
    stop_button.grid(row=0, column=1, padx=1, pady=1)

    # Add a toggle button for direction
    direction_button = tk.Button(motor_frame, text=f"Direction {motor_index+1}", command=lambda idx=motor_index: toggle_direction(idx), bg='purple', fg='white', font=("Arial", 12, "bold"))
    direction_button.grid(row=0, column=2, padx=1, pady=1)

    speed_slider = tk.Scale(motor_frame, from_=1, to=255, orient=tk.HORIZONTAL, font=("Arial", 12), length=200, sliderlength=15, command=lambda value, idx=motor_index: update_speed(idx, value))
    speed_slider.set(motor_speed[motor_index])
    speed_slider.grid(row=0, column=3, padx=5, pady=0)
    speed_sliders.append(speed_slider)

# Create the GUI
root = tk.Tk()
root.title("PULSE Stepper Motor Control")
root.geometry("800x450")
root.configure(bg='black')

# Create a canvas for scrolling
canvas = tk.Canvas(root, bg='black')
canvas.pack(side="left", fill="both", expand=True)

# Create a frame inside the canvas for placing widgets
frame = tk.Frame(canvas, bg='black')
canvas.create_window((0, 0), window=frame, anchor="nw")

# Add widgets to the main frame
welcome_label = tk.Label(frame, text="Welcome to\nPiClyde!", bg='black', fg='red', font=("Arial", 20, "bold"))
welcome_label.grid(row=1, column=1, columnspan=3, pady=5)

for i in range(6):
    create_motor_control(frame, i, i+1)

# Create two additional buttons
stop_all_motors_button = tk.Button(frame, text="Stop All\nMotors", command=stop_all_motors, bg='blue', fg='white', font=("Arial", 20, "bold"))
stop_all_motors_button.grid(row=2, column=1,columnspan=6, padx=10, pady=0)

quit_program_button = tk.Button(frame, text="Quit\nProgram", command=quit_program, bg='orangered', fg='white', font=("Arial", 18, "bold"))
quit_program_button.grid(row=5, column=1, padx=15, pady=1)

# Start the scrolling functionality
canvas.update_idletasks()
canvas.config(scrollregion=canvas.bbox("all"))

root.mainloop()
