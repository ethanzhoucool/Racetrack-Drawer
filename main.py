import matplotlib.pyplot as plt
import pyautogui
import time

# Set up the plot
plt.ion()  # Turn on interactive mode
figure, ax = plt.subplots()
line, = ax.plot([], [], 'b-', linewidth=1)  # For the line connecting dots
current_position_dot = ax.scatter([], [], s=100, color='red')  # For the current cursor position dot
plt.gca().invert_yaxis()  # Invert y-axis to match screen coordinates

x_data, y_data = [], []
lap_times = []  # List to store lap times
lap_start_time = time.time()  # Initialize lap start time

# Initialize flag to track if the first movement has been processed
first_movement_processed = False

def update_limits(x_data, y_data):
    margin = 10  # Add a small margin to make sure points are not on the edge
    ax.set_xlim(min(x_data) - margin, max(x_data) + margin)
    ax.set_ylim(min(y_data) - margin, max(y_data) + margin)

def add_perpendicular_line(x_data, y_data):
    global first_movement_processed, x_start, y_start, x_end, y_end, lap_start_time  # Access global variables and line coordinates
    if len(x_data) >= 2 and not first_movement_processed:
        # Calculate direction of movement
        dx = x_data[-1] - x_data[-2]
        dy = y_data[-1] - y_data[-2]
        # Calculate a perpendicular direction
        perp_dx, perp_dy = -dy, dx
        # Normalize the perpendicular vector
        length = (perp_dx**2 + perp_dy**2)**0.5
        if length != 0:
            perp_dx, perp_dy = (perp_dx / length) * 20, (perp_dy / length) * 20  # Adjust the length of the line as needed
            # Calculate the endpoints of the perpendicular line
            x_center, y_center = x_data[-1], y_data[-1]
            x_start, y_start = x_center - perp_dx / 2, y_center - perp_dy / 2
            x_end, y_end = x_center + perp_dx / 2, y_center + perp_dy / 2
            # Add a new green line for the first movement direction
            ax.plot([x_start, x_end], [y_start, y_end], 'g-', linewidth=2)
            first_movement_processed = True  # Update flag to prevent further perpendicular lines
            lap_start_time = time.time()  # First lap starts when the start line is placed

def side_of(px, py, ax, ay, bx, by):
    # Cross product: > 0 on one side of the line a->b, < 0 on the other, 0 on it
    return (bx - ax) * (py - ay) - (by - ay) * (px - ax)

def check_line_crossing(x_prev, y_prev, x, y, x_start, y_start, x_end, y_end):
    global lap_start_time, lap_times
    # Which side of the start line the last point and this point are on.
    # Moving forward along the track goes from the positive side to the negative side.
    before = side_of(x_prev, y_prev, x_start, y_start, x_end, y_end)
    after = side_of(x, y, x_start, y_start, x_end, y_end)
    if not (before > 0 and after <= 0):
        return
    # Only count it if the movement actually passes through the green segment,
    # not somewhere else along the same infinite line
    if side_of(x_start, y_start, x_prev, y_prev, x, y) * side_of(x_end, y_end, x_prev, y_prev, x, y) > 0:
        return
    # Calculate lap time and reset lap timer
    current_time = time.time()
    lap_time = current_time - lap_start_time
    lap_times.append(lap_time)
    lap_start_time = current_time
    print(f"Lap completed in {lap_time:.2f} seconds.")  # Print lap time

try:
    while True:
        x, y = pyautogui.position()  # Get current cursor position
        x_data.append(x)
        y_data.append(y)
        line.set_data(x_data, y_data)  # Update the line data
        
        # Update the scatter plot to show only the current position as a red dot
        current_position_dot.set_offsets([[x, y]])
        
        if x_data and y_data:  # Check if there are any points to avoid error on min/max calculation
            update_limits(x_data, y_data)
            if first_movement_processed:  # Only check for line crossing if the line exists
                check_line_crossing(x_data[-2], y_data[-2], x, y, x_start, y_start, x_end, y_end)
            add_perpendicular_line(x_data, y_data)  # Call this function to possibly add a perpendicular line
        
        plt.draw()
        plt.pause(0.1)  # Pause to update the graph and allow for UI interaction

except KeyboardInterrupt:
    plt.close('all')
    # Optionally, print all lap times at the end
    for i, lap_time in enumerate(lap_times, 1):
        print(f"Lap {i}: {lap_time:.2f} seconds")
