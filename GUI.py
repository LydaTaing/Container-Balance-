import os
import tkinter as tk
from tkinter import messagebox, scrolledtext, simpledialog
from Ship import Ship
from LogFile import LogFile

def print_outbound_manifest(goal_node, file_name, logfile, text_widget):
    if isinstance(goal_node, Ship):
        ship = goal_node
    else:
        ship = goal_node.ship

    output = []
    for r in range(ship.R):
        for c in range(ship.C):
            spot = ship.grid[r][c]
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
            output.append(f"[{r_str},{c_str}], {{{weight}}}, {desc}")

    file_name_no_ext = os.path.splitext(file_name)[0]
    manifest_output_file = file_name_no_ext + "_OUTBOUND.txt"
    
    try:
        with open(manifest_output_file, "w") as f:
            f.write('\n'.join(output))
        text_widget.insert(tk.END, f"\nDone! {manifest_output_file} was written to the desktop.\n")
        text_widget.insert(tk.END, f"I have written an updated manifest to the desktop as {manifest_output_file}\n")
        text_widget.insert(tk.END, "Don't forget to email it to the captain.\n")
        text_widget.see(tk.END)
        logfile.logging(f"Finished a Cycle. Manifest {manifest_output_file} was written.")
    except Exception as e:
        text_widget.insert(tk.END, f"\nError: {e}\n")
        text_widget.see(tk.END)

def draw_ship_grid(canvas, ship, show_balance_status=False):
    canvas.delete("all")
    cell_size = 60
    y_offset = 80
    x_offset = 40
    
    # crane box setup
    crane_indicator_x = 10
    crane_indicator_y = 10
    crane_indicator_width = 200
    crane_indicator_height = 60

    canvas.create_rectangle(
        crane_indicator_x, crane_indicator_y,
        crane_indicator_x + crane_indicator_width, crane_indicator_y + crane_indicator_height,
        fill="#333333", outline="black", width=3
    )

    if ship.cranePosR == ship.craneRestR and ship.cranePosC == ship.craneRestC:
        crane_pos_text = "HOME [09,01]"
    else:
        crane_pos_text = f"[{ship.cranePosR + 1:02},{ship.cranePosC + 1:02}]"
    canvas.create_text(
        crane_indicator_x + crane_indicator_width / 2,
        crane_indicator_y + 12,
        text=f"CRANE: {crane_pos_text}",
        fill="white",
        font=("Arial", 10, "bold")
    )
    
    if ship.loadedCrane is not None:
        loaded_container = ship.loadedCrane
        container_size = 30
        desc_text = loaded_container.desc[:12]
        
        # box + spacing + text
        text_spacing = 8
        estimated_text_width = len(desc_text) * 5
        total_width = container_size + text_spacing + estimated_text_width
        
        # center box + text horizontally
        container_x = crane_indicator_x + (crane_indicator_width - total_width) / 2
        # put below crane indicator
        container_y = crane_indicator_y + 12 + 15

        # container box
        canvas.create_rectangle(
            container_x, container_y,
            container_x + container_size, container_y + container_size,
            fill="#FFD700", outline="black", width=2
        )

        # container weight text inside box
        canvas.create_text(
            container_x + container_size / 2,
            container_y + container_size / 2,
            text=f"{loaded_container.weight}",
            font=("Arial", 8, "bold")
        )

        # container description text to the right
        canvas.create_text(
            container_x + container_size + text_spacing,
            container_y + container_size / 2,
            text=desc_text,
            fill="white",
            font=("Arial", 7),
            anchor="w"
        )
    else:
        # crane is empty
        canvas.create_text(  # empty label
            crane_indicator_x + crane_indicator_width / 2,
            crane_indicator_y + crane_indicator_height / 2 + 15,
            text="EMPTY",
            fill="lime",
            font=("Arial", 12, "bold")
        )
    
    # Balance status indicator (only show if requested)
    if show_balance_status:  # show balance status
        canvas_width = int(canvas.cget("width"))
        
        balance_indicator_width = 200
        # far right position
        balance_indicator_x = canvas_width - balance_indicator_width - 10
        balance_indicator_y = crane_indicator_y
        balance_indicator_height = crane_indicator_height
        
        canvas.create_rectangle(
            balance_indicator_x, balance_indicator_y,
            balance_indicator_x + balance_indicator_width, balance_indicator_y + balance_indicator_height,
            fill="#2E7D32", outline="black", width=3
        )
        
        # BALANCED text
        canvas.create_text(
            balance_indicator_x + balance_indicator_width / 2,
            balance_indicator_y + balance_indicator_height / 2,
            text="BALANCED",
            fill="lightgreen",
            font=("Arial", 16, "bold")
        )
    
    # write row numbers
    for r in range(ship.R):
        # flip the row, as we display starting with the lowest row at the bottom
        display_row = ship.R - 1 - r
        x = x_offset - 20
        y = display_row * cell_size + cell_size / 2 + y_offset
        canvas.create_text(x, y, text=str(r + 1), font=("Arial", 10, "bold"))
    
    for r in range(ship.R):
        display_row = ship.R - 1 - r
        for c in range(ship.C):
            x1 = c * cell_size + x_offset
            y1 = display_row * cell_size + y_offset
            x2 = x1 + cell_size
            y2 = y1 + cell_size
            spot = ship.grid[r][c]
            
            if spot == "NAN":
                color = "#808080"
                text = "NAN"
            elif spot is None:
                color = "#FFFFFF"
                text = "UNUSED"
            else:
                color = "#87CEEB"
                text = f"{spot.weight}\n{spot.desc[:8]}"
            
            if r == ship.cranePosR and c == ship.cranePosC:
                color = "#FFD700"
                if ship.loadedCrane:
                    text = "CRANE"
                else:
                    text += " CRANE"
            
            canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black", width=2)
            canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2,
                                text=text, font=("Arial", 8), width=cell_size-10)
    
    # dashed center line
    mid_col = ship.C // 2
    line_x = mid_col * cell_size + x_offset
    canvas.create_line(
        line_x, y_offset,
        line_x, y_offset + ship.R * cell_size,
        fill="black", width=4, dash=(6, 3)
    )
    
    # write column numbers
    for c in range(ship.C):
        x = c * cell_size + cell_size / 2 + x_offset
        y = ship.R * cell_size + y_offset + 20
        canvas.create_text(x, y, text=str(c + 1), font=("Arial", 10, "bold"))

class ShipBalancerGUI:
    def __init__(self, root):
        # window setup
        self.root = root
        self.root.title("Ship Balancer")
        self.root.geometry("1000x750")
        self.logfile = LogFile()
        self.solution_path = []
        self.current_step = 0
        self.file_name = None
        self.current_ship = None
        self.comment_logged = False
        
        # top interact bar
        top_frame = tk.Frame(root)
        top_frame.pack(pady=10)
        tk.Label(top_frame, text="Manifest File:").pack(side=tk.LEFT, padx=5)
        self.file_entry = tk.Entry(top_frame, width=40)
        self.file_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(top_frame, text="Load & Balance", command=self.load_and_balance, bg="#4CAF50", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(top_frame, text="Clear Grid", command=self.clear_grid, bg="#dc3545", fg="white").pack(side=tk.LEFT, padx=5)
        
        # main canvas where grid is drawn
        canvas_frame = tk.Frame(root)
        canvas_frame.pack(pady=10)
        tk.Label(canvas_frame, text="Ship Grid", font=("Arial", 12, "bold")).pack()
        self.canvas = tk.Canvas(canvas_frame, width=720, height=600, bg="lightgray")
        self.canvas.pack()
        
        # navigation section below grid
        nav_frame = tk.Frame(root)
        nav_frame.pack(pady=10)
        self.prev_button = tk.Button(nav_frame, text="Previous", command=self.prev_step, state=tk.DISABLED)
        self.prev_button.pack(side=tk.LEFT, padx=5)
        self.step_label = tk.Label(nav_frame, text="", font=("Arial", 10))
        self.step_label.pack(side=tk.LEFT, padx=20)
        self.next_button = tk.Button(nav_frame, text="Next", command=self.next_step, state=tk.DISABLED)
        self.next_button.pack(side=tk.LEFT, padx=5)
        
        # Program output at the bottom
        text_frame = tk.Frame(root)
        text_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        tk.Label(text_frame, text="Output Log", font=("Arial", 10, "bold")).pack()
        self.text_output = scrolledtext.ScrolledText(text_frame, height=6, wrap=tk.WORD)
        self.text_output.pack(fill=tk.BOTH, expand=True, padx=10)

    def load_and_balance(self):
        # get rid of all prev data
        self.clear_grid()
        self.comment_logged = False
        
        # get file name
        self.file_name = self.file_entry.get().strip()
        if not os.path.exists(self.file_name):
            messagebox.showerror("Error", f"File '{self.file_name}' not found.")
            return
        
        # setup
        self.text_output.insert(tk.END, "Loading manifest...\n")
        ship = Ship(self.file_name)
        ship.read_manifest()
        self.current_ship = ship
        self.logfile.createLog(self.file_name)
        self.text_output.insert(tk.END, f"Log file was created: {self.logfile.filePath}\n")
        self.logfile.logging(f"Manifest {self.file_name} is opened, there are {len(ship.containers)} containers on the ship")
        
        # set the size of the grid canvas
        cell_size = 60
        crane_indicator_height = 80
        row_label_space = 40
        column_label_space = 40
        self.canvas.config(
            # +20 for padding on both sides
            width=ship.C * cell_size + row_label_space + 20,
            height=ship.R * cell_size + crane_indicator_height + column_label_space
        )

        if ship.calculate_balance():
            self.text_output.insert(tk.END, "\nShip is already BALANCED.\n")
            self.logfile.logging("Ship is already BALANCED.")
            self.logfile.closeLog()
            print_outbound_manifest(ship, self.file_name, self.logfile, self.text_output)
            # show balanced status on grid
            draw_ship_grid(self.canvas, ship, True)
            return
        else:
            draw_ship_grid(self.canvas, ship)

        self.text_output.insert(tk.END, "\nShip is UNBALANCED.\n")
        self.text_output.insert(tk.END, "Starting A* Search...\n")
    
        # show finding message
        try:
            w = int(self.canvas.cget("width"))
            self.canvas.delete("finding_msg")
            self.canvas.create_text(w//2, 30, text="Finding solution...", font=("Arial", 12, "bold"), fill="orange", tags="finding_msg")
            # GUI updates are batched - WE NEED THIS
            self.root.update_idletasks()
        except Exception:
            pass

        self.logfile.logging("A* search started: Finding solution...")
        self.text_output.see(tk.END)

        # here we go...
        solution_node = ship.AstarSearch()

        try:
            self.canvas.delete("finding_msg")
        except Exception:
            pass

        self.logfile.logging("A* search completed.")
        if solution_node:
            #print_outbound_manifest(solution_node, self.file_name, self.logfile, self.text_output)
            self.build_solution_path(solution_node)
            self.text_output.insert(tk.END, f"\nSolution found! {len(self.solution_path)-1} moves, {solution_node.cost} minutes.\n")
            self.logfile.logging(f"Balance solution found, it will require {len(self.solution_path)-1} moves/{solution_node.cost} minutes.")
            self.update_display()
            self.next_button.config(state=tk.NORMAL)
        else:
            self.text_output.insert(tk.END, "\nError: No solution found. The ship cannot be balanced.\n")
            self.logfile.logging("Error: No solution found. The ship cannot be balanced.")
            messagebox.showerror("Error", "No solution found. The ship cannot be balanced.")
        self.text_output.see(tk.END)

    def build_solution_path(self, goal_node):
        self.solution_path = []
        current = goal_node
        while current:
            self.solution_path.append(current)
            current = current.parent
        self.solution_path.reverse()

    def update_display(self):
        node = self.solution_path[self.current_step]
        self.current_ship = node.ship
        
        # only show the balance status at the final step
        is_final_step = self.current_step == len(self.solution_path) - 1
        
        draw_ship_grid(
            self.canvas,
            node.ship,
            show_balance_status=is_final_step
        )
        
        # update navigation section below grid
        self.step_label.config(text=f"Step: {self.current_step}/{len(self.solution_path)-1}")
        self.prev_button.config(state=tk.NORMAL if self.current_step > 0 else tk.DISABLED)
        self.next_button.config(state=tk.NORMAL if self.current_step < len(self.solution_path)-1 else tk.DISABLED)

        if self.current_step == len(self.solution_path) - 1:
            self.text_output.insert(tk.END, "\n" + "="*50 + "\n")
            self.text_output.insert(tk.END, f"Total Steps: {len(self.solution_path) - 1}\n")
            self.text_output.insert(tk.END, f"Total Time: {node.cost} minutes\n")
            self.text_output.insert(tk.END, "="*50 + "\n")
            
            print_outbound_manifest(node, self.file_name, self.logfile, self.text_output)
            
            # COMMENT INPUT POPUP 
            if not self.comment_logged:
                # Ask user for input via popup
                comment = simpledialog.askstring("Log Comment", "Enter any comments to log file or press OK to save:")
                
                if comment:
                    self.logfile.logging(f"A comment was written to the log: {comment}")
                    self.text_output.insert(tk.END, f"\nComment logged: {comment}\n")
                
                # Close the log cycle
                self.logfile.closeLog()
                self.comment_logged = True
            
            self.text_output.see(tk.END)
            
            

    def next_step(self):
        if self.current_step < len(self.solution_path) - 1:  # check bound
            self.current_step += 1
            node = self.solution_path[self.current_step]

            if node.parent:  
                step_cost = node.cost - node.parent.cost
            else:
                step_cost = node.cost

            move_log = f"{self.current_step} of {len(self.solution_path)-1}: {node.move}, {step_cost} minutes"
            self.text_output.insert(tk.END, "\n" + move_log + "\n")
            self.logfile.logging(move_log)

            self.text_output.see(tk.END)
            self.update_display()

    def prev_step(self):
        if self.current_step > 0:
            revoked_node = self.solution_path[self.current_step]
    
            revoked_log = f"Move revoked: {self.current_step} of {len(self.solution_path)-1}: {revoked_node.move}"
            self.text_output.insert(tk.END, "\n" + revoked_log + "\n")
            self.logfile.logging(revoked_log)

            self.text_output.see(tk.END)
            self.current_step -= 1
            self.update_display()

    def clear_grid(self):
        # clear setup
        self.current_ship = None
        self.solution_path = []
        self.current_step = 0
        self.file_name = None
        
        # clear canvas
        try:
            self.canvas.delete("all")
        except Exception:
            pass
        
        # clear and disable nagivation
        self.prev_button.config(state=tk.DISABLED)
        self.next_button.config(state=tk.DISABLED)
        self.step_label.config(text="")
        
        # clear output
        self.text_output.delete(1.0, tk.END)
