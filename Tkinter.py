import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
from tkinter import messagebox
import mysql.connector

# Database connection
def connect_to_database():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="", 
            database="pharmacy_db",
            port="3307"
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

# Interface Graphique
class PharmacyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pharmacy Inventory Management")
        self.root.geometry("800x600+500+200")
        self.root.resizable(False, False) 
        
        # Load the background image
        self.bg_image = tk.PhotoImage(file="images/background_main.png")  
        bg_label = tk.Label(self.root, image=self.bg_image)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)  
        
        # Set the window icon
        self.icon_image = tk.PhotoImage(file="images/icon.png") 
        self.root.iconphoto(False, self.icon_image)
        
        # Connect to the database
        self.db_connection = connect_to_database()
        if not self.db_connection:
            print("Failed to connect to the database.")
            return

        # Composants UI
        self.create_widgets()
        self.populate_table()

    def create_widgets(self):
        # Title Label
        title_label = tk.Label(self.root, text="Pharmacy Inventory Management", font=("Arial", 16, "bold"), bg="#aac1dd", fg="#333")
        title_label.pack(pady=10)

        # Buttons Frame
        button_frame = tk.Frame(self.root, bg="#aac1dd")
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="View Expiry Status", font=("Arial", 12), bg="#2d3748", fg="white", padx=10, pady=5, command=self.open_expiry_window).grid(row=0, column=0, padx=10)
        tk.Button(button_frame, text="View Stock Status", font=("Arial", 12), bg="#2d3748", fg="white", padx=10, pady=5, command=self.open_stock_window).grid(row=0, column=1, padx=10)

        # Table for product display
        self.tree = ttk.Treeview(self.root, columns=("ID", "Name", "Category", "Price", "Quantity", "Expiration Date"), show='headings')
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        for col in self.tree['columns']:
            self.tree.heading(col, text=col, anchor=tk.W)
            self.tree.column(col, width=120, anchor=tk.W)

        # CRUD Buttons
        crud_frame = tk.Frame(self.root, bg="#aac1dd")
        crud_frame.pack(pady=10)

        tk.Button(crud_frame, text="Add Product", font=("Arial", 12), bg="#a8d5ba", fg="black", padx=10, pady=5, command=self.add_product).grid(row=0, column=0, padx=10)
        tk.Button(crud_frame, text="Edit Product", font=("Arial", 12), bg="#f6e3b4", fg="black", padx=10, pady=5, command=self.edit_product).grid(row=0, column=1, padx=10)
        tk.Button(crud_frame, text="Delete Product", font=("Arial", 12), bg="#f4a6a6", fg="black", padx=10, pady=5, command=self.delete_product).grid(row=0, column=2, padx=10)
        tk.Button(crud_frame, text="Refresh", font=("Arial", 12), bg="#8baecc", fg="black", padx=10, pady=5, command=self.populate_table).grid(row=0, column=3, padx=10)

    def populate_table(self):
        # Clear the table
        self.tree.delete(*self.tree.get_children())

        # Fetch data from the database
        cursor = self.db_connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM products")  
        rows = cursor.fetchall()

        for product in rows:
            self.tree.insert("", "end", values=(product["ID"], product["Name"], product["Category"], product["Price"], product["Quantity"], product["Expiration_Date"]))

        cursor.close()

    def open_expiry_window(self):
        expiry_window = tk.Toplevel(self.root)
        expiry_window.title("Expiration Status")
        expiry_window.geometry("600x400+550+250")
        
        # Set the window icon for the expiry window
        expiry_window.iconphoto(False, self.icon_image)

        # Create the Treeview widget
        tree = ttk.Treeview(expiry_window, columns=("ID", "Name", "Expiration Date", "Status"), show='headings')
        tree.pack(fill=tk.BOTH, expand=True)

        # Define column headings
        for col in tree['columns']:
            tree.heading(col, text=col, anchor=tk.W)
            tree.column(col, width=150, anchor=tk.W)

        
        tree.tag_configure("expired", foreground="red") 
        tree.tag_configure("valid", foreground="green")  

        
        today = datetime.today().date()  

        
        cursor = self.db_connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM products") 
        rows = cursor.fetchall()

        if not rows:
            messagebox.showinfo("Info", "No products found in the database.")
            return

        # Insert data into the Treeview
        for product in rows:
            exp_date = product.get("Expiration_Date") 

            if not exp_date:
                continue

            if exp_date < today:
                status = "Expired"
                tag = "expired"
            else:
                status = "Valid"
                tag = "valid"

            
            tree.insert("", "end", values=(product["ID"], product["Name"], exp_date, ""))

            
            item_id = tree.get_children()[-1]

            
            tree.item(item_id, values=(product["ID"], product["Name"], exp_date, status), tags=(tag,))

        cursor.close()

    def open_stock_window(self):
        stock_window = tk.Toplevel(self.root)
        stock_window.title("Stock Status")
        stock_window.geometry("600x400+550+250")
        
        # Set the window icon for the stock window
        stock_window.iconphoto(False, self.icon_image)

        # Create the Treeview widget
        tree = ttk.Treeview(stock_window, columns=("ID", "Name", "Quantity", "Stock Status"), show='headings')
        tree.pack(fill=tk.BOTH, expand=True)

        # Define column headings
        for col in tree['columns']:
            tree.heading(col, text=col, anchor=tk.W)
            tree.column(col, width=120, anchor=tk.W)

        
        tree.tag_configure("sufficient", foreground="green") 
        tree.tag_configure("low_stock", foreground="red")    

        
        cursor = self.db_connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM products")
        rows = cursor.fetchall()

       
        for product in rows:
            quantity = product["Quantity"]
            stock_status = "Low Stock" if quantity < 5 else "Sufficient"

            
            tree.insert(
                "", "end",
                values=(product["ID"], product["Name"], quantity, ""),  
            )

            
            item_id = tree.get_children()[-1]

            
            tree.item(item_id, values=(product["ID"], product["Name"], quantity, stock_status), tags=(stock_status.lower().replace(" ", "_"),))

        cursor.close()

    def add_product(self):
        # Create a new window for adding a product
        add_window = tk.Toplevel(self.root)
        add_window.title("Add Product")
        add_window.geometry("400x500+550+250")
        
        # Set the window icon for the stock window
        add_window.iconphoto(False, self.icon_image)

        # Predefined categories and their prefixes
        category_prefixes = {
            "Analgesics": "ANA",
            "Antibiotics": "ANT",
            "Antihistamines": "AHM",
            "Antacids": "AAC",
            "Antidepressants": "ADP",
            "Anticoagulants": "ACO",
            "Antihypertensives": "AHT",
            "Bronchodilators": "BRD",
            "Corticosteroids": "COR",
            "Hypoglycemics": "HYP",
            "NSAIDs": "NSA",
            "Vitamins & Supplements": "SUP"
        }

        # Labels and Entry fields for product details
        tk.Label(add_window, text="Name:").pack(pady=5)
        name_entry = tk.Entry(add_window)
        name_entry.pack(pady=5)

        tk.Label(add_window, text="Category:").pack(pady=5)
        category_combobox = ttk.Combobox(add_window, values=list(category_prefixes.keys()), state="readonly")
        category_combobox.pack(pady=5)

        tk.Label(add_window, text="Price:").pack(pady=5)
        price_entry = tk.Entry(add_window)
        price_entry.pack(pady=5)

        tk.Label(add_window, text="Quantity:").pack(pady=5)
        quantity_entry = tk.Entry(add_window)
        quantity_entry.pack(pady=5)

        tk.Label(add_window, text="Expiration Date (YYYY-MM-DD):").pack(pady=5)
        expiration_entry = tk.Entry(add_window)
        expiration_entry.pack(pady=5)

        # Function to validate inputs
        def validate_inputs():
            name = name_entry.get()
            category = category_combobox.get()
            price = price_entry.get()
            quantity = quantity_entry.get()
            expiration_date = expiration_entry.get()

            # Validate name 
            if not name.isalnum():
                messagebox.showerror("Error", "Product Name must only contain letters and numbers!")
                return False

            # Validate category 
            if category not in category_prefixes:
                messagebox.showerror("Error", "Category must be one of the predefined options!")
                return False

            # Validate price 
            try:
                price = float(price)
                if price <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Price must be a positive number!")
                return False

            # Validate quantity 
            if not quantity.isdigit() or int(quantity) <= 0:
                messagebox.showerror("Error", "Quantity must be a positive integer!")
                return False

            # Validate expiration date 
            try:
                datetime.strptime(expiration_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Error", "Expiration Date must be in the format YYYY-MM-DD!")
                return False

            return True

        # Function to generate the next product ID
        def generate_product_id(category):
            prefix = category_prefixes[category]
            cursor = self.db_connection.cursor()
            cursor.execute(f"SELECT ID FROM products WHERE ID LIKE '{prefix}-%' ORDER BY ID DESC LIMIT 1")
            last_id = cursor.fetchone()
            cursor.close()

            if last_id:
                # Extract the numeric part of the last ID and increment it
                last_number = int(last_id[0].split("-")[1])
                next_number = last_number + 1
            else:
                # Start from 1 if no ID exists for this category
                next_number = 1

            # Format the new ID with the prefix and a four-digit number
            return f"{prefix}-{next_number:04d}"

        # Function to save the product to the database
        def save_product():
            if not validate_inputs():
                return

            name = name_entry.get()
            category = category_combobox.get()
            price = float(price_entry.get())
            quantity = int(quantity_entry.get())
            expiration_date = expiration_entry.get()

            try:
                cursor = self.db_connection.cursor(dictionary=True)

                
                cursor.execute(
                    "SELECT * FROM products WHERE LOWER(Name) = %s AND Category = %s AND Price = %s AND Expiration_Date = %s",
                    (name.lower(), category, price, expiration_date),
                )
                existing_product = cursor.fetchone()

                if existing_product:
                    
                    new_quantity = existing_product["Quantity"] + quantity
                    cursor.execute(
                        "UPDATE products SET Quantity = %s WHERE ID = %s",
                        (new_quantity, existing_product["ID"]),
                    )
                    messagebox.showinfo("Success", "Existing product updated successfully!")
                else:
                    
                    product_id = generate_product_id(category)
                    cursor.execute(
                        "INSERT INTO products (ID, Name, Category, Price, Quantity, Expiration_Date) VALUES (%s, %s, %s, %s, %s, %s)",
                        (product_id, name, category, price, quantity, expiration_date),
                    )
                    messagebox.showinfo("Success", f"Product added successfully with ID: {product_id}")

                self.db_connection.commit()
                cursor.close()
                add_window.destroy()
                self.populate_table()
            except mysql.connector.Error as err:
                messagebox.showerror("Error", f"Database error: {err}")

        
        tk.Button(add_window, text="Save", command=save_product).pack(pady=20)

    def edit_product(self):
        # Get the selected product
        selected_item = self.tree.selection()
        if not selected_item:
            tk.messagebox.showerror("Error", "No product selected!")
            return

        product = self.tree.item(selected_item)["values"]

        # Create a new window for editing the product
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Product")
        edit_window.geometry("400x500+550+250")
        
        # Set the window icon for the stock window
        edit_window.iconphoto(False, self.icon_image)

        # Predefined categories and their prefixes
        category_prefixes = {
            "Analgesics": "ANA",
            "Antibiotics": "ANT",
            "Antihistamines": "AHM",
            "Antacids": "AAC",
            "Antidepressants": "ADP",
            "Anticoagulants": "ACO",
            "Antihypertensives": "AHT",
            "Bronchodilators": "BRD",
            "Corticosteroids": "COR",
            "Hypoglycemics": "HYP",
            "NSAIDs": "NSA",
            "Vitamins & Supplements": "SUP"
        }

        # Labels and Entry fields for product details
        tk.Label(edit_window, text="Name:").pack(pady=5)
        name_entry = tk.Entry(edit_window)
        name_entry.insert(0, product[1])
        name_entry.pack(pady=5)

        tk.Label(edit_window, text="Category:").pack(pady=5)
        category_combobox = ttk.Combobox(edit_window, values=list(category_prefixes.keys()), state="readonly")
        category_combobox.set(product[2])  
        category_combobox.pack(pady=5)

        tk.Label(edit_window, text="Price:").pack(pady=5)
        price_entry = tk.Entry(edit_window)
        price_entry.insert(0, product[3])
        price_entry.pack(pady=5)

        tk.Label(edit_window, text="Quantity:").pack(pady=5)
        quantity_entry = tk.Entry(edit_window)
        quantity_entry.insert(0, product[4])
        quantity_entry.pack(pady=5)

        tk.Label(edit_window, text="Expiration Date (YYYY-MM-DD):").pack(pady=5)
        expiration_entry = tk.Entry(edit_window)
        expiration_entry.insert(0, product[5])
        expiration_entry.pack(pady=5)

        # Function to validate inputs
        def validate_inputs():
            name = name_entry.get()
            category = category_combobox.get()
            price = price_entry.get()
            quantity = quantity_entry.get()
            expiration_date = expiration_entry.get()

            # Validate name 
            if not name.isalnum():
                messagebox.showerror("Error", "Product Name must only contain letters and numbers!")
                return False

            # Validate category 
            if category not in category_prefixes:
                messagebox.showerror("Error", "Category must be one of the predefined options!")
                return False

            # Validate price 
            try:
                price = float(price)
                if price <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Price must be a positive number!")
                return False

            # Validate quantity 
            if not quantity.isdigit() or int(quantity) <= 0:
                messagebox.showerror("Error", "Quantity must be a positive integer!")
                return False

            # Validate expiration date 
            try:
                datetime.strptime(expiration_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Error", "Expiration Date must be in the format YYYY-MM-DD!")
                return False

            return True

        # Function to generate the next product ID
        def generate_product_id(category):
            prefix = category_prefixes[category]
            cursor = self.db_connection.cursor()
            cursor.execute(f"SELECT ID FROM products WHERE ID LIKE '{prefix}-%' ORDER BY ID DESC LIMIT 1")
            last_id = cursor.fetchone()
            cursor.close()

            if last_id:
                last_number = int(last_id[0].split("-")[1])
                next_number = last_number + 1
            else:
                next_number = 1

            
            return f"{prefix}-{next_number:04d}"

        
        def update_product():
            if not validate_inputs():
                return

            name = name_entry.get()
            category = category_combobox.get()
            price = float(price_entry.get())
            quantity = int(quantity_entry.get())
            expiration_date = expiration_entry.get()

            # Generate a new ID if the category has changed
            new_id = product[0]
            if category != product[2]:  
                new_id = generate_product_id(category)

            try:
                cursor = self.db_connection.cursor(dictionary=True)

                # Update the product in the database
                cursor.execute(
                    "UPDATE products SET ID=%s, Name=%s, Category=%s, Price=%s, Quantity=%s, Expiration_Date=%s WHERE ID=%s",
                    (new_id, name, category, price, quantity, expiration_date, product[0]),
                )
                self.db_connection.commit()
                cursor.close()
                messagebox.showinfo("Success", "Product updated successfully!")
                edit_window.destroy()
                self.populate_table()
            except mysql.connector.Error as err:
                messagebox.showerror("Error", f"Database error: {err}")

        
        tk.Button(edit_window, text="Save", command=update_product).pack(pady=20)

    def delete_product(self):
        # Create a new window for multi-selection delete
        delete_window = tk.Toplevel(self.root)
        delete_window.title("Delete Products")
        delete_window.geometry("600x400+550+250")
        
        # Set the window icon for the stock window
        delete_window.iconphoto(False, self.icon_image)

        # Frame for the product list with checkboxes
        frame = tk.Frame(delete_window)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Scrollbar for the product list
        scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Canvas for the product list
        canvas = tk.Canvas(frame, yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=canvas.yview)

        # Frame inside the canvas for checkboxes
        checkbox_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=checkbox_frame, anchor="nw")

        # Fetch products from the database
        cursor = self.db_connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM products")
        rows = cursor.fetchall()
        cursor.close()

        checkbox_vars = {}

        # Add checkboxes for each product
        for product in rows:
            var = tk.BooleanVar()
            checkbox_vars[product["ID"]] = var
            tk.Checkbutton(checkbox_frame, text=f"{product['Name']} (Category: {product['Category']}, Quantity: {product['Quantity']}, Expiry: {product['Expiration_Date']})", variable=var).pack(anchor="w")

        # Function to select all checkboxes
        def select_all():
            for var in checkbox_vars.values():
                var.set(True)

        # Function to deselect all checkboxes
        def deselect_all():
            for var in checkbox_vars.values():
                var.set(False)

        # Buttons for "Select All" and "Deselect All"
        tk.Button(delete_window, text="Select All", command=select_all).pack(pady=5)
        tk.Button(delete_window, text="Deselect All", command=deselect_all).pack(pady=5)

        # Function to delete selected products
        def confirm_delete():
            selected_ids = [product_id for product_id, var in checkbox_vars.items() if var.get()]
            if not selected_ids:
                messagebox.showerror("Error", "No products selected for deletion!")
                return

            # Confirmation prompt
            confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete {len(selected_ids)} product(s)?")
            if not confirm:
                return

            # Delete selected products from the database
            try:
                cursor = self.db_connection.cursor()
                for product_id in selected_ids:
                    cursor.execute("DELETE FROM products WHERE ID=%s", (product_id,))
                self.db_connection.commit()
                cursor.close()
                messagebox.showinfo("Success", f"{len(selected_ids)} product(s) deleted successfully!")
                delete_window.destroy()
                self.populate_table()
            except mysql.connector.Error as err:
                messagebox.showerror("Error", f"Database error: {err}")

        # Delete button
        tk.Button(delete_window, text="Delete Selected", command=confirm_delete, bg="#f44336", fg="white").pack(pady=10)

        # Configure the canvas scroll region
        checkbox_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

if __name__ == "__main__":
    root = tk.Tk()
    app = PharmacyApp(root)
    root.mainloop()
    
    
    
    
    
    
    
    