import sys
import os
import psycopg2
import random
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QIcon, QFont, QColor, QPalette, QPixmap
from PyQt5.QtCore import Qt
from sqlalchemy import create_engine, text
import pandas as pd
from datetime import date, datetime, timedelta

# ----------------------------
# Database connection settings
# ----------------------------
DB_SETTINGS = {
    # "server": "10.150.40.74",
    # "dbname": "GRS",
    "dbname": "GSA",
    "user": "postgres",
    "password": "1234",
    # "host": "10.150.40.74",
    "host": "localhost",
    "port": "5432"
}

parent_directory = os.curdir
print(parent_directory)

APP_ICON_PATH = r".\Assessment.png"
logo = r".\Logo_icon.ico"

last_week = (datetime.today() - timedelta(days=7)).date()
yesterday = (datetime.today() - timedelta(days=1)).date()

# supervisorName = "Raseel alharthi"
# login_id= os.getlogin()
sup_ids = ["malnmar.c", "fhaddadi.c", "obakri.c", "ralotaibi.c", "falmarshed.c", "RAlharthi.c"]
login_id = sup_ids[3]
# ----------------------------
# Helper function for DB connection
# ----------------------------
def get_connection():
    return psycopg2.connect(**DB_SETTINGS)
    # return create_engine(f"postgres ql://{DB_SETTINGS['user']}:{DB_SETTINGS["password"]}@{DB_SETTINGS["server"]}:{DB_SETTINGS["port"]}/{DB_SETTINGS["dbname"]}")

def retrive_supervisor(supervisor_id):
    conn = get_connection()
    query = """SELECT "SupervisorName" FROM "GeoCompletion" WHERE "SupervisorID"=%s"""
    cursor = conn.cursor()
    # cursor.execute("""SELECT "SupervisorName" FROM "GeoCompletion" WHERE "SupervisorID"=%s """, (supervisor_id,))
    # results = cursor.fetchall()
    name = str(pd.read_sql(query, conn, params=[supervisor_id])["SupervisorName"].unique().tolist()[0])
    # name = str(results["SupervisorName"].unique())
    return name

supervisorName = retrive_supervisor(login_id)

# ----------------------------
# Main Window: Case List
# ----------------------------
class MainWindow(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Evaluation System")
        self.setWindowIcon(QIcon(APP_ICON_PATH))
        self.resize(1000, 720)

        # 🌈 Apply light theme
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#E6EDF4"))
        palette.setColor(QPalette.Base, QColor("#ffffff"))
        palette.setColor(QPalette.AlternateBase, QColor("#f3f3f3"))
        palette.setColor(QPalette.Button, QColor("#0A3556"))
        palette.setColor(QPalette.ButtonText, QColor("#ffffff"))
        self.setPalette(palette)

        self.setFont(QFont("Cairo", 10))
        
        # Main horizontal layout
        # === Main vertical layout (top title + content area) ===
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # icon = QPixmap(logo).scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio)
        # ----- Header Title -----
        header = QtWidgets.QLabel("GRS - Team Evaluation System")
        # self.header.setText(f'<img src="./Logo_icon.ico" width="24" height="24"> GRS - Team Evaluation System')
        header.setFont(QFont("Cairo", 16, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("""
            QLabel {
                background-color: #0A3556;
                color: white;
                padding: 12px;
                border-bottom: 3px solid #005a9e;
            }
        """)
        # main_layout.addWidget(icon)
        main_layout.addWidget(header)

        # ----- Main Content Area (Sidebar + Table) -----
        content_layout = QtWidgets.QHBoxLayout()
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(10)

        # Sidebar
        sidebar = QtWidgets.QFrame()
        sidebar.setFixedWidth(200)
        sidebar.setStyleSheet("""
        #     QFrame {
        #         background-color: #E6EDF4;
        #         border: 2px solid #d0d0d0;
        #     }
        # """)

        # Sidebar layout
        sidebar_layout = QtWidgets.QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(15, 20, 15, 20)
        sidebar_layout.setSpacing(10)

        title = QtWidgets.QLabel("🧺 Filter Cases")
        title.setFont(QFont("Cairo", 13))
        title.setStyleSheet("color: #0A3556;")
        sidebar_layout.addWidget(title)

        # Supervisor
        sidebar_layout.addWidget(QtWidgets.QLabel("Supervisor:"))
        self.logged_supervisor = supervisorName  # replace 'current_user' with your variable

        self.sup_input = QtWidgets.QLineEdit(self.logged_supervisor)
        self.sup_input.setReadOnly(True)
        self.sup_input.setStyleSheet("""
            QLineEdit {
                background-color: #f0f0f0;
                color: #333333;
                font-weight: bold;
                border: 1px solid #cccccc;
                padding: 4px;
            }
        """)
        sidebar_layout.addWidget(self.sup_input)
        
        # Date range
        sidebar_layout.addWidget(QtWidgets.QLabel("From:"))
        self.start_date = QtWidgets.QDateEdit(QtCore.QDate.currentDate().addDays(-24))
        self.start_date.setCalendarPopup(True)
        sidebar_layout.addWidget(self.start_date)

        sidebar_layout.addWidget(QtWidgets.QLabel("To:"))
        self.end_date = QtWidgets.QDateEdit(QtCore.QDate.currentDate().addDays(-18))
        self.end_date.setCalendarPopup(True)
        sidebar_layout.addWidget(self.end_date)

        # Editor
        sidebar_layout.addWidget(QtWidgets.QLabel("Editor:"))
        self.editor_drop = QtWidgets.QComboBox()
        self.editor_drop.addItem("")
        query = f"""SELECT "EditorName", "Region", "GeoAction" FROM "CaseAssignment" 
                Where "CompletionDate" BETWEEN '{self.start_date.date().toPyDate()}' AND '{self.end_date.date().toPyDate()}' 
                AND "AssignedSupervisor" = '{supervisorName}' """
        conn = get_connection()
        self.editor_drop.addItems(pd.read_sql(query, conn)['EditorName'].unique().tolist())
        sidebar_layout.addWidget(self.editor_drop)

        # GeoAction
        sidebar_layout.addWidget(QtWidgets.QLabel("GeoAction:"))
        self.action_combo = QtWidgets.QComboBox()
        self.action_combo.addItem("")
        self.action_combo.addItems([i for i in pd.read_sql(query, conn)['GeoAction'].unique().tolist()])
        sidebar_layout.addWidget(self.action_combo)

        # Region
        sidebar_layout.addWidget(QtWidgets.QLabel("Region:"))
        self.region_combo = QtWidgets.QComboBox()
        self.region_combo.addItem("")
        self.region_combo.addItems(pd.read_sql(query, conn)['Region'].unique().tolist())
        sidebar_layout.addWidget(self.region_combo)

        # Buttons
        self.load_btn = QtWidgets.QPushButton("🔄 Load Cases")
        self.load_btn.setStyleSheet("""
            QPushButton {
                background-color: #0A3556;
                color: white;
                padding: 6px 12px;
                border-radius: 6px;
            }
            QPushButton:hover { background-color: #005a9e; }
        """)
        self.reset_btn = QtWidgets.QPushButton("🧹 Reset")
        self.reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #824131;
                color: white;
                padding: 8px;
                border-radius: 8px;
                font-weight: 600;
            }
            QPushButton:hover { background-color: #a1503e; }
        """)
        fil_btn_layout = QtWidgets.QHBoxLayout()
        # Button row (optional)
        fil_btn_layout.setSpacing(15)

        fil_btn_layout.addWidget(self.load_btn)
        fil_btn_layout.addWidget(self.reset_btn)
        sidebar_layout.addLayout(fil_btn_layout)
        sidebar_layout.addStretch()

        # ----- Main area -----
        main_area = QtWidgets.QWidget()
        main_vlayout = QtWidgets.QVBoxLayout(main_area)
        main_vlayout.setContentsMargins(10, 10, 10, 10)

        self.table = QtWidgets.QTableWidget()
        self.table.setSelectionBehavior(QtWidgets.QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QHeaderView::section {
                background-color: #0A3556;
                color: white;
                font-family: Cairo;
                font-weight: bold;
                padding: 4px;
            }
            QTableWidget {
                gridline-color: #dcdcdc;
                selection-background-color: #367580;
            }
        """)
        main_vlayout.addWidget(self.table)

        # Combine sidebar and table area
        content_layout.addWidget(sidebar)
        content_layout.addWidget(main_area)

        main_layout.addLayout(content_layout)
        self.setLayout(main_layout)


        # Events
        self.load_btn.clicked.connect(self.load_cases)
        self.reset_btn.clicked.connect(self.reset_filters)
        self.table.cellDoubleClicked.connect(self.open_evaluation)

        self.cases_df = pd.DataFrame()

    # --------------------------
    # On-demand assignment
    # --------------------------
    def generate_daily_assignment(self):
        max_days = 7
        day_back = 1
        found_cases = False
        engine = create_engine("postgresql://postgres:1234@localhost:5432/GSA")
        conn = get_connection()
        while day_back <= max_days:
            target_date = self.end_date.date().toPyDate() - timedelta(days=day_back)
            # Pull yesterday's cases
            sql = """
                SELECT *
                FROM "GeoCompletion"
                WHERE "GEO S Completion"::date = %s
                AND "GeoAction" IS NOT NULL
                AND "GroupID" IN ('Editor Morning shift  ', 'Editor Night Shift')
                AND "UniqueKey" NOT IN (
                    SELECT "UniqueKey" FROM "EvaluationTable"
                    UNION
                    SELECT "UniqueKey" FROM "CaseAssignment"
                )
            """
            df = pd.read_sql(sql, conn, params=[target_date])

            if not df.empty:
                found_cases = True
                break
            day_back += 1

        if not found_cases:
            QtWidgets.QMessageBox.warning(None, "No Cases", 
                f"No valid cases found in the past {max_days} days.")
            return None, day_back-1

        # Editors and Supervisors for assignment
        supervisors = [i for i in df["SupervisorName"].unique() if not pd.isnull(i)]
        excluded = ["Mahmoud Aboalmaged", "Moataz Ibrahim"] + [i for i in supervisors]
        editors = [i for i in df["Geo Supervisor"].unique() if not pd.isnull(i) and i not in excluded]
        random.shuffle(supervisors)

        assignments = []

        # Create a list of all dates to search, starting with target_date
        search_dates = [self.end_date.date().toPyDate() - timedelta(days=x) for x in range(1, max_days + 1)]
        dates_back = []
        for i, editor in enumerate(editors):
            # 1 — Get cases for this editor from the primary (target) date
            editor_cases = df[df["Geo Supervisor"] == editor]

            reject_case = editor_cases[editor_cases["GeoAction"] == 'رفض']
            edit_case = editor_cases[editor_cases["GeoAction"] != 'رفض']
            print(f"==================================================\n Initial Df Editor: {editor} | Date: {target_date}\n{len(reject_case)}, {len(edit_case)}")
            # 2 — If missing categories → search older dates
            if reject_case.empty or edit_case.empty:

                for d in search_dates[1:]:  # skip target_date already checked
                    print(f"==================================================\n Searching for cases on {d}")
                    if d not in dates_back:
                        dates_back.append(d)
                    sql_more = """
                        SELECT *
                        FROM "GeoCompletion"
                        WHERE "GEO S Completion"::date = %s
                        AND "GeoAction" IS NOT NULL
                        AND "GroupID" IN ('Editor Morning shift  ', 'Editor Night Shift')
                        AND "Geo Supervisor" = %s
                        AND "UniqueKey" NOT IN (
                                SELECT "UniqueKey" FROM "EvaluationTable"
                                UNION
                                SELECT "UniqueKey" FROM "CaseAssignment"
                        )
                    """

                    df_more = pd.read_sql(sql_more, conn, params=[d, editor])

                    if df_more.empty:
                        continue

                    # append additional rows
                    if reject_case.empty:
                        reject_case = df_more[df_more["GeoAction"] == "رفض"]
                        # reject_case = pd.concat([reject_case, df_more[df_more["GeoAction"] == "رفض"]])

                    if edit_case.empty:
                        edit_case = df_more[df_more["GeoAction"] != "رفض"]
                        # edit_case = pd.concat([edit_case, df_more[df_more["GeoAction"] != "رفض"]])
                    print(editor,":", len(reject_case), "/ ", len(edit_case))
                    # Stop searching if both categories found
                    if not reject_case.empty and not edit_case.empty:
                        break

            # 3 — Final selection  
            selected_rows = []

            if not reject_case.empty:
                selected_rows.append(reject_case.sample(1))

            if not edit_case.empty:
                selected_rows.append(edit_case.sample(1))

            # If editor has neither category even after searching 14 days → skip
            if not selected_rows:
                continue

            # 4 — Format & assign supervisor
            for row in selected_rows:
                row_dict = row.to_dict(orient="records")[0]
                row_dict['AssignedSupervisor'] = supervisors[i % len(supervisors)]
                row_dict['AssignmentDate'] = date.today()
                assignments.append(row_dict)
        if not assignments:
            QtWidgets.QMessageBox.warning(None, "No Assignments", 
                "No cases could be assigned today.")
            return None, day_back-1

        assign_df = pd.DataFrame(assignments)
        # Write to CaseAssignment
        assign_df = assign_df[["UniqueKey","Case Number", "REN", "GEO S Completion", "Geo Supervisor", "Geo Supervisor Recommendation", "SupervisorName", "GroupID", "GeoAction",
                   "Region", "AssignedSupervisor","AssignmentDate"]]
        assign_df = assign_df.rename({"GEO S Completion":"CompletionDate", "Geo Supervisor":"EditorName", 
                                      "Geo Supervisor Recommendation":"EditorRecommendation"}, axis=1)
        assign_df[["UniqueKey","Case Number", "REN", "CompletionDate", "EditorName", "EditorRecommendation", "SupervisorName", "GroupID", "GeoAction",
                   "Region", "AssignedSupervisor","AssignmentDate"]].to_sql("CaseAssignment", engine, if_exists="append", index=False
        )
        days_searched = target_date - min(dates_back) if dates_back else timedelta(0)
        return assign_df, day_back, days_searched.days

    # --------------------------
    # Load supervisor cases
    # --------------------------
    def load_supervisor_assignment(self, supervisor_name):
        editor = self.editor_drop.currentText().strip()
        region = self.region_combo.currentText().strip()
        action = self.action_combo.currentText().strip()
        conn = get_connection()
        sql = """
            SELECT *
            FROM "CaseAssignment"
            WHERE "AssignedSupervisor" = %s
            AND "IsEvaluated" = FALSE
        """
        if editor:
            sql += f"""AND "EditorName" = '{editor}' """
        if action:
            sql += f"""AND "GeoAction" = '{action}' """
        if region:
            sql += f"""AND "Region" = '{region}' """

        sql += 'ORDER BY "EditorName" '
        df = pd.read_sql(sql, conn, params=[supervisor_name])
        return df

    # --------------------------
    # Usage example in PyQt MainWindow
    # --------------------------
    def load_cases(self):
        supervisor = self.sup_input.text().strip()
        if not supervisor:
            QtWidgets.QMessageBox.warning(self, "Error", "Please enter Supervisor Name.")
            return

        conn = get_connection()

        # Check if assignments exist
        check_sql = """
            SELECT COUNT(*) FROM "CaseAssignment"
            WHERE "AssignmentDate" = CURRENT_DATE
        """
        count = pd.read_sql(check_sql, conn).iloc[0,0]

        if count == 0:
            assigned_df, days_back, days_searched = self.generate_daily_assignment()
            if assigned_df is None:
                return
            QtWidgets.QMessageBox.information(self, "Assignments Generated",
                f"Assignments generated from {days_searched} day(s) back.")
        
        # Load supervisor's cases
        self.cases_df = self.load_supervisor_assignment(supervisor)
        # Format REN
        if "REN" in self.cases_df.columns:
            self.cases_df["REN"] = self.cases_df["REN"].astype(str).str[:16]

        # === Prepare fields for table ===
        self.preview_df = self.cases_df[
            [c for c in self.cases_df.columns
            if c in ["Case Number", "REN", "CompletionDate", "EditorName", "SupervisorName", "EditorRecommendation",
                    "GeoAction", "Region", "IsEvaluated"]]
        ]

        self.table.setRowCount(len(self.preview_df))
        self.table.setColumnCount(len(self.preview_df.columns))
        self.table.setHorizontalHeaderLabels(self.preview_df.columns)

        # === Color Rules ===
        for r in range(len(self.preview_df)):
            for c in range(len(self.preview_df.columns)):
                val = str(self.preview_df.iat[r, c])
                item = QtWidgets.QTableWidgetItem(val)
                item.setFlags(item.flags() ^ Qt.ItemIsEditable)

                # Row Coloring based on Evaluation Status
                if self.preview_df.iloc[r]["IsEvaluated"]:
                    item.setBackground(QColor("#A1A1A1"))  # gray for evaluated
                    item.setFlags(Qt.NoItemFlags)
                else:
                    # Row coloring based on GeoAction
                    geo_action = str(self.preview_df.iloc[r]["GeoAction"])
                    if geo_action == "رفض":
                        item.setBackground(QColor("#ffb3b3"))  # Light red
                    else:
                        item.setBackground(QColor("#c2f0c2"))  # Light green

                self.table.setItem(r, c, item)

    def reset_filters(self):
        """Reset all filters to default state."""
        # self.sup_input.clear()
        self.editor_drop.clear()
        self.action_combo.setCurrentIndex(0)
        self.region_combo.setCurrentIndex(0)
        self.start_date.setDate(QtCore.QDate.currentDate().addDays(-24))
        self.end_date.setDate(QtCore.QDate.currentDate().addDays(-17))

    def open_evaluation(self, row, column):
        if self.cases_df.empty:
            return
        eval_window = EvaluationWindow(self.cases_df, row, self.sup_input.text().strip())
        eval_window.exec_()


# ----------------------------
# Evaluation Window
# ----------------------------
class EvaluationWindow(QtWidgets.QDialog):
    def __init__(self, cases_df, row_index, supervisor_name):
        super().__init__()
        self.setWindowTitle("Case Evalution")
        self.setWindowIcon(QIcon(APP_ICON_PATH))
        self.resize(650, 450)
        # eval_title = QtWidgets.QLabel("📋Case Assessment")
        self.cases_df = cases_df
        self.index = row_index  # ✅ Fix: define index for navigation
        self.supervisor_name = supervisor_name

        self.setFont(QFont("Cairo", 11))
        self.setStyleSheet("""
            QGroupBox { font-weight: bold; color: #444; border: 1px solid #ccc; border-radius: 6px; margin-top: 8px; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; top: -4px; }
            QLabel { color: #333; }
            QPushButton {
                background-color: #0A3556; color: white;
                padding: 6px 12px; border-radius: 6px;
            }
            QPushButton:hover { background-color: #005a9e; }
        """)

        self.initUI()

    def initUI(self):
        main_layout = QtWidgets.QVBoxLayout(self)

        # Header + copy button layout
        header_layout = QtWidgets.QHBoxLayout()
        buttons_layout = QtWidgets.QVBoxLayout()
        left_layout = QtWidgets.QVBoxLayout()
        header_layout.addLayout(left_layout)
        # Copy Case Number button
        self.copy_FR = QtWidgets.QPushButton("Copy FR")
        self.copy_FR.setFixedWidth(80)
        self.copy_FR.setStyleSheet("""
            QPushButton {
                # background-color: #367580;
                color: white;
                border-radius: 6px;
                padding: 4px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #a1503e; }
        """)
        self.copy_FR.clicked.connect(self.copy_case_number)
        buttons_layout.addWidget(self.copy_FR)

        self.header = QtWidgets.QLabel(f"Case Evaluation - {self.cases_df.iloc[self.index]['Case Number']}")
        self.header.setAlignment(Qt.AlignCenter)
        self.header.setStyleSheet("font-size:16px; font-weight:bold; color:#0A3556; margin-bottom:6px;")
        header_layout.addWidget(self.header)

        # Copy REN button
        self.copy_btn_ren = QtWidgets.QPushButton("Copy REN")
        self.copy_btn_ren.setFixedWidth(80)
        self.copy_btn_ren.setStyleSheet("""
            QPushButton {
                background-color: #367580;
                color: white;
                border-radius: 6px;
                padding: 4px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #a1503e; }
        """)
        self.copy_btn_ren.clicked.connect(self.copy_ren)
        buttons_layout.addWidget(self.copy_btn_ren)

        header_layout.addLayout(buttons_layout)
        main_layout.addLayout(header_layout)
        
        # --- Case Info Section ---
        info_group = QtWidgets.QGroupBox("Case Information")
        info_layout = QtWidgets.QGridLayout(info_group)
        info_layout.setContentsMargins(5, 5, 5, 10)
        info_layout.setHorizontalSpacing(20)
        info_layout.setVerticalSpacing(2)

        # Prevent columns from stretching equally
        info_layout.setColumnStretch(0, 0)  # label column 1
        info_layout.setColumnStretch(1, 1)  # value column 1
        info_layout.setColumnStretch(2, 0)  # label column 2
        info_layout.setColumnStretch(3, 1)  # value column 2

        case = self.cases_df.iloc[self.index]
        self.case_field_map = {
            "Case Number": "Case Number",
            "REN": "REN",
            "Completion Date": "CompletionDate",
            "EditorName": "EditorName",
            "GeoAction": "GeoAction",
            "Supervisor": "SupervisorName",
            "Group ID": "GroupID",
        }
        # Case info fields
        case_fields = {
            "Case Number": case.get("Case Number", ""),
            "REN": case.get("REN", ""),
            "Completion Date": case.get("CompletionDate", ""),
            "Editor Name": case.get("EditorName", ""),
            "GeoAction": case.get("GeoAction", ""),
            "Supervisor": case.get("SupervisorName", ""),
            "Group ID": case.get("GroupID", ""),
        }

        # ✅ Store info labels for updates  
        self.info_labels = {}
        for i, (display, col_name) in enumerate(self.case_field_map.items()):
            lbl_title = QtWidgets.QLabel(f"<b>{display}:</b>")
            lbl_value = QtWidgets.QLabel(str(case.get(col_name, "")))
            self.info_labels[col_name] = lbl_value
            info_layout.addWidget(lbl_title, i // 2, (i % 2) * 2)
            info_layout.addWidget(lbl_value, i // 2, (i % 2) * 2 + 1)

        # --- Editor Recommendation (smaller, 2–3 lines) ---
        rec_label = QtWidgets.QLabel("<b>Editor Recommendation:</b>")
        self.recommendation_text = QtWidgets.QTextEdit()
        self.recommendation_text.setReadOnly(True)
        self.recommendation_text.setMaximumHeight(60)  # ✅ smaller box
        self.recommendation_text.setText(str(case.get("EditorRecommendation", "")))

        info_layout.addWidget(rec_label, (len(case_fields) // 2) + 1, 0, 1, 2)
        info_layout.addWidget(self.recommendation_text, (len(case_fields) // 2) + 2, 0, 1, 4)

        main_layout.addWidget(info_group)
        main_layout.addSpacing(15)

        # --- Evaluation Fields ---
        eval_group = QtWidgets.QGroupBox("Evaluation Fields")
        eval_layout = QtWidgets.QGridLayout(eval_group)
        eval_layout.setHorizontalSpacing(5)  # ✅ tighter horizontal space
        eval_layout.setVerticalSpacing(4)     # ✅ less vertical space
        eval_layout.setContentsMargins(8,8,8,8)
        self.eval_fields = {}

        options = ["Yes", "No"]
        fields = ["Procedure", "Recommendation", "Topology", "Completeness", "BlockAlignment"]
        technical_fields = ["Topology", "Completeness", "BlockAlignment"]
        weights = [0.7, 0.3, 0.35, 0.4,0.25]
              
        for i, field in enumerate(fields):
            label = QtWidgets.QLabel(field + ":")
            dropdown = QtWidgets.QComboBox()
            if case['GeoAction'] == 'رفض' and field in technical_fields:
                dropdown.addItems([None])
            else:
                dropdown.addItems([""]+options)
            dropdown.setFixedWidth(120)
            # dropdown.setContentsMargins(8,8,8,100)

            row = i // 2
            col = (i % 2) * 2

            eval_layout.addWidget(label, row, col)
            eval_layout.addWidget(dropdown, row, col + 1)
            self.eval_fields[field] = dropdown
            
            
        # print(self.eval_fields)
        

        main_layout.addWidget(eval_group)

        # --- Buttons in One Row ---
        btn_layout = QtWidgets.QHBoxLayout()
        # Button row (optional)
        btn_layout.setSpacing(20)
        self.prev_btn = QtWidgets.QPushButton("← Previous")
        self.prev_btn.setStyleSheet("""
            QPushButton {
                background-color: #824131;
                color: white;
                padding: 8px;
                border-radius: 8px;
                font-weight: 600;
            }
        """)
        self.prev_btn.clicked.connect(self.prev_case)
        self.next_btn = QtWidgets.QPushButton("Next →")
        self.next_btn.setStyleSheet("""
            QPushButton {
                background-color: #BC9975;
                color: white;
                padding: 8px;
                border-radius: 8px;
                font-weight: 600;
            }
        """)
        self.next_btn.clicked.connect(self.next_case)

        self.submit_btn = QtWidgets.QPushButton("Submit Evaluation")
        self.submit_btn.setStyleSheet("""
            QPushButton {
                background-color: #0A3556;
                color: white;
                padding: 8px;
                border-radius: 8px;
                font-weight: 600;
            }
        """)
        self.submit_btn.clicked.connect(self.submit_evaluation)

        btn_layout.addWidget(self.prev_btn)
        btn_layout.addWidget(self.next_btn)
        # btn_layout.addStretch()
        btn_layout.addWidget(self.submit_btn)

        main_layout.addLayout(btn_layout)

    # --- Navigation Functions ---
    def prev_case(self):
        if self.index > 0:
            self.index -= 1
            self.load_case()

    def next_case(self):
        if self.index < len(self.cases_df) - 1:
            self.index += 1
            self.load_case()

    def load_case(self):
        case = self.cases_df.iloc[self.index]

        # Update header
        self.header.setText(f"Case Evaluation - {case['Case Number']}")
        if case.get("IsEvaluated", False):
            self.header.setStyleSheet("font-size:14px; font-weight:bold; color:#824131; margin-bottom:6px;")
        else:
            self.header.setStyleSheet("font-size:14px; font-weight:bold; color:#0A3556; margin-bottom:6px;")


        # Update info labels
        for col_name, label_widget in self.info_labels.items():
            label_widget.setText(str(case.get(col_name, "")))

        # Update recommendation
        self.recommendation_text.setText(str(case.get("EditorRecommendation", "")))

        # --- Update evaluation fields ---
        options = ["Yes", "No"]
        technical_fields = ["Topology", "Completeness", "BlockAlignment"]
        fields = ["Procedure", "Recommendation", "Topology", "Completeness", "BlockAlignment"]

        for field in fields:
            dropdown = self.eval_fields[field]
            if isinstance(dropdown, QtWidgets.QComboBox):
                if case["IsEvaluated"]:
                    dropdown.setCurrentIndex(0)        # Reset to empty
                    dropdown.setEnabled(False)         # Disable editing
                else:
                    dropdown.setCurrentIndex(0)        # Reset to empty
                    dropdown.setEnabled(True)          # Enable editing
                    # Clear previous items
                    dropdown.clear()

                    # Repopulate based on GeoAction
                    if case['GeoAction'] == 'رفض' and field in technical_fields:
                        dropdown.addItem("")  # only allow empty
                    else:
                        dropdown.addItems([""] + options)
            
            # # Optional: show a message if the case is already evaluated
            # if case["IsEvaluated"]:
            #     QtWidgets.QMessageBox.information(self, "Info", 
            #         f"Case {case['Case Number']} has already been evaluated.")
            # Reset selection
            dropdown.setCurrentIndex(0)    

    def copy_case_number(self):
        """Copy the current case number to clipboard."""
        case_number = self.cases_df.iloc[self.index]['Case Number']
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(str(case_number))
        QtWidgets.QMessageBox.information(self, "Copied", f"Case Number '{case_number}' copied to clipboard!")
    
    def copy_ren(self):
        """Copy the current REN to clipboard."""
        ren = self.cases_df.iloc[self.index]['REN']
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(str(ren))
        QtWidgets.QMessageBox.information(self, "Copied", f"Case Number '{ren}' copied to clipboard!")

    # --- Submit Evaluation ---
    def submit_evaluation(self):
        case = self.cases_df.iloc[self.index]

        # 1️⃣ Extract dropdown choices
        procedure     = self.eval_fields["Procedure"].currentText()
        recommendation = self.eval_fields["Recommendation"].currentText()
        topology      = self.eval_fields["Topology"].currentText()
        completeness  = self.eval_fields["Completeness"].currentText()
        blockalign    = self.eval_fields["BlockAlignment"].currentText()

        # 2️⃣ Compute numeric scores
        def score(value, weight):
            return weight if value == "Yes" else 0

        procedure_score       = score(procedure, 0.7)
        recommendation_score  = score(recommendation, 0.3)
        
        # Handling invalid submissions
        field_dict = {"Procedure": procedure, "Recommendation": recommendation, "Topology": topology, 
                      "Completeness": completeness, "BlockAlignment": blockalign} 
        
        # Technical fields only counted if GeoAction != "رفض"
        if case["GeoAction"] == "رفض":
            check = ["Procedure", "Recommendation"]
            null_fields = [i for i in check if field_dict[i] == ""]
            if len(null_fields)>0:
                message = ', '.join([i for i in null_fields])
                QtWidgets.QMessageBox.warning(self, "Incomplete Evaluation", 
                    f"Please complete all required fields before submitting. Missing input for {message}.")
                return
            topology_score = completeness_score = blockalign_score = None
        else:
            null_fields = [i for i in field_dict.keys() if field_dict[i] == ""]
            if len(null_fields) >0:
                message = ', '.join([i for i in null_fields])
                QtWidgets.QMessageBox.warning(self, "Incomplete Evaluation", 
                    f"Please complete all required fields before submitting. Missing input for {message}.")
                return
            topology_score     = score(topology, 0.35)
            completeness_score = score(completeness, 0.4)
            blockalign_score   = score(blockalign, 0.25)

        # 3️⃣ Aggregated scores
        procedural_accuracy = procedure_score + recommendation_score

        if case["GeoAction"] == "رفض":
            technical_accuracy = None
        else:
            technical_accuracy = (
                topology_score + completeness_score + blockalign_score
            )

        # 4️⃣ Build VALUES list in correct order
        values = [
            case["UniqueKey"],
            case["Case Number"],
            case.get("CompletionDate", None),
            case.get("EditorRecommendation", None),
            case.get("EditorName", None),
            case.get("SupervisorName", None),
            case.get("GroupID", None),
            case.get("GeoAction", None),
            procedure, procedure_score, recommendation, recommendation_score, topology, topology_score, completeness,
            completeness_score, blockalign, blockalign_score, procedural_accuracy, technical_accuracy, self.supervisor_name, datetime.now().replace(microsecond=0)]

        # 5️⃣ Insert into database
        conn = get_connection()
        evaluatedCases = pd.read_sql("""SELECT "UniqueKey" FROM "EvaluationTable" """, conn)
        
        if case['UniqueKey'] in evaluatedCases["UniqueKey"].values:
            QtWidgets.QMessageBox.warning(self, "Duplicated Entry", f"Case {case['Case Number']} has already been evaluated.")
        
        else:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO "EvaluationTable"
                    ("UniqueKey","Case Number","CompletionDate","EditorRecommendation", "EditorName","SupervisorName","GroupID","GeoAction",
                    "Procedure","ProcedureScore","Recommendation","RecommendationScore", "Topology","TopologyScore","Completeness","CompletenessScore",
                    "BlockAlignment","BlockAlignmentScore","ProceduralAccuracy", "TechnicalAccuracy","EvaluatedBy","EvaluationDate")
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                            %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """, values)
                conn.commit()
            # Update EvaluationStatus On Assignment Table
            update_sql = """
                UPDATE "CaseAssignment"
                SET "IsEvaluated" = TRUE
                WHERE "UniqueKey" = %s
                AND "AssignedSupervisor" = %s
            """
            with conn.cursor() as cur:
                cur.execute(update_sql, (case["UniqueKey"], self.supervisor_name))
                conn.commit()

            


            conn.close()
            QtWidgets.QMessageBox.information(self, "Success", "Evaluation submitted!")



# ----------------------------
# Main
# ----------------------------
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
