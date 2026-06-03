import flet as ft
import mysql.connector

# ==========================
# MYSQL CONNECTION
# ==========================

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Shariefd2002",
    database="tracking_db"
)

cursor = db.cursor()


def main(page: ft.Page):

    page.title = "Tracking System"
    page.window_width = 900
    page.window_height = 650
    page.scroll = "auto"

    selected_id = None

    # ==========================
    # INPUT FIELDS
    # ==========================

    item_name = ft.TextField(
        label="Item Name",
        width=250
    )

    status = ft.Dropdown(
        label="Status",
        width=200,
        options=[
            ft.dropdown.Option("Pending"),
            ft.dropdown.Option("In Progress"),
            ft.dropdown.Option("Completed")
        ]
    )

    category = ft.Dropdown(
        label="Category",
        width=200
    )

    search_box = ft.TextField(
        label="Search Item",
        width=250
    )

    # ==========================
    # TABLE
    # ==========================

    table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Item Name")),
            ft.DataColumn(ft.Text("Status")),
            ft.DataColumn(ft.Text("Category")),
            ft.DataColumn(ft.Text("Actions"))
        ],
        rows=[]
    )

    # ==========================
    # LOAD CATEGORIES
    # ==========================

    def load_categories():

        category.options.clear()

        cursor.execute(
            "SELECT category_id, category_name FROM categories"
        )

        records = cursor.fetchall()

        for row in records:
            category.options.append(
                ft.dropdown.Option(
                    key=str(row[0]),
                    text=row[1]
                )
            )

        page.update()

    # ==========================
    # LOAD DATA
    # ==========================

    def load_data(search=""):

        table.rows.clear()

        sql = """
        SELECT
            items.id,
            items.item_name,
            items.status,
            categories.category_name

        FROM items

        INNER JOIN categories
        ON items.category_id =
        categories.category_id
        """

        values = ()

        if search != "":
            sql += " WHERE items.item_name LIKE %s"
            values = (f"%{search}%",)

        cursor.execute(sql, values)

        records = cursor.fetchall()

        for row in records:

            edit_btn = ft.ElevatedButton(
                "Edit",
                on_click=lambda e, r=row:
                edit_item(r)
            )

            delete_btn = ft.ElevatedButton(
                "Delete",
                color="white",
                bgcolor="red",
                on_click=lambda e, item_id=row[0]:
                delete_item(item_id)
            )

            table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(
                            ft.Text(str(row[0]))
                        ),

                        ft.DataCell(
                            ft.Text(row[1])
                        ),

                        ft.DataCell(
                            ft.Text(row[2])
                        ),

                        ft.DataCell(
                            ft.Text(row[3])
                        ),

                        ft.DataCell(
                            ft.Row([
                                edit_btn,
                                delete_btn
                            ])
                        )
                    ]
                )
            )

        page.update()

    # ==========================
    # ADD ITEM
    # ==========================

    def add_item(e):

        if (
            item_name.value == ""
            or status.value is None
            or category.value is None
        ):
            return

        sql = """
        INSERT INTO items
        (item_name, status, category_id)

        VALUES (%s, %s, %s)
        """

        values = (
            item_name.value,
            status.value,
            category.value
        )

        cursor.execute(sql, values)
        db.commit()

        clear_fields()
        load_data()

    # ==========================
    # EDIT ITEM
    # ==========================

    def edit_item(row):

        nonlocal selected_id

        selected_id = row[0]

        item_name.value = row[1]
        status.value = row[2]

        cursor.execute("""
            SELECT category_id
            FROM categories
            WHERE category_name=%s
        """, (row[3],))

        result = cursor.fetchone()

        if result:
            category.value = str(result[0])

        page.update()

    # ==========================
    # UPDATE ITEM
    # ==========================

    def update_item(e):

        nonlocal selected_id

        if selected_id is None:
            return

        sql = """
        UPDATE items

        SET
        item_name=%s,
        status=%s,
        category_id=%s

        WHERE id=%s
        """

        values = (
            item_name.value,
            status.value,
            category.value,
            selected_id
        )

        cursor.execute(sql, values)
        db.commit()

        selected_id = None

        clear_fields()
        load_data()

    # ==========================
    # DELETE ITEM
    # ==========================

    def delete_item(item_id):

        cursor.execute(
            "DELETE FROM items WHERE id=%s",
            (item_id,)
        )

        db.commit()

        load_data()

    # ==========================
    # SEARCH
    # ==========================

    def search_item(e):

        load_data(search_box.value)

    # ==========================
    # CLEAR FIELDS
    # ==========================

    def clear_fields():

        item_name.value = ""
        status.value = None
        category.value = None

        page.update()

    # ==========================
    # BUTTONS
    # ==========================

    add_btn = ft.ElevatedButton(
        "Add Item",
        on_click=add_item
    )

    update_btn = ft.ElevatedButton(
        "Update Item",
        on_click=update_item
    )

    search_btn = ft.ElevatedButton(
        "Search",
        on_click=search_item
    )

    # ==========================
    # PAGE DESIGN
    # ==========================

    page.add(

        ft.Column(

            [

                ft.Text(
                    "TRACKING SYSTEM",
                    size=30,
                    weight="bold"
                ),

                ft.Divider(),

                item_name,

                status,

                category,

                ft.Row([
                    add_btn,
                    update_btn
                ]),

                ft.Divider(),

                ft.Row([
                    search_box,
                    search_btn
                ]),

                table

            ]

        )

    )

    load_categories()
    load_data()


ft.app(target=main)