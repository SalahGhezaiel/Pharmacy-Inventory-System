import os
from tkinter import *
from tkinter import messagebox
import mysql.connector  
import subprocess
import sys

# Database connection
def connect_to_db():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",  
            password="",  
            database="pharmacy_db",  
            port = "3307"   
        )
        return connection
    except mysql.connector.Error as err:
        messagebox.showerror("Erreur", f"Erreur de connexion à la base de données : {err}")
        return None

def on_entry(e, entry, default_text):
    if entry.get() == default_text:
        entry.delete(0, 'end') 
        if default_text == "Password":
            entry.config(show="*") 

def on_leave(e, entry, default_text):
    if entry.get() == "":
        entry.insert(0, default_text)  
        if default_text == "Password":
            entry.config(show="")  

def signin():
    username = user.get()
    password = code.get()

    if username == "Username" or username == "":
        messagebox.showerror("Erreur", "Veuillez saisir un nom d'utilisateur.")
    elif password == "Password" or password == "":
        messagebox.showerror("Erreur", "Veuillez saisir un mot de passe.")
    else:
        connection = connect_to_db()
        if connection:
            cursor = connection.cursor()
            query = "SELECT * FROM users WHERE username = %s AND password = %s"
            cursor.execute(query, (username, password))
            result = cursor.fetchone()
            connection.close()

            if result:
                root.destroy()
                try:
                    script_path = os.path.join(os.getcwd(), "Tkinter.py")
                    print(f"Tentative d'ouverture : {script_path}")  
                    if os.path.exists(script_path):
                        os.system(f'python {script_path}')  
                    else:
                        messagebox.showerror("Erreur", f"Fichier introuvable :\n{script_path}")
                except Exception as e:
                    messagebox.showerror("Erreur", f"Impossible de lancer Tkinter.py\n{str(e)}")
            else:
                messagebox.showerror("Erreur", "Nom d'utilisateur ou mot de passe incorrect.")

# Interface graphique
root = Tk()
root.title('Welcome')
root.geometry("925x500+500+200")
root.configure(bg="#aac1dd")
root.resizable(False, False) 

# Set the window icon
icon_image = PhotoImage(file="images/icon.png") 
root.iconphoto(False, icon_image)

# Load the background image
bg_image = PhotoImage(file="images/background_login.png")
bg_label = Label(root, image=bg_image)
bg_label.place(x=0, y=0, relwidth=1, relheight=1) 

frame = Frame(root, width=350, height=350, bg="#aac1dd")
frame.place(x=50, y=70) 

heading = Label(frame, text='Sign in', fg='#1f00ff', bg='#aac1dd', font=('Helvetica', 23, 'bold'))
heading.place(x=120, y=5)  

# Champ Username
user = Entry(frame, width=25, fg='black', border=0, bg="#aac1dd", font=('Helvetica', 11))
user.place(x=30, y=80)  
user.insert(0, 'Username') 
user.bind("<FocusIn>", lambda e: on_entry(e, user, "Username"))  
user.bind("<FocusOut>", lambda e: on_leave(e, user, "Username")) 
Frame(frame, width=295, height=2, bg='black').place(x=25, y=107)  

# Champ Password
code = Entry(frame, width=25, fg='black', border=0, bg="#aac1dd", font=('Helvetica', 11))
code.place(x=30, y=150) 
code.insert(0, 'Password')  
code.bind("<FocusIn>", lambda e: on_entry(e, code, "Password")) 
code.bind("<FocusOut>", lambda e: on_leave(e, code, "Password"))  
Frame(frame, width=295, height=2, bg='black').place(x=25, y=177)

# Bouton Sign In
Button(frame, width=39, text='Sign in', bg='#1f00ff', fg='white', border=0, command=signin).place(x=35, y=204)  

root.mainloop()