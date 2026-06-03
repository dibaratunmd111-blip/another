import flet as ft
import mysql.connector

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


def main(page: ft.Page):

    page.title = "School Equipment Tracking System"
    page.window_width = 1000
    page.window_height = 700
    page.scroll = "auto"

    # =========================
    # SELECTED IDS
    # =========================
    selected_item = {"id": None}
    selected_borrower={"id": None}

    # =========================
    # INPUTS - ITEM
    # =========================
    item_name = ft.TextField(label="Item Name", width=200)

    item_status = ft.Dropdown(
        label="Status",
        width=200,
        options=[
            ft.dropdown.Option("Available"),
            ft.dropdown.Option("Borrowed"),
            ft.dropdown.Option("Maintenance")
        ]
    )

    category = ft.Dropdown(label="Category", width=200)

    # =========================
    # INPUTS - BORROWER
    # =========================
    borrower_name = ft.TextField(label="Borrower Name", width=200)

    course = ft.TextField(label="Course", width=200)

    borrow_item = ft.Dropdown(label="Item", width=200)

    # =========================
    # TABLES
    # =========================
    item_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Item")),
            ft.DataColumn(ft.Text("Status")),
            ft.DataColumn(ft.Text("Category")),
            ft.DataColumn(ft.Text("Actions"))
        ],
        rows=[]
    )

    borrower_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Borrower")),
            ft.DataColumn(ft.Text("Course")),
            ft.DataColumn(ft.Text("Item")),
            ft.DataColumn(ft.Text("Actions"))
        ],
        rows=[]
    )

    # =========================
    # LOAD CATEGORIES
    # =========================
    def load_categories():
        category.options.clear()

        cursor.execute("SELECT * FROM categories")

        for c in cursor.fetchall():
            category.options.append(
                ft.dropdown.Option(key=str(c[0]), text=c[1])
            )

        page.update()

    # =========================
    # LOAD ITEMS
    # =========================
    def load_items():
        item_table.rows.clear()
        borrow_item.options.clear()

        cursor.execute("""
            SELECT items.id, items.item_name, items.status, categories.category_name
            FROM items
            JOIN categories ON items.category_id = categories.category_id
        """)

        for row in cursor.fetchall():

            item_id = row[0]

            borrow_item.options.append(
                ft.dropdown.Option(key=str(row[0]), text=row[1])
            )

            edit_btn = ft.ElevatedButton(
                "Edit",
                bgcolor="blue",
                color="white",
                on_click=lambda e, r=row: edit_item(r)
            )

            delete_btn = ft.ElevatedButton(
                "Delete",
                bgcolor="red",
                color="white",
                on_click=lambda e, i=item_id: delete_item(i)
            )

            item_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(row[0]))),
                        ft.DataCell(ft.Text(row[1])),
                        ft.DataCell(ft.Text(row[2])),
                        ft.DataCell(ft.Text(row[3])),
                        ft.DataCell(ft.Row([edit_btn, delete_btn]))
                    ]
                )
            )

        page.update()

    # =========================
    # LOAD BORROWERS
    # =========================
    def load_borrowers():
        borrower_table.rows.clear()

        cursor.execute("""
            SELECT borrowers.borrower_id,
                   borrowers.borrower_name,
                   borrowers.course,
                   items.item_name
            FROM borrowers
            JOIN items ON borrowers.item_id = items.id
        """)

        for row in cursor.fetchall():

            borrower_id = row[0]

            edt_btn_brw = ft.ElevatedButton(
                                ("edit"),
                                bgcolor="blue",
                                color="white",
                                on_click=lambda e, r=row: edit_borrower(r)
                            )
            dlt_btn_brw = ft.ElevatedButton("delete",
                                bgcolor="blue",
                                color="white",
                                on_click=lambda e, i=borrower_id: delete_borrower(i)
                            )
# ft.IconButton(
                            #     icon=ft.Icons.DELETE,
                            #     icon_color="red",
                            #     on_click=lambda e, i=borrower_id: delete_borrower(i)
                            # )
            borrower_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(row[0]))),
                        ft.DataCell(ft.Text(row[1])),
                        ft.DataCell(ft.Text(row[2])),
                        ft.DataCell(ft.Text(row[3])),
                        ft.DataCell(ft.Row([edt_btn_brw, dlt_btn_brw]))
                    ]
                )
            )

        page.update()

    # =========================
    # ADD ITEM
    # =========================
    def add_item(e):

        cursor.execute("""
            INSERT INTO items(item_name, status, category_id)
            VALUES(%s, %s, %s)
        """, (
            item_name.value,
            item_status.value,
            category.value
        ))

        db.commit()

        clear_item_fields()
        load_items()

    # =========================
    # EDIT ITEM
    # =========================
    def edit_item(row):

        selected_item["id"] = row[0]

        item_name.value = row[1]
        item_status.value = row[2]

        cursor.execute("""
            SELECT category_id
            FROM categories
            WHERE category_name=%s
        """, (row[3],))

        result = cursor.fetchone()

        if result:
            category.value = str(result[0])

        page.update()

    # =========================
    # UPDATE ITEM
    # =========================
    def update_item(e):

        if selected_item["id"] is None:
            return

        cursor.execute("""
            UPDATE items
            SET item_name=%s,
                status=%s,
                category_id=%s
            WHERE id=%s
        """, (
            item_name.value,
            item_status.value,
            category.value,
            selected_item["id"]
        ))

        db.commit()

        selected_item["id"] = None

        clear_item_fields()
        load_items()

    # =========================
    # DELETE ITEM
    # =========================
    def delete_item(item_id):
        cursor.execute("DELETE FROM items WHERE id=%s", (item_id,))
        db.commit()
        load_items()

    # BORROW ITEM
   
    def borrow_item_action(e):

        cursor.execute("""
            INSERT INTO borrowers(borrower_name, course, item_id)
            VALUES(%s, %s, %s)
        """, (
            borrower_name.value,
            course.value,
            borrow_item.value
        ))

        db.commit()

        clear_borrow_fields()
        load_borrowers()

    def edit_borrower(row):

        selected_borrower["id"] = row[0]

        borrower_name.value = row[1]
        course.value = row[2]

        cursor.execute(
        "SELECT id FROM items WHERE item_name=%s",
        (row[3],))

        result = cursor.fetchone()

        if result:
            borrow_item.value =str (result[0])

        page.update()

    def update_borrower(e):

        if selected_borrower["id"] is None:
            return

        cursor.execute("""
            UPDATE borrowers
            SET borrower_name=%s,
                course=%s,
                item_id=%s
            WHERE id=%s
        """, (
            borrower_name.value,
            course.value,
            borrow_item.value,
            selected_borrower["id"]
        ))

        db.commit()

        selected_borrower["id"] = None

        clear_borrow_fields()
        load_borrowers()

    # =========================
    # DELETE BORROWER
    # =========================
    def delete_borrower(borrower_id):
        cursor.execute(
            "DELETE FROM borrowers WHERE borrower_id=%s",
            (borrower_id,)
        )
        db.commit()
        load_borrowers()

    # =========================
    # CLEAR FIELDS
    # =========================
    def clear_item_fields():
        item_name.value = ""
        item_status.value = None
        category.value = None
        page.update()

    def clear_borrow_fields():
        borrower_name.value = ""
        course.value = ""
        borrow_item.value = None
        page.update()

    # =========================
    # BUTTONS
    # =========================
    add_btn = ft.ElevatedButton("Add Item", bgcolor="blue", color = "white",on_click=add_item)
    update_btn = ft.ElevatedButton("Update Item",bgcolor="blue",color="white", on_click=update_item)

    borrow_btn = ft.ElevatedButton(
        "Borrow Item",
        bgcolor="green",
        color="white",
        on_click=borrow_item_action
    )

    update_borrow_btn = ft.ElevatedButton(
    "Update Borrower",
    bgcolor="green",
    color="white",
    on_click=update_borrower
    )

    # =========================
    # UI
    # =========================
    page.add(

        ft.Text("SCHOOL EQUIPMENT TRACKING SYSTEM", size=24, weight="bold"),

        ft.Divider(),

        ft.Text("ITEM MANAGEMENT", weight="bold"),

        ft.Row([item_name, item_status, category]),
        ft.Row([add_btn, update_btn]),

        ft.Divider(),

        item_table,

        ft.Divider(),

        ft.Text("BORROW MANAGEMENT", weight="bold"),

        ft.Row([borrower_name, course, borrow_item]),
        ft.Row([borrow_btn, update_borrow_btn]),

        borrower_table
    )

    # =========================
    # INITIAL LOAD
    # =========================
    load_categories()
    load_items()
    load_borrowers()


ft.app(target=main)