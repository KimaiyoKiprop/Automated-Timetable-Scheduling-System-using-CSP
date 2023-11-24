from constraint import Problem
import time
import matplotlib.pyplot as plt

class Class:
    def __init__(self, name, capacity, special_requirements):
        self.name = name
        self.capacity = capacity
        self.special_requirements = special_requirements
        self.timeslots = []

class Teacher:
    def __init__(self, name, available_timeslots, subjects):
        self.name = name
        self.available_timeslots = available_timeslots
        self.subjects = subjects

class Room:
    def __init__(self, name, capacity, available_timeslots, features):
        self.name = name
        self.capacity = capacity
        self.available_timeslots = available_timeslots
        self.features = features
        self.timeslots = []

class Timeslot:
    def __init__(self, day, time):
        self.day = day
        self.time = time

class Timetable:
    def __init__(self):
        self.schedule = {}

def backtracking_search(csp, use_heuristics=True):
    assignment = {}
    return backtrack(assignment, csp, use_heuristics)

def backtrack(assignment, csp, use_heuristics=True):
    if len(assignment) == len(csp):
        return assignment

    var = select_unassigned_variable(csp, assignment, use_heuristics)
    print(f"Trying variable: {var.name}")

    for value in order_domain_values(var, assignment, csp, use_heuristics):
        if is_consistent(var, value, assignment, csp):
            assignment[var] = value
            print(f"Assigned {var.name} to {value.name}")

            if isinstance(var, Class):
                assigned_teacher = assignment.get(var)
                assigned_room = assignment.get(assigned_teacher)
                if assigned_room:
                    assigned_room.timeslots.append(var.timeslots[0])

            result = backtrack(assignment, csp, use_heuristics)
            if result is not None:
                return result

            print(f"Backtracking on {var.name}")

            if isinstance(var, Class):
                assigned_teacher = assignment.get(var)
                assigned_room = assignment.get(assigned_teacher)
                if assigned_room and assigned_room.timeslots:
                    assigned_room.timeslots.remove(var.timeslots[0])

            del assignment[var]

    print(f"No valid assignment for {var.name}")
    return None


def select_unassigned_variable(csp, assignment, use_heuristics=True):
    unassigned_vars = [var for var in csp if var not in assignment]
    return mrv_heuristic(unassigned_vars, assignment, csp) if use_heuristics else unassigned_vars[0]

def order_domain_values(var, assignment, csp, use_heuristics=True):
    return lcv_heuristic(csp, var, assignment) if use_heuristics else csp[var]

def is_consistent(var, value, assignment, csp):
    print(f"Checking consistency for {var.name} = {value.name}")

    if isinstance(var, Class):
        for neighbor in csp[var]:
            neighbor_value = assignment.get(neighbor)
            if neighbor_value is not None and not constraint(var, value, neighbor_value, csp):
                print(f"Inconsistent with {neighbor.name}")
                return False
        assigned_teacher = assignment.get(var)
        assigned_room = assignment.get(assigned_teacher)
        if assigned_room and hasattr(assigned_room, 'timeslots'):
            assigned_room.timeslots.append(var.timeslots[0])

    elif isinstance(var, Teacher):
        for neighbor in csp[var]:
            neighbor_value = assignment.get(neighbor)
            if neighbor_value is not None and not constraint(var, value, neighbor_value, csp):
                print(f"Inconsistent with {neighbor.name}")
                return False

    elif isinstance(var, Room):
        for neighbor in csp[var]:
            neighbor_value = assignment.get(neighbor)
            if neighbor_value is not None and not constraint(var, value, neighbor_value, csp):
                print(f"Inconsistent with {neighbor.name}")
                return False

    # Check for room assignment consistency
    for assigned_var, assigned_value in assignment.items():
        if assigned_var != var and isinstance(assigned_value, Room) and assigned_value.name == value.name:
            print(f"Inconsistent: Room {value.name} is already assigned to {assigned_var.name}")
            return False

    print("Consistent")
    return True
    
def constraint(var, value, neighbor_value, csp):
    if var in csp and neighbor_value in assignment:
        return csp[var](value, neighbor_value)
    return True

def teacher_constraint(class_obj, teacher_obj):
    return class_obj.name in teacher_obj.subjects and not any(t in teacher_obj.available_timeslots for t in class_obj.timeslots)

def room_constraint(class_obj, room_obj):
    return not any(t in room_obj.available_timeslots for t in class_obj.timeslots) and room_obj.capacity >= class_obj.capacity

def capacity_constraint(class_obj, room_obj):
    return class_obj.capacity <= room_obj.capacity

def preference_constraint(teacher_obj, timeslot_obj):
    return timeslot_obj.day + "_" + timeslot_obj.time in teacher_obj.available_timeslots

def mrv_heuristic(unassigned_vars, assignment, full_csp):
    return min(unassigned_vars, key=lambda x: len(getattr(full_csp[x], 'timeslots', [])) if hasattr(full_csp[x], 'timeslots') else len(full_csp[x].timeslots) if hasattr(full_csp[x], 'timeslots') else len(full_csp[x]) if isinstance(full_csp[x], (list, tuple)) and len(full_csp[x]) > 0 and isinstance(full_csp[x][0], Timeslot) else len(getattr(x, 'timeslots', [])))

def lcv_heuristic(csp, variable, assignment):
    values = sorted(csp[variable], key=lambda x: sum(len(csp[neighbor]) for neighbor in csp if x in csp[neighbor] and x not in assignment))
    return values

# Create instances of classes, teachers, rooms, and timeslots
math_class = Class("Math", 30, False)
physics_class = Class("Physics", 25, True)
john_teacher = Teacher("John", ["Monday_10AM", "Wednesday_2PM"], ["Math", "Physics"])
jane_teacher = Teacher("Jane", ["Tuesday_1PM", "Thursday_10AM"], ["Physics"])
classroom_a = Room("A", 40, ["Monday_10AM", "Wednesday_2PM", "Friday_3PM"], ["Projector"])
classroom_b = Room("B", 30, ["Tuesday_1PM", "Thursday_10AM", "Friday_3PM"], ["Lab"])
morning_slot = Timeslot("Monday", "10AM")
afternoon_slot = Timeslot("Wednesday", "2PM")

# Set timeslots for classes
math_class.timeslots = [morning_slot]
physics_class.timeslots = [afternoon_slot]

# Create a timetable instance
timetable = Timetable()

# Create CSP representation and constraints
csp = {
    math_class: [john_teacher, classroom_a],
    physics_class: [jane_teacher, classroom_b]
}

# Measure execution time without heuristics
start_time_without_heuristics = time.time()
result_backtracking_without_heuristics = backtracking_search(csp, use_heuristics=False)
end_time_without_heuristics = time.time()
execution_time_without_heuristics = end_time_without_heuristics - start_time_without_heuristics

# Measure execution time with heuristics
start_time_with_heuristics = time.time()
result_backtracking_with_heuristics = backtracking_search(csp)
end_time_with_heuristics = time.time()
execution_time_with_heuristics = end_time_with_heuristics - start_time_with_heuristics

# Display the final schedule in a table
print("\nResults\nSchedule Visualization\n")
print("| {:<15} | {:<15} | {:<15} | {:<15} |".format("Timeslot", "Assigned Class", "Assigned Teacher", "Assigned Room"))
print("|" + "-" * 69 + "|")

for var in csp:
    timeslot = var.timeslots[0] if var.timeslots else "Not Assigned"
    assigned_teacher = result_backtracking_with_heuristics.get(var) if result_backtracking_with_heuristics else None
    assigned_room = result_backtracking_with_heuristics.get(assigned_teacher) if result_backtracking_with_heuristics and assigned_teacher else None

    assigned_teacher_name = assigned_teacher.name if assigned_teacher else "Not Assigned"
    assigned_room_name = assigned_room.name if assigned_room else "Not Assigned"

    print("| {:<15} | {:<15} | {:<15} | {:<15} |".format(
        f"{timeslot.day}_{timeslot.time}", var.name, assigned_teacher_name, assigned_room_name
    ))

# Plotting execution time comparison
labels = ['Without Heuristics', 'With Heuristics']
execution_times = [execution_time_without_heuristics, execution_time_with_heuristics]

plt.figure(figsize=(8, 5))
plt.bar(labels, execution_times, color=['blue', 'orange'])
plt.xlabel('Heuristics')
plt.ylabel('Execution Time (seconds)')
plt.title('Execution Time Comparison')
plt.show()

