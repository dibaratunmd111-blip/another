import flet as ft
import mysql.connector
from datetime import datetime

# =========================
# DATABASE CONNECTION
# =========================
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Shariefd2002",
    database="tracking_db"
)

cursor = db.cursor()

# =========================
# MAIN APP
# =========================
def main(page: ft.Page):
    page.title = "School Equipment Tracking System"
    page.window_width = 1100
    page.window_height = 700
    page.scroll = "auto"

    # =========================
    # INPUT FIELDS
    # =========================
    item_name = ft.TextField(label="Item Name")
    item_qty = ft.TextField(label="Quantity", keyboard_type=ft.KeyboardType.NUMBER)

    borrower_name = ft.TextField(label="Borrower Name")
    borrower_course = ft.TextField(label="Course")

    # =========================
    # TABLES
    # =========================
    item_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Name")),
            ft.DataColumn(ft.Text("Qty")),
        ],
        rows=[]
    )

    borrower_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Name")),
            ft.DataColumn(ft.Text("Course")),
        ],
        rows=[]
    )

    borrow_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Item")),
            ft.DataColumn(ft.Text("Borrower")),
            ft.DataColumn(ft.Text("Borrow Date")),
            ft.DataColumn(ft.Text("Return Date")),
            ft.DataColumn(ft.Text("Penalty")),
            ft.DataColumn(ft.Text("Status")),
        ],
        rows=[]
    )

    # =========================
    # LOAD FUNCTIONS
    # =========================
    def load_items():
        cursor.execute("SELECT * FROM items")
        rows = cursor.fetchall()

        item_table.rows.clear()
        for r in rows:
            item_table.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(r[0])),
                    ft.DataCell(ft.Text(r[1])),
                    ft.DataCell(ft.Text(r[2])),
                ])
            )
        page.update()

    def load_borrowers():
        cursor.execute("SELECT * FROM borrowers")
        rows = cursor.fetchall()

        borrower_table.rows.clear()
        for r in rows:
            borrower_table.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(r[0])),
                    ft.DataCell(ft.Text(r[1])),
                    ft.DataCell(ft.Text(r[2])),
                ])
            )
        page.update()

    def load_borrowings():
        cursor.execute("""
            SELECT b.id, i.name, br.name, b.borrow_date, b.return_date, b.penalty, b.status
            FROM borrowings b
            JOIN items i ON b.item_id = i.id
            JOIN borrowers br ON b.borrower_id = br.id
        """)
        rows = cursor.fetchall()

        borrow_table.rows.clear()
        for r in rows:
            borrow_table.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(r[0])),
                    ft.DataCell(ft.Text(r[1])),
                    ft.DataCell(ft.Text(r[2])),
                    ft.DataCell(ft.Text(str(r[3]))),
                    ft.DataCell(ft.Text(str(r[4]))),
                    ft.DataCell(ft.Text(str(r[5]))),
                    ft.DataCell(ft.Text(r[6])),
                ])
            )
        page.update()

    # =========================
    # CRUD FUNCTIONS
    # =========================
    def add_item(e):
        cursor.execute(
            "INSERT INTO items (name, quantity) VALUES (%s, %s)",
            (item_name.value, item_qty.value)
        )
        db.commit()
        load_items()

    def add_borrower(e):
        cursor.execute(
            "INSERT INTO borrowers (name, course) VALUES (%s, %s)",
            (borrower_name.value, borrower_course.value)
        )
        db.commit()
        load_borrowers()

    def borrow_item(e):
        cursor.execute(
            "INSERT INTO borrowings (item_id, borrower_id, borrow_date, return_date, penalty, status) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (1, 1, datetime.now().date(), None, 0.00, "Borrowed")
        )
        db.commit()
        load_borrowings()

    # =========================
    # UI LAYOUT
    # =========================
    page.add(
        ft.Text("📦 School Equipment Tracking System", size=22, weight="bold"),

        ft.Divider(),

        ft.Text("📌 ITEMS"),
        ft.Row([
            item_name,
            item_qty,
            ft.ElevatedButton("Add Item", on_click=add_item),
        ]),
        item_table,

        ft.Divider(),

        ft.Text("👤 BORROWERS"),
        ft.Row([
            borrower_name,
            borrower_course,
            ft.ElevatedButton("Add Borrower", on_click=add_borrower),
        ]),
        borrower_table,

        ft.Divider(),

        ft.Text("📋 BORROWING RECORDS"),
        ft.ElevatedButton("Refresh Borrowings", on_click=lambda e: load_borrowings()),
        borrow_table,
    )

    # =========================
    # INITIAL LOAD
    # =========================
    load_items()
    load_borrowers()
    load_borrowings()


ft.app(target=main)