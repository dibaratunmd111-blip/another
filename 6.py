import mysql.connector
import flet as ft
from datetime import datetime


db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Shariefd2002",
    database="tracking_bd"
)

cursor = db.cursor()



def main(page: ft.Page):
    page.title = "School Equipment Tracking System"
    page.window_width = 1000
    page.window_height = 700
    page.scroll = "auto"

    # =========================
    # INPUT FIELDS
    # =========================
    item_name = ft.TextField(label="Item Name")
    item_qty = ft.TextField(label="Quantity")

    borrower_name = ft.TextField(label="Borrower Name")

    borrow_item_id = ft.TextField(label="Item ID")
    borrow_borrower_id = ft.TextField(label="Borrower ID")

    output = ft.Column()

    # =========================
    # REFRESH DATA DISPLAY
    # =========================
    def refresh():
        output.controls.clear()

        # ITEMS
        cursor.execute("SELECT * FROM items")
        items = cursor.fetchall()

        output.controls.append(ft.Text("ITEMS", size=20, weight="bold"))
        for i in items:
            output.controls.append(
                ft.Text(f"ID:{i[0]} | Name:{i[1]} | Qty:{i[2]}")
            )

        # BORROWERS
        cursor.execute("SELECT * FROM borrowers")
        borrowers = cursor.fetchall()

        output.controls.append(ft.Text("\nBORROWERS", size=20, weight="bold"))
        for b in borrowers:
            output.controls.append(
                ft.Text(f"ID:{b[0]} | Name:{b[1]}")
            )

        # BORROW RECORDS
        cursor.execute("SELECT * FROM borrow_records")
        records = cursor.fetchall()

        output.controls.append(ft.Text("\nBORROW RECORDS", size=20, weight="bold"))
        for r in records:
            output.controls.append(
                ft.Text(
                    f"ID:{r[0]} | ItemID:{r[1]} | BorrowerID:{r[2]} | "
                    f"{r[3]} → {r[4]} | {r[5]}"
                )
            )

        page.update()

    # =========================
    # ITEM FUNCTIONS
    # =========================
    def add_item(e):
        cursor.execute(
            "INSERT INTO items(name, quantity) VALUES(%s, %s)",
            (item_name.value, item_qty.value)
        )
        db.commit()
        refresh()

    def delete_item(e):
        cursor.execute("DELETE FROM items WHERE id=%s", (item_name.value,))
        db.commit()
        refresh()

    # =========================
    # BORROWER FUNCTIONS
    # =========================
    def add_borrower(e):
        cursor.execute(
            "INSERT INTO borrowers(name) VALUES(%s)",
            (borrower_name.value,)
        )
        db.commit()
        refresh()

    def delete_borrower(e):
        cursor.execute("DELETE FROM borrowers WHERE id=%s", (borrower_name.value,))
        db.commit()
        refresh()

    # =========================
    # BORROW SYSTEM
    # =========================
    def borrow_item(e):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
            INSERT INTO borrow_records(item_id, borrower_id, borrow_date, return_date, status)
            VALUES(%s, %s, %s, %s, %s)
        """, (
            borrow_item_id.value,
            borrow_borrower_id.value,
            now,
            "",
            "BORROWED"
        ))

        db.commit()
        refresh()

    def return_item(e):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
            UPDATE borrow_records
            SET return_date=%s, status=%s
            WHERE item_id=%s AND status='BORROWED'
        """, (
            now,
            "RETURNED",
            borrow_item_id.value
        ))

        db.commit()
        refresh()

    # =========================
    # UI DESIGN
    # =========================
    page.add(
        ft.Text("School Equipment Tracking System", size=28, weight="bold"),
        ft.Divider(),

        ft.Text("ITEM MANAGEMENT", size=18, weight="bold"),
        item_name,
        item_qty,
        ft.Row([
            ft.ElevatedButton("Add Item", on_click=add_item),
            ft.ElevatedButton("Delete Item (by ID)", on_click=delete_item),
        ]),

        ft.Divider(),

        ft.Text("BORROWER MANAGEMENT", size=18, weight="bold"),
        borrower_name,
        ft.Row([
            ft.ElevatedButton("Add Borrower", on_click=add_borrower),
            ft.ElevatedButton("Delete Borrower (by ID)", on_click=delete_borrower),
        ]),

        ft.Divider(),

        ft.Text("BORROW SYSTEM", size=18, weight="bold"),
        borrow_item_id,
        borrow_borrower_id,
        ft.Row([
            ft.ElevatedButton("Borrow Item", on_click=borrow_item),
            ft.ElevatedButton("Return Item", on_click=return_item),
        ]),

        ft.Divider(),

        ft.ElevatedButton("Refresh Data", on_click=lambda e: refresh()),

        output
    )

    refresh()


ft.app(target=main)