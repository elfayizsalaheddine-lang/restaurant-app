import tkinter as tk
from tkinter import messagebox
import sqlite3
from datetime import datetime


# ============================================================
# DATABASE
# ============================================================

db = sqlite3.connect("restaurant.db")
cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS menu (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    price REAL NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    total REAL NOT NULL,
    date TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    product TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    total REAL NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS settings (
    id INTEGER PRIMARY KEY,
    restaurant_open INTEGER NOT NULL DEFAULT 0,
    opened_at TEXT
)
""")

db.commit()


# ============================================================
# CODES
# ============================================================

CLIENT_CODE = "1111"
PATRON_CODE = "9999"


# ============================================================
# VARIABLES
# ============================================================

cart = []
client_mode = False


# ============================================================
# DEFAULT MENU
# ============================================================

cursor.execute("SELECT COUNT(*) FROM menu")

if cursor.fetchone()[0] == 0:

    default_products = [
        ("Pizza", 40),
        ("Tacos", 30),
        ("Burger", 35),
        ("Jus", 12)
    ]

    cursor.executemany(
        "INSERT INTO menu (name, price) VALUES (?, ?)",
        default_products
    )

    db.commit()


# ============================================================
# RESTAURANT SETTINGS
# ============================================================

cursor.execute(
    "SELECT restaurant_open FROM settings WHERE id = 1"
)

setting = cursor.fetchone()

if setting is None:

    cursor.execute("""
        INSERT INTO settings
        (id, restaurant_open, opened_at)
        VALUES (1, 0, NULL)
    """)

    db.commit()


# ============================================================
# MAIN WINDOW
# ============================================================

window = tk.Tk()

window.title("Restaurant Manager")

window.geometry("900x750")

window.resizable(False, False)


# ============================================================
# DATABASE FUNCTIONS
# ============================================================

def restaurant_is_open():

    cursor.execute(
        "SELECT restaurant_open FROM settings WHERE id = 1"
    )

    result = cursor.fetchone()

    return result[0] == 1


def get_opened_at():

    cursor.execute(
        "SELECT opened_at FROM settings WHERE id = 1"
    )

    result = cursor.fetchone()

    return result[0]


def get_menu():

    cursor.execute(
        "SELECT name, price FROM menu ORDER BY id"
    )

    return cursor.fetchall()


# ============================================================
# CLEAR WINDOW
# ============================================================

def clear_window():

    for widget in window.winfo_children():
        widget.destroy()


# ============================================================
# HOME
# ============================================================

def home_page():

    global client_mode

    client_mode = False

    clear_window()

    title = tk.Label(
        window,
        text="🍽️ RESTAURANT",
        font=("Arial", 34, "bold")
    )

    title.pack(pady=60)

    subtitle = tk.Label(
        window,
        text="Restaurant Manager",
        font=("Arial", 18)
    )

    subtitle.pack(pady=5)

    tk.Button(
        window,
        text="👤 CLIENT",
        font=("Arial", 18, "bold"),
        width=25,
        height=2,
        command=client_login
    ).pack(pady=20)

    tk.Button(
        window,
        text="👨‍💼 PATRON",
        font=("Arial", 18, "bold"),
        width=25,
        height=2,
        command=patron_login
    ).pack(pady=20)


# ============================================================
# CLIENT LOGIN
# ============================================================

def client_login():

    clear_window()

    title = tk.Label(
        window,
        text="👤 MODE CLIENT",
        font=("Arial", 28, "bold")
    )

    title.pack(pady=50)

    tk.Label(
        window,
        text="Code Client",
        font=("Arial", 16)
    ).pack()

    code_var = tk.StringVar()

    entry = tk.Entry(
        window,
        textvariable=code_var,
        show="*",
        font=("Arial", 18),
        width=15
    )

    entry.pack(pady=15)

    entry.focus()

    def verify_client():

        if code_var.get() != CLIENT_CODE:

            messagebox.showerror(
                "Erreur",
                "❌ Code Client incorrect."
            )

            return

        if not restaurant_is_open():

            messagebox.showwarning(
                "Restaurant fermé",
                "🔴 Le restaurant est fermé.\n\n"
                "Le Patron doit ouvrir la journée."
            )

            return

        client_page()

    tk.Button(
        window,
        text="🔓 Entrer",
        font=("Arial", 16, "bold"),
        width=18,
        command=verify_client
    ).pack(pady=15)

    tk.Button(
        window,
        text="Retour",
        command=home_page
    ).pack(pady=10)


# ============================================================
# CLIENT PAGE
# ============================================================

def client_page():

    global cart
    global client_mode

    client_mode = True
    cart = []

    clear_window()

    title = tk.Label(
        window,
        text="👤 ESPACE CLIENT",
        font=("Arial", 28, "bold")
    )

    title.pack(pady=15)

    tk.Label(
        window,
        text="🟢 Restaurant ouvert",
        font=("Arial", 15, "bold")
    ).pack()


    # --------------------------------------------------------
    # MENU
    # --------------------------------------------------------

    menu_frame = tk.LabelFrame(
        window,
        text="🍽️ MENU",
        font=("Arial", 16, "bold"),
        padx=20,
        pady=20
    )

    menu_frame.pack(
        padx=50,
        pady=20,
        fill="x"
    )

    items = get_menu()

    if not items:

        tk.Label(
            menu_frame,
            text="Aucun produit disponible.",
            font=("Arial", 15)
        ).pack()

        return

    product_names = [
        item[0]
        for item in items
    ]

    product_var = tk.StringVar()

    product_var.set(product_names[0])

    product_menu = tk.OptionMenu(
        menu_frame,
        product_var,
        *product_names
    )

    product_menu.config(
        width=20,
        font=("Arial", 14)
    )

    product_menu.grid(
        row=0,
        column=0,
        padx=10
    )

    tk.Label(
        menu_frame,
        text="Quantité:",
        font=("Arial", 14)
    ).grid(
        row=0,
        column=1,
        padx=10
    )

    quantity_var = tk.StringVar()

    quantity_entry = tk.Entry(
        menu_frame,
        textvariable=quantity_var,
        width=8,
        font=("Arial", 14)
    )

    quantity_entry.grid(
        row=0,
        column=2,
        padx=10
    )

    result_label = tk.Label(
        window,
        text="",
        font=("Arial", 14)
    )

    result_label.pack(pady=5)


    # --------------------------------------------------------
    # ADD TO CART
    # --------------------------------------------------------

    def add_to_cart():

        product = product_var.get()

        try:

            quantity = int(
                quantity_var.get()
            )

            if quantity <= 0:
                raise ValueError

        except ValueError:

            messagebox.showwarning(
                "Erreur",
                "دخل كمية صحيحة."
            )

            return

        cursor.execute(
            "SELECT price FROM menu WHERE name = ?",
            (product,)
        )

        result = cursor.fetchone()

        if result is None:

            messagebox.showerror(
                "Erreur",
                "Produit introuvable."
            )

            return

        price = result[0]

        total = price * quantity

        cart.append({
            "product": product,
            "quantity": quantity,
            "total": total
        })

        quantity_var.set("")

        result_label.config(
            text=f"✅ {product} x {quantity} ajouté au panier"
        )


    tk.Button(
        window,
        text="➕ Ajouter au panier",
        font=("Arial", 15, "bold"),
        width=25,
        command=add_to_cart
    ).pack(pady=7)


    # --------------------------------------------------------
    # SHOW CART
    # --------------------------------------------------------

    def show_cart():

        if not cart:

            messagebox.showinfo(
                "Panier",
                "🛒 Panier vide."
            )

            return

        text = "🛒 PANIER\n\n"

        total = 0

        for item in cart:

            text += (
                f"{item['product']} x "
                f"{item['quantity']} = "
                f"{item['total']:.2f} DH\n"
            )

            total += item["total"]

        text += (
            "\n----------------------\n"
            f"💰 TOTAL : {total:.2f} DH"
        )

        messagebox.showinfo(
            "Mon Panier",
            text
        )


    tk.Button(
        window,
        text="🛒 Voir le panier",
        font=("Arial", 15),
        width=25,
        command=show_cart
    ).pack(pady=7)


    # --------------------------------------------------------
    # CLEAR CART
    # --------------------------------------------------------

    def clear_cart():

        if not cart:
            return

        cart.clear()

        result_label.config(
            text="🗑️ Panier vidé."
        )


    tk.Button(
        window,
        text="🗑️ Vider le panier",
        font=("Arial", 15),
        width=25,
        command=clear_cart
    ).pack(pady=7)


    # --------------------------------------------------------
    # VALIDATE ORDER
    # --------------------------------------------------------

    def validate_order():

        if not cart:

            messagebox.showwarning(
                "Commande",
                "🛒 Panier vide."
            )

            return

        total = sum(
            item["total"]
            for item in cart
        )

        now = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        cursor.execute(
            """
            INSERT INTO orders (total, date)
            VALUES (?, ?)
            """,
            (total, now)
        )

        order_id = cursor.lastrowid

        for item in cart:

            cursor.execute(
                """
                INSERT INTO order_items
                (order_id, product, quantity, total)
                VALUES (?, ?, ?, ?)
                """,
                (
                    order_id,
                    item["product"],
                    item["quantity"],
                    item["total"]
                )
            )

        db.commit()

        cart.clear()

        messagebox.showinfo(
            "Commande validée",
            f"✅ Commande #{order_id}\n\n"
            f"💰 Total : {total:.2f} DH"
        )

        client_page()


    tk.Button(
        window,
        text="✅ VALIDER COMMANDE",
        font=("Arial", 16, "bold"),
        width=25,
        height=2,
        command=validate_order
    ).pack(pady=10)


    # --------------------------------------------------------
    # CLIENT EXIT WITH PATRON CODE
    # --------------------------------------------------------

    def client_exit():

        code_window = tk.Toplevel(window)

        code_window.title(
            "Autorisation Patron"
        )

        code_window.geometry(
            "430x300"
        )

        code_window.resizable(
            False,
            False
        )

        code_window.grab_set()

        tk.Label(
            code_window,
            text="🔐 SORTIE CLIENT",
            font=("Arial", 21, "bold")
        ).pack(pady=25)

        tk.Label(
            code_window,
            text="Code Patron obligatoire",
            font=("Arial", 14)
        ).pack()

        patron_var = tk.StringVar()

        entry = tk.Entry(
            code_window,
            textvariable=patron_var,
            show="*",
            font=("Arial", 18),
            width=16
        )

        entry.pack(pady=15)

        entry.focus()

        def verify():

            global client_mode

            if patron_var.get() == PATRON_CODE:

                client_mode = False

                code_window.grab_release()
                code_window.destroy()

                home_page()

            else:

                messagebox.showerror(
                    "Accès refusé",
                    "❌ Code Patron incorrect.",
                    parent=code_window
                )

                entry.delete(
                    0,
                    tk.END
                )

        tk.Button(
            code_window,
            text="🔓 Confirmer",
            font=("Arial", 14, "bold"),
            width=15,
            command=verify
        ).pack(pady=10)


    tk.Button(
        window,
        text="🔒 SORTIR DU MODE CLIENT",
        font=("Arial", 14, "bold"),
        width=25,
        command=client_exit
    ).pack(pady=20)


# ============================================================
# PATRON LOGIN
# ============================================================

def patron_login():

    clear_window()

    title = tk.Label(
        window,
        text="👨‍💼 ESPACE PATRON",
        font=("Arial", 28, "bold")
    )

    title.pack(pady=50)

    tk.Label(
        window,
        text="Code Patron",
        font=("Arial", 16)
    ).pack()

    code_var = tk.StringVar()

    entry = tk.Entry(
        window,
        textvariable=code_var,
        show="*",
        font=("Arial", 18),
        width=15
    )

    entry.pack(pady=15)

    entry.focus()

    def verify():

        if code_var.get() == PATRON_CODE:

            patron_dashboard()

        else:

            messagebox.showerror(
                "Erreur",
                "❌ Code Patron incorrect."
            )

            entry.delete(
                0,
                tk.END
            )

    tk.Button(
        window,
        text="🔓 SE CONNECTER",
        font=("Arial", 16, "bold"),
        width=20,
        command=verify
    ).pack(pady=15)

    tk.Button(
        window,
        text="Retour",
        command=home_page
    ).pack(pady=10)


# ============================================================
# OPEN / CLOSE DAY
# ============================================================

def toggle_restaurant():

    if restaurant_is_open():

        answer = messagebox.askyesno(
            "Fermer la journée",
            "واش متأكد بغيتي تسد journée؟"
        )

        if not answer:
            return

        cursor.execute(
            """
            UPDATE settings
            SET restaurant_open = 0,
                opened_at = NULL
            WHERE id = 1
            """
        )

        db.commit()

        messagebox.showinfo(
            "Journée",
            "🔒 Journée fermée."
        )

    else:

        now = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        cursor.execute(
            """
            UPDATE settings
            SET restaurant_open = 1,
                opened_at = ?
            WHERE id = 1
            """,
            (now,)
        )

        db.commit()

        messagebox.showinfo(
            "Journée",
            "🔓 Journée ouverte."
        )

    patron_dashboard()


# ============================================================
# PATRON DASHBOARD
# ============================================================

def patron_dashboard():

    clear_window()

    title = tk.Label(
        window,
        text="👨‍💼 DASHBOARD PATRON",
        font=("Arial", 28, "bold")
    )

    title.pack(pady=15)


    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    if restaurant_is_open():

        status_text = "🟢 RESTAURANT OUVERT"

    else:

        status_text = "🔴 RESTAURANT FERMÉ"


    tk.Label(
        window,
        text=status_text,
        font=("Arial", 16, "bold")
    ).pack()


    # --------------------------------------------------------
    # CURRENT DAY STATISTICS
    # --------------------------------------------------------

    opened_at = get_opened_at()

    if opened_at:

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM orders
            WHERE date >= ?
            """,
            (opened_at,)
        )

        orders_count = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT COALESCE(SUM(total), 0)
            FROM orders
            WHERE date >= ?
            """,
            (opened_at,)
        )

        revenue = cursor.fetchone()[0]

    else:

        orders_count = 0
        revenue = 0


    stats_frame = tk.LabelFrame(
        window,
        text="📊 JOURNÉE ACTUELLE",
        font=("Arial", 15, "bold"),
        padx=30,
        pady=15
    )

    stats_frame.pack(
        padx=50,
        pady=15,
        fill="x"
    )


    tk.Label(
        stats_frame,
        text=f"📦 Commandes : {orders_count}",
        font=("Arial", 16)
    ).pack(pady=5)


    tk.Label(
        stats_frame,
        text=f"💰 Chiffre d'affaires : {revenue:.2f} DH",
        font=("Arial", 17, "bold")
    ).pack(pady=5)


    # --------------------------------------------------------
    # PRODUCTS SOLD TODAY
    # --------------------------------------------------------

    sold_frame = tk.LabelFrame(
        window,
        text="🍕 PRODUITS VENDUS",
        font=("Arial", 15, "bold"),
        padx=20,
        pady=10
    )

    sold_frame.pack(
        padx=50,
        pady=10,
        fill="x"
    )


    if opened_at:

        cursor.execute(
            """
            SELECT oi.product, SUM(oi.quantity)
            FROM order_items oi
            JOIN orders o
            ON oi.order_id = o.id
            WHERE o.date >= ?
            GROUP BY oi.product
            ORDER BY SUM(oi.quantity) DESC
            """,
            (opened_at,)
        )

        products = cursor.fetchall()

    else:

        products = []


    if not products:

        tk.Label(
            sold_frame,
            text="Aucune vente pour cette journée.",
            font=("Arial", 13)
        ).pack()

    else:

        for product, quantity in products:

            tk.Label(
                sold_frame,
                text=f"🍽️ {product} : {quantity}",
                font=("Arial", 13)
            ).pack(
                anchor="w",
                pady=2
            )


    # --------------------------------------------------------
    # BUTTONS
    # --------------------------------------------------------

    tk.Button(
        window,
        text="🔓 OUVRIR / 🔒 FERMER JOURNÉE",
        font=("Arial", 14, "bold"),
        width=32,
        command=toggle_restaurant
    ).pack(pady=7)


    tk.Button(
        window,
        text="🍽️ GÉRER LE MENU",
        font=("Arial", 14),
        width=32,
        command=manage_menu
    ).pack(pady=7)


    tk.Button(
        window,
        text="📋 VOIR LES COMMANDES",
        font=("Arial", 14),
        width=32,
        command=view_orders
    ).pack(pady=7)


    tk.Button(
        window,
        text="🚪 QUITTER ESPACE PATRON",
        font=("Arial", 14),
        width=32,
        command=home_page
    ).pack(pady=7)


# ============================================================
# VIEW ORDERS
# ============================================================

def view_orders():

    clear_window()

    title = tk.Label(
        window,
        text="📋 COMMANDES",
        font=("Arial", 26, "bold")
    )

    title.pack(pady=20)


    opened_at = get_opened_at()


    if opened_at:

        cursor.execute(
            """
            SELECT id, total, date
            FROM orders
            WHERE date >= ?
            ORDER BY id DESC
            """,
            (opened_at,)
        )

    else:

        cursor.execute(
            """
            SELECT id, total, date
            FROM orders
            ORDER BY id DESC
            LIMIT 50
            """
        )


    orders = cursor.fetchall()


    list_frame = tk.Frame(window)

    list_frame.pack(
        padx=50,
        pady=10
    )


    if not orders:

        tk.Label(
            list_frame,
            text="Aucune commande.",
            font=("Arial", 15)
        ).pack()

    else:

        for order_id, total, date in orders:

            text = (
                f"Commande #{order_id}   |   "
                f"{total:.2f} DH   |   {date}"
            )

            tk.Label(
                list_frame,
                text=text,
                font=("Arial", 12)
            ).pack(
                anchor="w",
                pady=4
            )


    tk.Button(
        window,
        text="⬅️ Retour Dashboard",
        font=("Arial", 14),
        command=patron_dashboard
    ).pack(pady=25)


# ============================================================
# MANAGE MENU
# ============================================================

def manage_menu():

    clear_window()

    title = tk.Label(
        window,
        text="🍽️ GESTION DU MENU",
        font=("Arial", 26, "bold")
    )

    title.pack(pady=15)


    # --------------------------------------------------------
    # CURRENT MENU
    # --------------------------------------------------------

    list_frame = tk.LabelFrame(
        window,
        text="📋 MENU ACTUEL",
        font=("Arial", 15, "bold"),
        padx=20,
        pady=10
    )

    list_frame.pack(
        padx=50,
        pady=10,
        fill="x"
    )


    # --------------------------------------------------------
    # VARIABLES
    # --------------------------------------------------------

    name_var = tk.StringVar()
    price_var = tk.StringVar()

    modify_var = tk.StringVar()
    modify_price_var = tk.StringVar()

    delete_var = tk.StringVar()


    # --------------------------------------------------------
    # ADD PRODUCT
    # --------------------------------------------------------

    add_frame = tk.LabelFrame(
        window,
        text="➕ AJOUTER PRODUIT",
        font=("Arial", 14, "bold"),
        padx=10,
        pady=10
    )

    add_frame.pack(
        padx=50,
        pady=5,
        fill="x"
    )


    tk.Label(
        add_frame,
        text="Nom:"
    ).grid(
        row=0,
        column=0,
        padx=5
    )


    tk.Entry(
        add_frame,
        textvariable=name_var,
        width=15
    ).grid(
        row=0,
        column=1,
        padx=5
    )


    tk.Label(
        add_frame,
        text="Prix:"
    ).grid(
        row=0,
        column=2,
        padx=5
    )


    tk.Entry(
        add_frame,
        textvariable=price_var,
        width=10
    ).grid(
        row=0,
        column=3,
        padx=5
    )


    # --------------------------------------------------------
    # MODIFY MENU WIDGET
    # --------------------------------------------------------

    modify_menu = tk.OptionMenu(
        window,
        modify_var,
        ""
    )

    modify_menu.config(
        width=18,
        font=("Arial", 12)
    )


    # --------------------------------------------------------
    # DELETE MENU WIDGET
    # --------------------------------------------------------

    delete_menu = tk.OptionMenu(
        window,
        delete_var,
        ""
    )

    delete_menu.config(
        width=18,
        font=("Arial", 12)
    )


    # --------------------------------------------------------
    # REFRESH MENU
    # --------------------------------------------------------

    def refresh_menu():

        for widget in list_frame.winfo_children():
            widget.destroy()


        items = get_menu()


        for name, price in items:

            tk.Label(
                list_frame,
                text=f"🍽️ {name}   —   {price:.2f} DH",
                font=("Arial", 14)
            ).pack(
                anchor="w",
                pady=3
            )


        # Update modify dropdown

        modify_menu["menu"].delete(
            0,
            "end"
        )


        # Update delete dropdown

        delete_menu["menu"].delete(
            0,
            "end"
        )


        for name, price in items:

            modify_menu["menu"].add_command(
                label=name,
                command=lambda value=name:
                modify_var.set(value)
            )


            delete_menu["menu"].add_command(
                label=name,
                command=lambda value=name:
                delete_var.set(value)
            )


        if items:

            modify_var.set(
                items[0][0]
            )

            delete_var.set(
                items[0][0]
            )

        else:

            modify_var.set("")
            delete_var.set("")


    # --------------------------------------------------------
    # ADD PRODUCT FUNCTION
    # --------------------------------------------------------

    def add_product():

        name = name_var.get().strip()

        if not name:

            messagebox.showwarning(
                "Erreur",
                "دخل اسم المنتج."
            )

            return


        try:

            price = float(
                price_var.get()
            )

            if price <= 0:
                raise ValueError

        except ValueError:

            messagebox.showwarning(
                "Erreur",
                "دخل ثمن صحيح."
            )

            return


        try:

            cursor.execute(
                """
                INSERT INTO menu
                (name, price)
                VALUES (?, ?)
                """,
                (name, price)
            )

            db.commit()

        except sqlite3.IntegrityError:

            messagebox.showwarning(
                "Erreur",
                "هاد المنتج موجود من قبل."
            )

            return


        name_var.set("")
        price_var.set("")

        refresh_menu()


    tk.Button(
        add_frame,
        text="➕ Ajouter",
        command=add_product
    ).grid(
        row=0,
        column=4,
        padx=10
    )


    # --------------------------------------------------------
    # MODIFY SECTION
    # --------------------------------------------------------

    modify_frame = tk.LabelFrame(
        window,
        text="✏️ MODIFIER PRIX",
        font=("Arial", 14, "bold"),
        padx=10,
        pady=10
    )

    modify_frame.pack(
        padx=50,
        pady=5,
        fill="x"
    )


    modify_menu.pack(
        side="left",
        padx=15
    )


    tk.Entry(
        modify_frame,
        textvariable=modify_price_var,
        width=10
    ).pack(
        side="left",
        padx=10
    )


    def modify_product():

        product = modify_var.get()

        if not product:

            messagebox.showwarning(
                "Erreur",
                "Choisis un produit."
            )

            return


        try:

            new_price = float(
                modify_price_var.get()
            )

            if new_price <= 0:
                raise ValueError

        except ValueError:

            messagebox.showwarning(
                "Erreur",
                "دخل ثمن صحيح."
            )

            return


        cursor.execute(
            """
            UPDATE menu
            SET price = ?
            WHERE name = ?
            """,
            (new_price, product)
        )

        db.commit()

        modify_price_var.set("")

        refresh_menu()


        messagebox.showinfo(
            "Menu",
            "✅ Prix modifié."
        )


    tk.Button(
        modify_frame,
        text="✏️ Modifier",
        command=modify_product
    ).pack(
        side="left",
        padx=10
    )


    # --------------------------------------------------------
    # DELETE SECTION
    # --------------------------------------------------------

    delete_frame = tk.LabelFrame(
        window,
        text="🗑️ SUPPRIMER PRODUIT",
        font=("Arial", 14, "bold"),
        padx=10,
        pady=10
    )

    delete_frame.pack(
        padx=50,
        pady=5,
        fill="x"
    )


    delete_menu.pack(
        in_=delete_frame,
        side="left",
        padx=15
    )


    def delete_product():

        product = delete_var.get()

        if not product:

            messagebox.showwarning(
                "Erreur",
                "Choisis un produit."
            )

            return


        answer = messagebox.askyesno(
            "Confirmation",
            f"واش متأكد بغيتي تحيد {product} ؟"
        )


        if not answer:
            return


        cursor.execute(
            "DELETE FROM menu WHERE name = ?",
            (product,)
        )

        db.commit()

        refresh_menu()


    tk.Button(
        delete_frame,
        text="🗑️ Supprimer",
        command=delete_product
    ).pack(
        side="left",
        padx=10
    )


    refresh_menu()


    tk.Button(
        window,
        text="⬅️ RETOUR DASHBOARD",
        font=("Arial", 14),
        command=patron_dashboard
    ).pack(pady=15)


# ============================================================
# CLOSE APPLICATION
# ============================================================

def close_application():

    global client_mode

    # --------------------------------------------------------
    # CLIENT CANNOT CLOSE WITHOUT PATRON CODE
    # --------------------------------------------------------

    if client_mode:

        code_window = tk.Toplevel(window)

        code_window.title(
            "Autorisation Patron"
        )

        code_window.geometry(
            "450x300"
        )

        code_window.resizable(
            False,
            False
        )

        code_window.grab_set()

        tk.Label(
            code_window,
            text="🔐 AUTORISATION PATRON",
            font=("Arial", 20, "bold")
        ).pack(pady=25)

        tk.Label(
            code_window,
            text="Code Patron obligatoire pour fermer.",
            font=("Arial", 13)
        ).pack()

        code_var = tk.StringVar()

        entry = tk.Entry(
            code_window,
            textvariable=code_var,
            show="*",
            font=("Arial", 18),
            width=16
        )

        entry.pack(pady=15)

        entry.focus()


        def verify_close():

            if code_var.get() == PATRON_CODE:

                client_mode = False

                code_window.grab_release()
                code_window.destroy()

                db.close()
                window.destroy()

            else:

                messagebox.showerror(
                    "Accès refusé",
                    "❌ Code Patron incorrect.",
                    parent=code_window
                )

                entry.delete(
                    0,
                    tk.END
                )


        tk.Button(
            code_window,
            text="🔓 FERMER APPLICATION",
            font=("Arial", 13, "bold"),
            command=verify_close
        ).pack(pady=10)

        return


    # --------------------------------------------------------
    # NORMAL CLOSE
    # --------------------------------------------------------

    db.close()
    window.destroy()


# ============================================================
# WINDOW CLOSE BUTTON
# ============================================================

window.protocol(
    "WM_DELETE_WINDOW",
    close_application
)


# ============================================================
# START APPLICATION
# ============================================================

home_page()

window.mainloop()