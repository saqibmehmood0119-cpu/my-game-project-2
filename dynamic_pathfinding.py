import tkinter as tk
import heapq
import random
import time
import math

try:
    ROWS = int(input("Enter grid size: "))
except:
    print("Invalid input")
    ROWS = 15

CELL_SIZE = 30
SPAWN_PROB = 0.05

BG_COLOR = "#F8F0FF"
EMPTY_COLOR = "#FFF5FA"
OBSTACLE_COLOR = "#7A4EAB"
START_COLOR = "#FF69B4"
GOAL_COLOR = "#FF3770"
PATH_COLOR = "#A8E6CF"
VISITED_COLOR = "#A0C4FF"
FRONTIER_COLOR = "#FFF3B0"
BUTTON_BG = "#CDB4DB"
BUTTON_FG = "#5A189A"

start = (0, 0)
goal = (ROWS - 1, ROWS - 1)

grid = [[0 for _ in range(ROWS)] for _ in range(ROWS)]

agent_pos = start
current_path = []
visited_nodes = set()
frontier_nodes = set()

current_algorithm = "A*"
current_heuristic = "Manhattan"

nodes_expanded = 0
execution_time = 0
path_cost = 0


def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def euclidean(a, b):
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)


def heuristic(a, b):
    if current_heuristic == "Manhattan":
        return manhattan(a, b)
    return euclidean(a, b)


def search(start_node):
    global visited_nodes, frontier_nodes, nodes_expanded, execution_time

    visited_nodes = set()
    frontier_nodes = set()
    nodes_expanded = 0

    open_set = []
    heapq.heappush(open_set, (0, start_node))

    came_from = {}
    g_score = {start_node: 0}

    start_time = time.time()

    while open_set:
        f_val, current = heapq.heappop(open_set)

        if current == goal:
            break

        if current in visited_nodes:
            continue

        visited_nodes.add(current)
        nodes_expanded += 1

        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nx, ny = current[0] + dx, current[1] + dy

            if 0 <= nx < ROWS and 0 <= ny < ROWS and grid[nx][ny] == 0:

                if current_algorithm == "A*":
                    temp_g = g_score[current] + 1
                    if (nx, ny) not in g_score or temp_g < g_score.get((nx, ny), float("inf")):
                        g_score[(nx, ny)] = temp_g
                        f = temp_g + heuristic((nx, ny), goal)
                        heapq.heappush(open_set, (f, (nx, ny)))
                        frontier_nodes.add((nx, ny))
                        came_from[(nx, ny)] = current
                else:
                    if (nx, ny) not in visited_nodes:
                        f = heuristic((nx, ny), goal)
                        heapq.heappush(open_set, (f, (nx, ny)))
                        frontier_nodes.add((nx, ny))
                        came_from[(nx, ny)] = current

    execution_time = (time.time() - start_time) * 1000

    path = []
    node = goal
    while node in came_from:
        path.append(node)
        node = came_from[node]

    path.reverse()
    return path


def generate_random_map():
    density = float(density_entry.get())
    for i in range(ROWS):
        for j in range(ROWS):
            if (i, j) != start and (i, j) != goal:
                grid[i][j] = 1 if random.random() < density else 0
    draw()


def run_static():
    global current_path, agent_pos, path_cost
    agent_pos = start
    current_path = search(start)
    path_cost = len(current_path)
    draw()


def move_agent():
    global agent_pos, current_path, path_cost

    if agent_pos == goal:
        return

    if not current_path:
        current_path = search(agent_pos)
        path_cost = len(current_path)

    if not current_path:
        return

    next_step = current_path.pop(0)

    if grid[next_step[0]][next_step[1]] == 1:
        current_path = []
        root.after(200, move_agent)
        return

    agent_pos = next_step

    if random.random() < SPAWN_PROB:
        r = random.randint(0, ROWS - 1)
        c = random.randint(0, ROWS - 1)
        if (r, c) != agent_pos and (r, c) != goal:
            grid[r][c] = 1

    draw()
    root.after(200, move_agent)


def draw():
    canvas.delete("all")

    for i in range(ROWS):
        for j in range(ROWS):
            x1 = j * CELL_SIZE
            y1 = i * CELL_SIZE
            x2 = x1 + CELL_SIZE
            y2 = y1 + CELL_SIZE

            color = EMPTY_COLOR

            if grid[i][j] == 1:
                color = OBSTACLE_COLOR

            if (i, j) in frontier_nodes:
                color = FRONTIER_COLOR

            if (i, j) in visited_nodes:
                color = VISITED_COLOR

            if (i, j) in current_path:
                color = PATH_COLOR

            if (i, j) == agent_pos:
                color = START_COLOR

            if (i, j) == goal:
                color = GOAL_COLOR

            canvas.create_rectangle(
                x1, y1, x2, y2,
                fill=color,
                outline="black",
                width=1
            )

    metrics_label.config(
        text=f"Algorithm: {current_algorithm}\n"
             f"Heuristic: {current_heuristic}\n"
             f"Visited: {nodes_expanded}\n"
             f"Path Cost: {path_cost}\n"
             f"Time(ms): {round(execution_time,2)}"
    )


def place_wall(event):
    row = event.y 
    col = event.x 

    if 0 <= row < ROWS and 0 <= col < ROWS:
        if (row, col) != agent_pos and (row, col) != goal:
            grid[row][col] = 1 if grid[row][col] == 0 else 0

    draw()


root = tk.Tk()
root.title("✨ DPFA ✨")
root.configure(bg=BG_COLOR)

main_frame = tk.Frame(root, bg=BG_COLOR)
main_frame.pack()

canvas = tk.Canvas(
    main_frame,
    width=ROWS * CELL_SIZE,
    height=ROWS * CELL_SIZE,
    bg=BG_COLOR,
    highlightthickness=0
)
canvas.grid(row=0, column=0, padx=10, pady=10)
canvas.bind("<Button-1>", place_wall)

control_frame = tk.Frame(main_frame, bg=BG_COLOR)
control_frame.grid(row=0, column=1, sticky="n", padx=10, pady=10)

tk.Label(control_frame, text="Controls <3",
         font=("Arial", 13, "bold"),
         bg=BG_COLOR,
         fg=BUTTON_FG).pack(pady=5)

tk.Label(control_frame, text="Density (0-1)",
         bg=BG_COLOR,
         fg=BUTTON_FG).pack()

density_entry = tk.Entry(control_frame, width=8)
density_entry.insert(0, "0.3")
density_entry.pack(pady=2)

tk.Button(control_frame, text="Generate Map",
          width=18,
          bg=BUTTON_BG,
          fg=BUTTON_FG,
          command=generate_random_map).pack(pady=4)

algorithm_var = tk.StringVar(value="A*")
heuristic_var = tk.StringVar(value="Manhattan")

def update_algorithm(*args):
    global current_algorithm
    current_algorithm = algorithm_var.get()

def update_heuristic(*args):
    global current_heuristic
    current_heuristic = heuristic_var.get()

algorithm_var.trace_add("write", update_algorithm)
heuristic_var.trace_add("write", update_heuristic)

tk.Label(control_frame, text="Algorithm",
         bg=BG_COLOR,
         fg=BUTTON_FG).pack(pady=(10, 0))
tk.OptionMenu(control_frame, algorithm_var, "A*", "Greedy").pack()

tk.Label(control_frame, text="Heuristic",
         bg=BG_COLOR,
         fg=BUTTON_FG).pack(pady=(10, 0))
tk.OptionMenu(control_frame, heuristic_var,
              "Manhattan", "Euclidean").pack()

tk.Button(control_frame, text="Run Static Search",
          width=18,
          bg=BUTTON_BG,
          fg=BUTTON_FG,
          command=run_static).pack(pady=4)

tk.Button(control_frame, text="Start Dynamic Mode",
          width=18,
          bg=BUTTON_BG,
          fg=BUTTON_FG,
          command=move_agent).pack(pady=4)

metrics_label = tk.Label(control_frame,
                         text="",
                         justify="left",
                         bg=BG_COLOR,
                         fg=BUTTON_FG)
metrics_label.pack(pady=10)

draw()
root.mainloop()