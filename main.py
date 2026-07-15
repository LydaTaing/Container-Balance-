import os
from Ship import Ship
from LogFile import LogFile

import tkinter as tk
from GUI import ShipBalancerGUI

# Print the final manifest in the specified format
def print_outbound_manifest(goal_node, file_name, logfile):
    ship = goal_node.ship
    
    output = []

    for r in range(ship.R):
        for c in range(ship.C):
            spot = ship.grid[r][c]
            # shift up 1 based indexing
            # necessary to pad with zeros
            r_str = f"{r+1:02}"
            c_str = f"{c+1:02}"

            if spot == "NAN":
                weight = "00000"
                desc = "NAN"
            elif spot is None:
                weight = "00000"
                desc = "UNUSED"
            else:
                weight = f"{spot.weight:05}"
                desc = spot.desc

            # it would make more sense to just append to string, but we should use the equivalent of a StringBuilder
            # since strings are immutable
            output.append(f"[{r_str},{c_str}], {{{weight}}}, {desc}")
    
    file_name_no_ext = os.path.splitext(file_name)[0]
    manifest_output_file = file_name_no_ext + "_OUTBOUND.txt"
    print(f"\nDone! {manifest_output_file} was written to the desktop.")
    
    # write the final manifest - must be in exact format as input manifest but with OUTBOUND suffix
    try:
        with open(manifest_output_file, "w") as f:
            f.write('\n'.join(output))
        
        print(f"\nI have written an updated manifest to the desktop as {manifest_output_file}")
        print("Don't forget to email it to the captain.")
        

        print(f"\nFinal manifest is here: {manifest_output_file}")
        logfile.logging(f"Finished a Cycle. Manifest {manifest_output_file} was written to desktop, and a reminder pop-up to operator to send file was displayed.")
        
    except Exception as e:
        print(f"\nError: {e}")

def print_solution(goal_node, logfile):
    path = []
    current = goal_node
    
    while current:
        path.append(current)
        current = current.parent
    path.reverse()
    
    num_moves = len(path) - 1
    total_time = goal_node.cost
    
    print(f"\nSolution was found, it will take {total_time} minutes and {num_moves} moves.")
    logfile.logging(f"Balance solution found, it will require {num_moves} moves/{total_time} minutes.")
    
    # enter to continue
    input("")
    for i, node in enumerate(path[1:], 1):
        # each step cost: (Current Total - Previous Total)
        step_cost = node.cost - node.parent.cost
        
        print(f"{i} of {num_moves}: {node.move}, {step_cost} minutes")
        logfile.logging(f"{i} of {num_moves}: {node.move}, {step_cost} minutes")
        input("")
    
    print("="*50)
    print(f"Total Steps: {len(path) - 1}")
    print(f"Total Time:  {goal_node.cost} minutes")
    print("="*50)

def mainnnnnnnnn():
    logfile = LogFile()
    file_name = input("Enter manifest file name: ").strip()
    
    if not os.path.exists(file_name):
        print(f"Error: File '{file_name}' not found.")
        return
    
    #Initialize Ship
    ship = Ship(file_name)
    ship.read_manifest()
    
    logfile.createLog(file_name)
    logfile.logging(f"Manifest {file_name} is opened, there are {len(ship.containers)} containers on the ship")
    
    # Check Initial Balance
    if ship.calculate_balance():
        print("\n Ship is already BALANCED.")
        logfile.logging("Ship is already BALANCED.")
        logfile.closeLog()
        return

    print("\nShip is UNBALANCED.")
    print("Starting A* Search...")

    # RUN THE SEARCH
    solution_ship = ship.AstarSearch()

    # Handle Result
    if solution_ship:
        print_solution(solution_ship, logfile)
        print_outbound_manifest(solution_ship, file_name, logfile)
    else:
        print("\nError: No solution found. The ship cannot be balanced.")
        logfile.logging("Error: No solution found. The ship cannot be balanced.")
        
    # user commnent and to close
    comment = input("Enter any commnts to log file or press enter to exit: ")
    if comment:
        logfile.logging(f"A comment was written to the log “{comment}”")
    logfile.closeLog()
    
def main():
    root = tk.Tk()
    ShipBalancerGUI(root)
    root.mainloop()
    
if __name__ == "__main__":
    main()