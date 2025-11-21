import sys
import os
import psycopg2
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QIcon, QFont, QColor, QPalette
from PyQt5.QtCore import Qt
from sqlalchemy import create_engine, text
import pandas as pd
from datetime import datetime, timedelta

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

last_week = (datetime.today() - timedelta(days=7)).date()
yesterday = (datetime.today() - timedelta(days=1)).date()

# supervisorName = "Raseel alharthi"
login_id= "RAlharthi.c"#os.getlogin()

# ----------------------------
# Helper function for DB connection
# ----------------------------
def get_connection():
    return psycopg2.connect(**DB_SETTINGS)
    # return create_engine(f"postgresql://{DB_SETTINGS['user']}:{DB_SETTINGS["password"]}@{DB_SETTINGS["server"]}:{DB_SETTINGS["port"]}/{DB_SETTINGS["dbname"]}")

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
        self.resize(900, 600)

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

        # ----- Header Title -----
        header = QtWidgets.QLabel("🗂️ Team Evaluation System")
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
        self.start_date = QtWidgets.QDateEdit(QtCore.QDate.currentDate().addDays(-16))
        self.start_date.setCalendarPopup(True)
        sidebar_layout.addWidget(self.start_date)

        sidebar_layout.addWidget(QtWidgets.QLabel("To:"))
        self.end_date = QtWidgets.QDateEdit(QtCore.QDate.currentDate().addDays(-15))
        self.end_date.setCalendarPopup(True)
        sidebar_layout.addWidget(self.end_date)

        # Editor
        sidebar_layout.addWidget(QtWidgets.QLabel("Editor:"))
        self.editor_drop = QtWidgets.QComboBox()
        self.editor_drop.addItem("")
        query = f"""SELECT "Geo Supervisor", "Region", "GeoAction" FROM "GeoCompletion" 
                Where "GEO S Completion" BETWEEN '{self.start_date.date().toPyDate()}' AND '{self.end_date.date().toPyDate()}' 
                AND "SupervisorName"= '{supervisorName}' """
        conn = get_connection()
        self.editor_drop.addItems(pd.read_sql(query, conn)['Geo Supervisor'].unique().tolist())
        sidebar_layout.addWidget(self.editor_drop)

        # GeoAction
        sidebar_layout.addWidget(QtWidgets.QLabel("GeoAction:"))
        self.action_combo = QtWidgets.QComboBox()
        self.action_combo.addItem("")
        self.action_combo.addItems([i for i in pd.read_sql(query, conn)['GeoAction'].unique().tolist() if i not in ['', 'رفض']])
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

    def load_cases(self):
        supervisor = self.sup_input.text().strip()
        editor = self.editor_drop.currentText().strip()
        region = self.region_combo.currentText().strip()
        action = self.action_combo.currentText().strip()

        if not supervisor:
            QtWidgets.QMessageBox.warning(self, "Error", "Please enter Supervisor Name.")
            return

        conn = get_connection()
        days_back = 1
        max_days = 14

        result_df = pd.DataFrame()

        while days_back <= max_days:

            target_date = self.end_date.date().toPyDate() - timedelta(days=days_back)

            # -------- 1️⃣ Rejected case query ----------
            reject_query = """
                WITH rejected AS (
                    SELECT *,
                        ROW_NUMBER() OVER (
                            PARTITION BY "Geo Supervisor"
                            ORDER BY "GEO S Completion" DESC
                        ) AS rn
                    FROM "GeoCompletion"
                    WHERE "SupervisorName" = %s
                    AND "GEO S Completion" = %s
                    AND "GeoAction" = 'رفض'
                   -- AND "UniqueKey" NOT IN (SELECT "UniqueKey" FROM "EvaluationTable")
                )
                SELECT * FROM rejected WHERE rn = 1;
            """

            # -------- 2️⃣ Non-rejected case query ----------
            normal_query = """
                WITH accepted AS (
                    SELECT *,
                        ROW_NUMBER() OVER (
                            PARTITION BY "Geo Supervisor"
                            ORDER BY "GEO S Completion" DESC
                        ) AS rn
                    FROM "GeoCompletion"
                    WHERE "SupervisorName" = %s
                    AND "GEO S Completion" = %s
                    AND "GeoAction" != 'رفض'
                    --AND "UniqueKey" NOT IN (SELECT "UniqueKey" FROM "EvaluationTable")
                )
                SELECT * FROM accepted WHERE rn = 1;
            """

            reject_df = pd.read_sql(reject_query, conn, params=[supervisor, target_date])
            normal_df = pd.read_sql(normal_query, conn, params=[supervisor, target_date])

            combined = pd.concat([reject_df, normal_df], ignore_index=True)

            # -------- Optional Filters --------
            if editor:
                combined = combined[combined["Geo Supervisor"].str.contains(editor, case=False, na=False)]

            if region:
                combined = combined[combined["Region"].str.contains(region, case=False, na=False)]

            if action:
                combined = combined[combined["GeoAction"].str.contains(action, case=False, na=False)]

            # STOP when we have at least one case
            if not combined.empty:
                result_df = combined
                break

            days_back += 1

        conn.close()

        # Nothing at all found
        if result_df.empty:
            QtWidgets.QMessageBox.information(
                self, "Info", "No cases found for the past 14 days."
            )
            return

        # -------- Show message: how many days back searched --------
        QtWidgets.QMessageBox.information(
            self, "Search Result",
            f"Cases retrieved from {days_back} day(s) back (Date: {target_date})"
        )

        # -------- Warn if only 1 case for editor --------
        if len(result_df) == 1:
            editor_name = result_df.iloc[0]["Geo Supervisor"]
            QtWidgets.QMessageBox.warning(
                self,
                "Incomplete Assignment",
                f"Editor '{editor_name}' has only 1 valid case.\n"
                f"(Expected: 2 cases — Reject + Non-Reject)"
            )

        # Save final df
        self.cases_df = result_df.copy()

        # Format REN
        if "REN" in self.cases_df.columns:
            self.cases_df["REN"] = self.cases_df["REN"].astype(str).str[:16]

        # === Prepare fields for table ===
        self.preview_df = self.cases_df[
            [c for c in self.cases_df.columns
            if c in ["Case Number", "Geo Supervisor", "Geo Supervisor Recommendation",
                    "GEO S Completion", "GeoAction", "Region"]]
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
        self.start_date.setDate(QtCore.QDate.currentDate().addDays(-36))
        self.end_date.setDate(QtCore.QDate.currentDate().addDays(-30))

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
        self.resize(600, 400)
        # eval_title = QtWidgets.QLabel("📋Case Assessment")
        self.cases_df = cases_df
        self.index = row_index  # ✅ Fix: define index for navigation
        self.supervisor_name = supervisor_name

        self.setFont(QFont("Cairo", 10))
        self.setStyleSheet("""
            QGroupBox { font-weight: bold; color: #444; border: 1px solid #ccc; border-radius: 6px; margin-top: 8px; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; top: -4px; }
            QLabel { color: #333; }
            QPushButton {
                background-color: #BC9975; color: white;
                padding: 6px 12px; border-radius: 6px;
            }
            QPushButton:hover { background-color: #005a9e; }
        """)

        self.initUI()

    def initUI(self):
        main_layout = QtWidgets.QVBoxLayout(self)

        # Header + copy button layout
        header_layout = QtWidgets.QHBoxLayout()

        self.header = QtWidgets.QLabel(f"Case Evaluation - {self.cases_df.iloc[self.index]['Case Number']}")
        self.header.setAlignment(Qt.AlignCenter)
        self.header.setStyleSheet("font-size:14px; font-weight:bold; color:#824131; margin-bottom:6px;")
        header_layout.addWidget(self.header)

        # Copy Case Number button
        self.copy_FR = QtWidgets.QPushButton("Copy FR")
        self.copy_FR.setFixedWidth(80)
        self.copy_FR.setStyleSheet("""
            QPushButton {
                background-color: #824131;
                color: white;
                border-radius: 6px;
                padding: 4px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #a1503e; }
        """)
        self.copy_FR.clicked.connect(self.copy_case_number)
        header_layout.addWidget(self.copy_FR)

        # Copy REN button
        self.copy_btn_ren = QtWidgets.QPushButton("Copy REN")
        self.copy_btn_ren.setFixedWidth(80)
        self.copy_btn_ren.setStyleSheet("""
        #     QPushButton {
        #         background-color: #367580;
        #         color: white;
        #         border-radius: 6px;
        #         padding: 4px;
        #         font-weight: bold;
        #     }
        #     QPushButton:hover { background-color: #a1503e; }
        # """)
        self.copy_btn_ren.clicked.connect(self.copy_ren)
        header_layout.addWidget(self.copy_btn_ren)

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
            "Completion Date": "GEO S Completion",
            "Editor": "Geo Supervisor",
            "GeoAction": "GeoAction",
            "Supervisor": "SupervisorName",
            "Group ID": "GroupID",
        }
        # Case info fields
        case_fields = {
            "Case Number": case.get("Case Number", ""),
            "REN": case.get("REN", ""),
            "Completion Date": case.get("GEO S Completion", ""),
            "Editor": case.get("Geo Supervisor", ""),
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
        self.recommendation_text.setText(str(case.get("Geo Supervisor Recommendation", "")))

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
        fields = ["Procedure", "Topology", "Recommendation", "Completeness", "BlockAlignment"]

        for i, field in enumerate(fields):
            label = QtWidgets.QLabel(field + ":")
            dropdown = QtWidgets.QComboBox()
            dropdown.addItems([""] + options)
            dropdown.setFixedWidth(120)
            # dropdown.setContentsMargins(8,8,8,100)

            row = i // 2
            col = (i % 2) * 2

            eval_layout.addWidget(label, row, col)
            eval_layout.addWidget(dropdown, row, col + 1)
            self.eval_fields[field] = dropdown
        # self.eval_fields["EvaluationDate"] = datetime.now()

        main_layout.addWidget(eval_group)

        # --- Buttons in One Row ---
        btn_layout = QtWidgets.QHBoxLayout()
        # Button row (optional)
        btn_layout.setSpacing(15)
        self.prev_btn = QtWidgets.QPushButton("← Previous")
        self.prev_btn.setStyleSheet("""
            QPushButton {
                background-color: #BC9975;
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

        for col_name, label_widget in self.info_labels.items():
            label_widget.setText(str(case.get(col_name, "")))

        self.recommendation_text.setText(str(case.get("Geo Supervisor Recommendation", "")))

        for field in self.eval_fields:
            self.eval_fields[field].setCurrentIndex(0)
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
        values = [
            case["Case Number"],
            case.get("GEO S Completion", ""),
            case.get("Geo Supervisor", ""),
            case.get("Geo Supervisor Recommendation", ""),
            case.get("GeoAction", ""),
            self.supervisor_name,
            case.get("GroupID", ""),
        ]
        values += [self.eval_fields[field].currentText() for field in self.eval_fields]
        # values += [datetime.now()]

        conn = get_connection()
        evaluation = pd.DataFrame
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO "Evaluation"
                ("CaseNumber","CompletionDate", "EditorName", "EditorRecommendation", "GeoAction", "SupervisorName","GroupID",
                 "Procedure","Topology","Recommendation", "Completeness","BlockAlignment", "EvaluationDate")
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, values + [datetime.now()])
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
