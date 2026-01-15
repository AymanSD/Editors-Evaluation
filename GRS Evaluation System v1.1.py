import sys
import os
import psycopg2
import random
import openpyxl
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtGui import QIcon, QFont, QColor, QPalette, QPixmap
from PyQt5.QtCore import Qt
from sqlalchemy import create_engine, text
import pandas as pd
from datetime import date, datetime, timedelta

# ----------------------------
# Database connection settings
# ----------------------------
DB_SETTINGS = {
    # "dbname": "GSA",
    "dbname": "GRS",
    "user": "evalApp",
    "password": "app1234",
    "host": "10.150.40.74",
    # "host":"127.0.0.1",
    "port": "5432"
}

APP_ICON_PATH = os.path.dirname(os.path.abspath(__file__)) + r"\Assessment.ico"
logo_path = os.path.dirname(os.path.abspath(__file__)) + r"\LogoFull.png"
if not os.path.exists(APP_ICON_PATH):
    APP_ICON_PATH = r"\\10.150.40.49\las\Ayman\Tools & Apps\Data For Tools\Icons\Assessment.ico"

if os.path.exists(logo_path):
    logo_path = r"\\10.150.40.49\las\Ayman\Tools & Apps\Data For Tools\Icons\LogoFull.png"

last_week = (datetime.today() - timedelta(days=7)).date()
yesterday = (datetime.today() - timedelta(days=1)).date()

# supervisorName = "Raseel alharthi"
login_id= os.getlogin().lower().strip()
# admin_users = [i.lower().strip() for i in ["Aaltoum", "MIbrahim.c", "aalhares.c", "LMohammed.c",  "AMagboul.c", "telwahab.c", "nalsuhaimi.c"]]
excluded_supervisors = ["Mohammed Mustafa Al-Daly", "Musab Hassan"]
sup_ids = ['MMohammed.c', 'MBarakat.c', 'AElFadil.c', 'MFadil.c', 'falmarshed.c', 'ralotaibi.c', 'mmohammedKhir.c', 'malnmar.c', 'RAlharthi.c', 'SAlfuraihi.c', 'obakri.c', 'fhaddadi.c']
# login_id = sup_ids[10].lower().strip()
# login_id = admin_users[6].lower().strip()
# login_id =  "MAlsheikh.c".lower().strip()
# ----------------------------
# Helper function for DB connection
# ----------------------------
def get_connection():
    return psycopg2.connect(**DB_SETTINGS)
    # return create_engine(f"postgres ql://{DB_SETTINGS['user']}:{DB_SETTINGS["password"]}@{DB_SETTINGS["server"]}:{DB_SETTINGS["port"]}/{DB_SETTINGS["dbname"]}")

def get_admins_upadtes():
    conn = get_connection()
    try:
        query = """SELECT DISTINCT("UserID") FROM evaluation."EditorsList" 
                WHERE "GroupID" IN ('COORDINATOR', 'Developers', 'TEAMLEADER', 'TRANING') 
                AND "UserID" IS NOT NULL"""
        df = pd.read_sql(query, conn)
        admins = [str(u).lower().strip() for u in df["UserID"].unique().tolist()]
        # print(">>",admins)
        return admins
    finally:
        conn.close()

def retrive_supervisor(supervisor_id):
    conn = get_connection()
    query = """SELECT DISTINCT("CasePortalName"), "UserID" FROM evaluation."EditorsList" WHERE LOWER("UserID") = LOWER(%s)"""
    # if supervisor_id in admin_users:
    #     return "Admin User"
    # else:
    df = pd.read_sql(query, conn, params=[supervisor_id])
    
    if df.empty:
        return None
    name = str(df["CasePortalName"].iloc[0]).strip()
    print("==+==",name, supervisor_id)
    if supervisor_id in admin_users:
        return name+" 🔓"
    else:
        return name
    # name = str(results["SupervisorName"].unique())

def get_ids(name):
    conn = get_connection()
    query = """SELECT DISTINCT("UserID") FROM evaluation."EditorsList" WHERE "CasePortalName" = %s """
    try:
        id = pd.read_sql(query, conn, params=[str(name)])
        if id.empty:
            print(query)
            print(f"No Matches were found for {name}, {len(name)} ")
            return None
        print("===============\n",str(id["UserID"].tolist()[0]))
        return str(id["UserID"].tolist()[0])
    finally:
        conn.close()

def is_allowed_user(login_id):
    conn = get_connection()
    query = """SELECT DISTINCT("SupervisorID") FROM evaluation."EditorsList" 
            WHERE "GroupID" IN ('Editor Morning Shift', 'Editor Night Shift', 'Pod-Al-Shuhada-1', 'Pod-Al-Shuhada-2', 'Urgent Team')
            """
    # max_days = 7
    # current_date = datetime.now().date() -timedelta(days=1)
    # for day in range(1, 7):
    users = pd.read_sql(query, conn)
    if not users.empty:
        allowed_users = users["SupervisorID"].unique().tolist()
        allowed_users = [i.lower() for i in allowed_users]
        print(allowed_users)
        if login_id in allowed_users or login_id in admin_users:
            return True
        else:
            return False
    # current_date -= timedelta(days=1)

def get_replacement_supervisor(user):
    conn = get_connection()
    # cur = conn.cursor()

    query = """
        SELECT "AbsentSupervisor" FROM evaluation."SupervisorReplacements"
        WHERE LOWER(%s) = LOWER("ReplacementSupervisorID")
          AND CURRENT_DATE BETWEEN "StartDate" AND "EndDate"
    """
    row = pd.read_sql(query, conn, params=[user]).iloc[0,0] if not pd.read_sql(query, conn, params=[user]).empty else None
    print(f'***************{row}')
    # cur.execute(query, (user,))
    # row = cur.fetchone()
    conn.close()

    return row

def add_replacement(absent, replacement, start, end):
    conn = get_connection()
    absent_id = get_ids(absent)
    replaced_id = get_ids(replacement)
    cur = conn.cursor()

    query = """
        INSERT INTO evaluation."SupervisorReplacements"
        ("AbsentSupervisor", "AbsentSupervisorID", "ReplacementSupervisor", "ReplacementSupervisorID", "StartDate", "EndDate")
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT ("AbsentSupervisorID", "StartDate", "EndDate")
        DO UPDATE SET "ReplacementSupervisor" = EXCLUDED."ReplacementSupervisor",
                      "ReplacementSupervisorID" = EXCLUDED."ReplacementSupervisorID", 
                      "EndDate" = EXCLUDED."EndDate";
    """

    cur.execute(query, (absent, absent_id, replacement, replaced_id, start, end))
    conn.commit()
    conn.close()

def load_all_users():
    conn = get_connection()
    query = """
        SELECT DISTINCT("CasePortalName")
        FROM evaluation."EditorsList"
        WHERE "GroupID" IN ('Editor Morning Shift', 'Editor Night Shift', 
                    'Pod-Al-Shuhada-1', 'Pod-Al-Shuhada-2', 'Urgent Team', 'Support Team_Night', 'RG-Cases', 'Support Team_Morning')
        AND "CasePortalName" IS NOT NULL
        ORDER BY "CasePortalName"
    """
    df = pd.read_sql(query, conn)
    conn.close()
    if df.empty:
        return None
    potential_supervisors = [i.strip() for i in df[~df["CasePortalName"].isin(current_supervisors)]["CasePortalName"].tolist()]
    return potential_supervisors

def convert_to_date(df):
    dtimeFields = ['Case Date', 'Case Submission Date','Latest Action Date','Transferred to Geospatial','GEO Completion','GEO S Completion','Transferred to Ops', 'Attachment Added Date', "ListDate"]
    for field in dtimeFields:
        if field in df.columns:
            df[field] = pd.to_datetime(df[field]).dt.date
    return df

def getGeoAction(df):
    
    if 'City Name' in df.columns:
        df['Region'] = ''
        for regionName, cities in regions_dict.items():
            df.loc[df["City Name"].isin(cities), 'Region'] = regionName
    
    geoActions = {'البيانات الجيومكانية صحيحة':['الجيومكانية صحيحة', 'الجيومكانية صحيحه', 'الجيومكانيه صحيحه', 'جيومكانية صحيحة'],'تعديل بيانات وصفية':['بيانات وصفية', 'بيانات وصفيه', 'البيانات الوصفية', 'البيانات الوصفيه'], 'تعديل أبعاد الأرض':['أبعاد', 'ابعاد', 'تعديل أبعاد', 'تعديل ابعاد', 'تعديل الأبعاد', 'تعديل الابعاد'], 
                'تجزئة':['تجزئة','التجزئة'], 'دمج':['دمج', 'الدمج'], 'رفض':["يعاد", 'رفض', 'نقص','مرفوض',"مستندات", "ارفاق", "إرفاق", "غير صحيحة", "الارض المختارة غير صحيحة"]}

    rejectionReasons = {'محضر الدمج/التجزئة':['محضر', 'المحضر', 'المحضر المطلوب', 'محضر اللجنة الفنية'], 
                        'إزدواجية صكوك': ['ازدواجية صكوك', 'إزدواجية صكوك', 'ازدواجيه', 'إزدواجيه صكوك'],
                        "خطأ في بيانات الصك'":['خطأ في بيانات الصك', 'خطأ في الصك'],
                        'صك الأرض':['صك الأرض', 'صك الارض', 'صك', 'الصك'], 
                        "إرفاق المؤشرات":["مؤشرات", "إرفاق كافه المؤشرات", "ارفاق كافة المؤشرات","ارفاق كافه المؤشرات"],
                        'طلب لوحدة عقارية':['طلب لوحدة عقارية', 'وحدة', 'وحده', 'وحده عقارية', 'وحدة عقاريه', 'عقارية'], 
                        'طلب مسجل مسبقاً':['سابق', 'مسبقا', 'مسبقاً', 'مسبق', 'طلب آخر', 'مكرر', 'طلب تسجيل اول مكرر'], 'إختيار خاطئ': ['اختيار خاطئ','المختارة غير صحيحة','إختيار خاطئ','المختارة غير صحيحه'],
                        "المخطط المعتمد":["المخطط", "مخطط"]}
    # Ensure required columns exist
    if not {'Geo Supervisor Recommendation','GEO Recommendation'}.issubset(df.columns):
        return df

    df['GeoAction'] = ''
    df['Rejection'] = ''

    for i in range(len(df)):
        recomm = df.at[i, 'Geo Supervisor Recommendation']
        recomm2 = df.at[i, 'GEO Recommendation']

        # Normalize empty values
        if pd.isna(recomm) or recomm == '':
            recomm = recomm2
        if pd.isna(recomm) or recomm == '':
            df.at[i, 'GeoAction'] = 'No Action'
            continue

        text = str(recomm)

        action_found = False

        # -----------------------------------------------------
        # 1️⃣ FIRST: check all official actions from geoActions
        # -----------------------------------------------------
        for action, keywords in geoActions.items():
            if any(k in text for k in keywords):
                df.at[i, 'GeoAction'] = action
                action_found = True

                # If it is a rejection, also check reasons
                if action == 'رفض':
                    for reject, r_words in rejectionReasons.items():
                        if any(k in text for k in r_words):
                            df.at[i, 'Rejection'] = reject

                break  # stop scanning actions once matched

        # -----------------------------------------------------
        # 2️⃣ If no official action found, check “شطفة”
        # -----------------------------------------------------
        if not action_found:
            if any(k in text for k in ['شطفة', 'الشطفة', 'شطفه']):
                df.at[i, 'GeoAction'] = 'شطفة'
                continue

        # -----------------------------------------------------
        # 3️⃣ If still nothing, check “غرفة كهرباء”
        # -----------------------------------------------------
        if not action_found:
            if any(k in text for k in ['كهرب', 'غرف', 'غرفة كهرباء', 'غرفة الكهرباء', 'غرفة', 'الكهرباء']):
                df.at[i, 'GeoAction'] = 'غرفة كهرباء'
                continue

        # -----------------------------------------------------
        # 4️⃣ If still no match → No Action
        # -----------------------------------------------------
        if not action_found:
            df.at[i, 'GeoAction'] = 'No Action'

    return df

def apply_theme_to_widgets(widget):
        """
        Apply text color override for widgets that don't fully respect QPalette.
        """
        if ThemeManager.is_dark:
            fg = "#e6e6e6"
            bg = "#3c3c3c"
        else:
            fg = "#000000"
            bg = "#ffffff"

        # Minimal stylesheet just for text
        widget.setStyleSheet(f"""
            QLineEdit, QComboBox, QTextEdit, QTableWidget {{
                color: {fg};
                background-color: {bg};
            }}
        """)

        # # Recursively apply to child widgets
        for child in widget.findChildren(QtWidgets.QWidget):
            apply_theme_to_widgets(child)


conn=get_connection()
admins = pd.read_sql("""SELECT DISTINCT("AdminID"), "AdminName" FROM evaluation."Administrator" WHERE "IsActive" = TRUE """, conn)
admin_users = [i.lower().strip() for i in admins["AdminID"].unique().tolist()]
print(admin_users)

regions_df = pd.read_sql("""SELECT * FROM evaluation."Regions" """, conn)
regions = regions_df["Region"].unique().tolist()
regions_dict = {}
for re in regions:
    regions_dict[re] = regions_df[regions_df['Region']==re]["CityName"].tolist()
if login_id in admin_users:
    supervisorName = admins[admins["AdminID"].str.lower()==login_id]
else:
    supervisorName = retrive_supervisor(login_id)#.strip()
print(login_id, supervisorName)
# admin_users = admin_users + [i for i in get_admins_upadtes() if i not in admin_users]
# print("+++++++++ ",admin_users)
supervisors_sql = """SELECT DISTINCT("SupervisorName") FROM evaluation."EditorsList" 
                    WHERE "GroupID" IN ('Editor Morning Shift', 'Editor Night Shift', 
                    'Pod-Al-Shuhada-1', 'Pod-Al-Shuhada-2', 'Urgent Team') AND "SupervisorName" IS NOT NULL """

current_supervisors = [i for i in pd.read_sql(supervisors_sql, conn)["SupervisorName"].tolist() if i not in excluded_supervisors]
conn.close()
# ----------------------------
# Main Window: Case List
# ----------------------------
class MainWindow(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("GRS Evaluation System V1.1")
        self.setWindowIcon(QIcon(APP_ICON_PATH))
        self.resize(1000, 720)

        # self.dark_mode_enabled = False    # or load from settings

        # ThemeManager.set_theme(self.dark_mode_enabled)
        # ThemeManager.apply_theme(self)    # ⬅ APPLY THEME TO MAIN WINDOW
        

        # # 🌈 Apply light theme
        # palette = QPalette()
        # palette.setColor(QPalette.Window, QColor("#000000"))
        # palette.setColor(QPalette.Base, QColor("#1d1d1d"))
        # palette.setColor(QPalette.AlternateBase, QColor("#f3f3f3"))
        # palette.setColor(QPalette.Button, QColor("#0A3556"))
        # palette.setColor(QPalette.ButtonText, QColor("#ffffff"))
        # self.setPalette(palette)

        self.setFont(QFont("Cairo", 8))
        
        # Main horizontal layout
        # === Main vertical layout (top title + content area) ===
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # icon = QPixmap(logo).scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio)
        # ----- Header Title -----
        header = QtWidgets.QWidget()
        header.setStyleSheet("background-color: #0A3556")
        header_layout = QtWidgets.QHBoxLayout(header)
        logo = QtWidgets.QLabel()
        pixmap = QPixmap(logo_path).scaled(110, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo.setPixmap(pixmap)

        title = QtWidgets.QLabel("Team Evaluation System")
        # if self.is_dark==True:
        #     title.setStyleSheet("font-size: 26px; font-weight: 700; margin-left: 10px; color: #0A3556;")
        # else:
        title.setStyleSheet("font-size: 24px; font-weight: 500; margin-left: 10px; color: #ffffff;")
        # if login_id in admin_users:
        rem, eval = self.getRemainingCount(supervisorName, replacement)
        self.remaining_label = QtWidgets.QLabel(f"Evaluated: {eval}   •   Remaining: {rem}")
        self.remaining_label.setStyleSheet("font-size: 16px; font-weight: bold; padding-right: 10px; color: #bc9975;")
        # Theme toggle button (sun/moon)
        self.theme_btn = QtWidgets.QPushButton("🌙")
        self.theme_btn.setFixedSize(36, 36)
        self.theme_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                font-size: 18px;
                border: none;
            }
            QPushButton:hover {
                color: #ffffff;
            }
        """)
        # self.theme_btn.clicked.connect(self.toggle_theme)
        self.theme_btn.clicked.connect(ThemeManager.toggle_theme)

        # self.apply_light_theme()
        
        header_layout.addWidget(logo)
        header_layout.addStretch()
        header_layout.addWidget(title)
        # header_layout.addSpacing(15)
        header_layout.addStretch()
        header_layout.addWidget(self.remaining_label)
        header_layout.addWidget(self.theme_btn)
        # main_layout.addWidget(icon)
        main_layout.addWidget(header)

        # ----- Main Content Area (Sidebar + Table) -----
        content_layout = QtWidgets.QHBoxLayout()
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(10)

        # Sidebar
        sidebar = QtWidgets.QFrame()
        sidebar.setFixedWidth(200)
        # sidebar.setStyleSheet("""
        # #     QFrame {
        # #         background-color: #E6EDF4;
        # #         border: 2px solid #d0d0d0;
        # #     }
        # # """)

        # Sidebar layout
        sidebar_layout = QtWidgets.QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(15, 20, 15, 20)
        sidebar_layout.setSpacing(10)

        title = QtWidgets.QLabel("🧺 Filter Cases")
        title.setFont(QFont("Cairo", 13))
        # title.setStyleSheet("color: #0A3556;")
        sidebar_layout.addWidget(title)

        # Supervisor
        sidebar_layout.addWidget(QtWidgets.QLabel("User Name:"))
        self.logged_supervisor = retrive_supervisor(login_id)  # replace 'current_user' with your variable

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
        # sidebar_layout.addWidget(QtWidgets.QLabel("From:"))
        self.start_date = QtWidgets.QDateEdit(QtCore.QDate.currentDate().addDays(-7))
        self.start_date.setCalendarPopup(True)
        # sidebar_layout.addWidget(self.start_date)

        # sidebar_layout.addWidget(QtWidgets.QLabel("To:"))
        self.end_date = QtWidgets.QDateEdit(QtCore.QDate.currentDate())#.addDays(-1))
        self.end_date.setCalendarPopup(True)
        # sidebar_layout.addWidget(self.end_date)
        
        # Supervisor:
        
        query = f"""SELECT "AssignedSupervisor","EditorName", "Region", "GeoAction" FROM evaluation."CaseAssignment" """
        sidebar_layout.addWidget(QtWidgets.QLabel("Supervisor:"))
        self.supervisor_drop = QtWidgets.QComboBox()
        self.supervisor_drop.addItem("")
        conn = get_connection()
        self.supervisor_drop.addItems(pd.read_sql(query, conn)['AssignedSupervisor'].unique().tolist())
        if login_id in admin_users:
            sidebar_layout.addWidget(self.supervisor_drop)
            if self.supervisor_drop.currentText():
                rem, eval = self.getRemainingCount(self.supervisor_drop.currentText(), replacement)
                self.remaining_label = QtWidgets.QLabel(f"Evaluated: {eval}   •   Remaining: {rem}")
        # Editor
        sidebar_layout.addWidget(QtWidgets.QLabel("Editor:"))
        self.editor_drop = QtWidgets.QComboBox()
        self.editor_drop.addItem("")
        # query = f"""SELECT "EditorName", "Region", "GeoAction" FROM evaluation."CaseAssignment" """
        if login_id not in admin_users:
            if replacement:
                current_sup = replacement
            else:
                current_sup = supervisorName
            query += f"""WHERE "AssignedSupervisor" = '{current_sup}' """
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
                background-color: #367580;
                color: white;
                padding: 6px;
                border-radius: 6px;
                font-weight: 200;
                font-size: 11px;
                width: 70%;
            }
            QPushButton:hover { background-color: #005a9e; }
        """)
        self.reset_btn = QtWidgets.QPushButton("🧹 Reset")
        self.reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #BC9975;
                color: white;
                padding: 6px;
                border-radius: 6px;
                font-weight: 400;
                font-size: 12px;
                width: 30%;
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

        self.update_btn = QtWidgets.QPushButton("Update Ops Data")
        self.update_btn.setStyleSheet("""
            QPushButton {
                background-color: #0A3556;
                color: white;
                padding: 6px;
                border-radius: 6px;
                font-weight: 400;
                font-size: 12px;
                width: 30%;
            }
            QPushButton:hover { background-color: #a1503e; }
        """)
        self.update_btn.clicked.connect(lambda: UpdateOpsData(conn).exec_())

        self.replacement_btn = QtWidgets.QPushButton("Manage Replacements")
        self.replacement_btn.setStyleSheet("""
            QPushButton {
                background-color: #0A3556;
                color: white;
                padding: 6px;
                border-radius: 6px;
                font-weight: 400;
                font-size: 12px;
                width: 30%;
            }
            QPushButton:hover { background-color: #a1503e; }
        """)
        self.replacement_btn.clicked.connect(lambda: ReplacementManager().exec_())
        if login_id in admin_users:
            sidebar_layout.addWidget(self.update_btn)
            sidebar_layout.addWidget(self.replacement_btn)

        # ----- Main area -----
        main_area = QtWidgets.QWidget()
        # main_area.setStyleSheet("background-color: #1d1d1d")
        main_vlayout = QtWidgets.QVBoxLayout(main_area)
        main_vlayout.setContentsMargins(10, 0, 10, 0)
        # main_vlayout.setStyleSheet("background-color: #1d1d1d")

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
                selection-background-color: #BC9975;
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
    # Light/Dark Themes
    # --------------------------
    # def apply_light_theme(self):
    #     palette = QPalette()
    #     palette.setColor(QPalette.Window, QColor("#F4F4F4"))
    #     palette.setColor(QPalette.Base, QColor("#FFFFFF"))
    #     palette.setColor(QPalette.AlternateBase, QColor("#F1F1F1"))
    #     palette.setColor(QPalette.Button, QColor("#0A3556"))
    #     palette.setColor(QPalette.ButtonText, QColor("#FFFFFF"))
    #     palette.setColor(QPalette.Text, QColor("#000000"))
    #     palette.setColor(QPalette.WindowText, QColor("#0A3556"))
    #     self.setPalette(palette)
    #     # '#367580'
    #     self.setStyleSheet("""
    #         QWidget {
    #             background-color: #F4F4F4;
    #             color: #000000;
    #         }

    #         QFrame {
    #             background-color: #367580;
    #             border: 1px solid #CCCCCC;
    #             padding: 2px;
    #             border-radius: 6px;
    #         }

    #         QLineEdit, QComboBox, QDateEdit {
    #             background-color: white;
    #             color: #000;
    #             border: 1px solid #BFBFBF;
    #             padding: 4px;
    #         }

    #         QPushButton {
    #             background-color: #0A3556;
    #             color: white;
    #             border-radius: 6px;
    #         }

    #         QTableWidget {
    #             background-color: #ffffff;
    #             alternate-background-color: #f3f3f3;
    #         }

    #         QHeaderView::section {
    #             background-color: #0A3556;
    #             color: white;
    #             font-weight: bold;
    #             padding: 4px;
    #         }
    #     """)

    #     self.theme_btn.setText("🌙")  # dark mode icon

    # def apply_dark_theme(self):
    #     palette = QPalette()
    #     palette.setColor(QPalette.Window, QColor("#121212"))
    #     palette.setColor(QPalette.Base, QColor("#1E1E1E"))
    #     palette.setColor(QPalette.AlternateBase, QColor("#2A2A2A"))
    #     palette.setColor(QPalette.Button, QColor("#BC9975"))
    #     palette.setColor(QPalette.ButtonText, QColor("#FFFFFF"))
    #     palette.setColor(QPalette.Text, QColor("#DDDDDD"))
    #     palette.setColor(QPalette.WindowText, QColor("#FFFFFF"))
    #     self.setPalette(palette)
    #     "#717070"
    #     "#c2c2c2"
    #     self.setStyleSheet("""
    #         QWidget {
    #             background-color: #121212;
    #             color: #E0E0E0;
    #         }

    #         QFrame {
    #             background-color: #1E1E1E;
    #             border: 1px solid #c2c2c2;
    #             padding: 2px
    #             border-radius: 6px;
    #         }

    #         QLineEdit, QComboBox, QDateEdit {
    #             background-color: #717070;
    #             color: #E0E0E0;
    #             border: 1px solid #c2c2c2;
    #             padding: 6px;
    #         }

    #         QPushButton {
    #             background-color: #BC9975;
    #             color: white;
    #             border: 1px solid #c2c2c2;
    #             border-radius: 6px;
    #         }

    #         QPushButton:hover {
    #             background-color: #4D8BC7;
    #         }

    #         QTableWidget {
    #             background-color: #1E1E1E;
    #             alternate-background-color: #2A2A2A;
    #             color: #E0E0E0;
    #         }

    #         QHeaderView::section {
    #             background-color: #3A6EA5;
    #             color: white;
    #             font-weight: bold;
    #             padding: 4px;
    #         }
    #     """)

    #     self.theme_btn.setText("☀️")  # light mode icon

    # def toggle_theme(self):
    #     if self.is_dark:
    #         self.apply_light_theme()
    #     else:
    #         self.apply_dark_theme()
    #     self.is_dark = not self.is_dark

    # def toggle_theme(self):
    #     if ThemeManager.current_theme == "light":
    #         ThemeManager.current_theme = "dark"
    #     else:
    #         ThemeManager.current_theme = "light"

    #     ThemeManager.apply_theme(self)
    # def toggle_theme(self, dark_mode_enabled):
    #     ThemeManager.set_theme(dark_mode_enabled)
    #     ThemeManager.apply_theme(self)        # apply theme to Main Window


    # --------------------------
    # Get Remaining Cases Count
    # --------------------------
    def getRemainingCount(self, supervisor_name, replacement_name):
        conn = get_connection()
        supervisorName = supervisor_name
        remaining_query = """
            SELECT COUNT(*) FROM evaluation."CaseAssignment"
            WHERE "IsEvaluated" = FALSE
            AND "IsRetired" = FALSE
        """
        evaluated_query = """
            SELECT COUNT(*) FROM evaluation."EvaluationTable"
            WHERE "EvaluationDate"::date = CURRENT_DATE
        """
        if login_id in admin_users:
            pass
            # if self.supervisor_drop:
            current_supervisor = supervisor_name
            # else:    
            #     current_supervisor = supervisor_name
        else:
            if replacement_name:
                current_supervisor = replacement_name
            else:
                current_supervisor = supervisor_name

                # supervisorName = replacement_name
            remaining_query += """AND "AssignedSupervisor" = %s """
            evaluated_query += """AND "EvaluatedBy" = %s """
            # print("=>>> Current Supervisor:", str(supervisorName))
        remainging = str(pd.read_sql(remaining_query, conn, params=[current_supervisor]).iloc[0,0])
        evaluated = str(pd.read_sql(evaluated_query, conn, params=[supervisorName]).iloc[0,0])
        return remainging, evaluated
    
    # def replace_existingCases(self):
    #     query = """SELECT *
    #             FROM evaluation."CaseAssignment"
    #             WHERE "IsEvaluated" = FALSE """
    #     op_data = """SELECT *
    #             FROM evaluation."CaseAssignment"
    #             WHERE "IsEvaluated" = FALSE """
    #     df = 

    def check_unevaluateded_status(self):
        conn = get_connection()
        
        # 1. Fetch all un-evaluated assignments
        query_assignments = """
            SELECT *
            FROM evaluation."CaseAssignment"
            WHERE "IsEvaluated" = FALSE
            AND "IsRetired" = FALSE
            AND "AssignmentDate" <> CURRENT_DATE
            AND "UniqueKey" NOT IN (SELECT "UniqueKey" FROM evaluation."OpsData")
        """
        assignments = pd.read_sql(query_assignments, conn)
        
        if assignments.empty:
            return  # Nothing to do
        
        print(f"There are {len(assignments)} un-evaluated cases to be updated")
        
        # 2. Loop through each assignment and check if case exists in OpsData
        QtWidgets.QMessageBox.warning(None, "Unresolved Assignments", 
                f"There are {len(assignments)} unresolved cases.")
        for idx, row in assignments.iterrows():
            assign_id = row["AssignmentID"]
            case_id = row["UniqueKey"]
            editor = row["EditorName"]
            assigned_supervisor = row["AssignedSupervisor"]
            assignment_date = row["AssignmentDate"]
            geo_action = row["GeoAction"]
            print(f"Searching for replacement for {case_id}...")
            if geo_action=="رفض":
                action_query = f"""AND "GeoAction" = '{geo_action}' """
            else:
                action_query = """AND "GeoAction" NOT IN ('رفض','No Action') """
            
            # Check if the case exists in OpsData
            check_query = """SELECT 1 FROM evaluation."OpsData" WHERE "UniqueKey" = %s"""
            exists = pd.read_sql(check_query, conn, params=[case_id])
            
            if exists.empty:
                print("_____Case no longer exists, fetch replacement using same logic as daily assignment")
                
                replacement_query = f"""
                    SELECT * FROM evaluation."OpsData"
                    WHERE "Geo Supervisor" = %s
                    {action_query}
                    AND "UniqueKey" NOT IN (
                    SELECT "UniqueKey" FROM evaluation."EvaluationTable"
                    UNION
                    SELECT "UniqueKey" FROM evaluation."CaseAssignment"
                )
                    ORDER BY "GEO S Completion" DESC
                    LIMIT 1
                """
                replacement = pd.read_sql(replacement_query, conn, params=[editor])#.iloc[0]
                print(f"_____{len(replacement)}")
                if not replacement.empty:
                    replacement_case = replacement.iloc[0]
                    replacement_case["REN"] = replacement_case["REN"].astype(str)
                    print(replacement_case)
                    # Update the assignment row with the new case info
                    # update_query = """
                    #     UPDATE evaluation."CaseAssignment"
                    #     SET "UniqueKey" = %s,
                    #         "Case Number" = %s,
                    #         "REN" = %s,
                    #         "CompletionDate" = %s,
                    #         "EditorRecommendation" = %s,
                    #         "GeoAction" = %s,
                    #         "SupervisorName" = %s,
                    #         "GroupID" = %s,
                    #         "Region" = %s
                    #     WHERE "AssignmentID" = %s
                    # """
                    update_query = """UPDATE evaluation."CaseAssignment"
                                    SET "IsRetired" = TRUE
                                     WHERE "AssignmentID" = %s """
                    cols =  ["UniqueKey", "Case Number", "REN", "GEO S Completion", "Geo Supervisor", 
                             "Geo Supervisor Recommendation", "SupervisorName", "GroupID", "GeoAction", "Region"]
                    values = replacement_case[cols].tolist() + [assigned_supervisor, assignment_date]
                    print(len(values))

                    print(f"Case: {case_id} is replaced by: {values[0]}")
                    cur = conn.cursor()
                    cur.execute(update_query, [assign_id])
                    cur.execute("""
                        INSERT INTO evaluation."CaseAssignment"
                        ("UniqueKey", "Case Number", "REN", "CompletionDate", "EditorName", "EditorRecommendation", 
                        "SupervisorName", "GroupID", "GeoAction", "Region", "AssignedSupervisor", "AssignmentDate")
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                        ON ConFLICT ("UniqueKey") DO NOTHING
                    """, values)
                    conn.commit()
                    cur.close()
        QtWidgets.QMessageBox.warning(None, "Unresolved Assignments", f"Finished Re-assignment of unresolved cases.")

    # --------------------------
    # On-demand assignment
    # --------------------------
    def generate_daily_assignment(self):
        self.check_unevaluateded_status()
        try:
            max_days = 360
            day_back = 1
            found_cases = False
            engine = create_engine("postgresql://evalApp:app1234@10.150.40.74:5432/GRS")
            # engine = create_engine("postgresql://evalApp:app1234@127.0.0.1:5432/GSA")
            conn = get_connection()
            active_editors = pd.read_sql("""SELECT DISTINCT("CasePortalName") FROM evaluation."EditorsList" 
                                        WHERE "CasePortalName" IS NOT NULL
                                        AND "GroupID" IN ('Editor Morning Shift', 'Editor Night Shift', 'Pod-Al-Shuhada-1', 'Pod-Al-Shuhada-2', 'Urgent Team')
                                        """, conn)["CasePortalName"].tolist()
            while day_back <= max_days:
                target_date = self.end_date.date().toPyDate() - timedelta(days=day_back)
                # print(f"Searching Cases on {target_date}")
                    # Pull yesterday's cases
                sql = """
                    SELECT *
                    FROM evaluation."OpsData"
                    WHERE "GEO S Completion"::date = %s
                    AND "GeoAction" IS NOT NULL AND "GeoAction" <> 'No Action'
                    AND "GroupID" IN ('Editor Morning Shift', 'Editor Night Shift', 'Pod-Al-Shuhada-1', 'Pod-Al-Shuhada-2', 'Urgent Team')
                    AND "UniqueKey" NOT IN (
                        SELECT "UniqueKey" FROM evaluation."EvaluationTable"
                        UNION
                        SELECT "UniqueKey" FROM evaluation."CaseAssignment"
                    )
                """
                df = pd.read_sql(sql, conn, params=[target_date])

                if not df.empty:# or len(df["Geo Supervisor"].unique().tolist()) >= 20:
                    found_cases = True
                    break
                day_back += 1
                # print(f"No cases found on {target_date}. Searching back {day_back} days...")

            if not found_cases:
                QtWidgets.QMessageBox.warning(None, "No Cases", 
                    f"No valid cases found in the past {max_days} days.")
                return None, day_back-1

            # Editors and Supervisors for assignment

            supervisors = [i for i in current_supervisors]
            excluded = ["Mahmoud Aboalmaged", "Moataz Ibrahim"] + [i for i in supervisors]
            editors = [i for i in active_editors if not pd.isnull(i) and i not in excluded]
            random.shuffle(supervisors)
            print("----------------",supervisors)

            assignments = []

            # Create a list of all dates to search, starting with target_date
            search_dates = [self.end_date.date().toPyDate() - timedelta(days=x) for x in range(1, max_days + 1)]
            dates_back = []
            for i, editor in enumerate(active_editors):
                # 1 — Get cases for this editor from the primary (target) date
                editor_cases = df[df["Geo Supervisor"] == editor]

                reject_case = editor_cases[editor_cases["GeoAction"] == 'رفض']
                edit_case = editor_cases[editor_cases["GeoAction"] != 'رفض']
                # print(f"==================================================\n Initial Df Editor: {editor} | Date: {target_date}\n{len(reject_case)}, {len(edit_case)}")
                # 2 — If missing categories → search older dates
                if reject_case.empty or edit_case.empty:

                    for d in search_dates[1:]:  # skip target_date already checked
                        # print(f"==================================================\n Searching for cases on {d}")
                        if d not in dates_back:
                            dates_back.append(d)
                        sql_more = """
                            SELECT *
                            FROM evaluation."OpsData"
                            WHERE "GEO S Completion"::date = %s
                            AND "GeoAction" IS NOT NULL AND "GeoAction" <> 'No Action'
                            AND "GroupID" IN ('Editor Morning Shift', 'Editor Night Shift', 'Pod-Al-Shuhada-1', 'Pod-Al-Shuhada-2', 'Urgent Team')
                            AND "Geo Supervisor" = %s
                            AND "UniqueKey" NOT IN (
                                    SELECT "UniqueKey" FROM evaluation."EvaluationTable"
                                    UNION
                                    SELECT "UniqueKey" FROM evaluation."CaseAssignment"
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
                        # print(editor,":", len(reject_case), "/ ", len(edit_case))
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
            assign_df = assign_df.drop_duplicates(subset=["UniqueKey"])
            # Write to CaseAssignment
            assign_df = assign_df[["UniqueKey","Case Number", "REN", "GEO S Completion", "Geo Supervisor", "Geo Supervisor Recommendation", "SupervisorName", "GroupID", "GeoAction",
                    "Region", "AssignedSupervisor","AssignmentDate"]]
            assign_df = assign_df.rename({"GEO S Completion":"CompletionDate", "Geo Supervisor":"EditorName", 
                                        "Geo Supervisor Recommendation":"EditorRecommendation"}, axis=1)
            assign_df[["UniqueKey","Case Number", "REN", "CompletionDate", "EditorName", "EditorRecommendation", "SupervisorName", "GroupID", "GeoAction",
                    "Region", "AssignedSupervisor","AssignmentDate"]].to_sql("CaseAssignment", engine, schema='evaluation', if_exists="append", index=False)
            
            days_searched = target_date - min(dates_back) if dates_back else timedelta(0)
            return assign_df, day_back, days_searched.days
            # return 
        except Exception as e:
            QtWidgets.QMessageBox.warning(None, "Error during case assignment", 
                f"{e}")
        # return "",'',''
        

    # --------------------------
    # Load supervisor cases
    # --------------------------
    def load_supervisor_assignment(self, supervisor_name):
        editor = self.editor_drop.currentText().strip()
        region = self.region_combo.currentText().strip()
        action = self.action_combo.currentText().strip()

        conn = get_connection()

        # --- Replacement Supervisor ---
        replace_supervisor = get_replacement_supervisor(login_id)
        if replace_supervisor:
            supervisor_name = replace_supervisor

        # --- Query Construction ---
        base_query = """
            SELECT *
            FROM evaluation."CaseAssignment"
        """

        where_clauses = []
        params = []

        # --- Admin Mode: can see all supervisors ---
        if login_id not in admin_users:
            where_clauses.append('"AssignedSupervisor" = %s')
            params.append(supervisor_name)
        else:
            supervisor = self.supervisor_drop.currentText().strip()
            if supervisor:
                where_clauses.append('"AssignedSupervisor" = %s')
                params.append(supervisor)

        # Common filters for both admin and normal users
        where_clauses.append('("IsEvaluated" = FALSE OR "AssignmentDate" = CURRENT_DATE)')

        if editor:
            where_clauses.append('"EditorName" = %s')
            params.append(editor)

        if action:
            where_clauses.append('"GeoAction" = %s')
            params.append(action)

        if region:
            where_clauses.append('"Region" = %s')
            params.append(region)

        # Final SQL
        sql = base_query + " WHERE " + " AND ".join(where_clauses) + ' ORDER BY "EditorName"'

        # Debug print if needed
        # print("SQL:", sql)
        # print("Params:", params)

        df = pd.read_sql(sql, conn, params=params)
        print(f"/////{sql}")
        print(len(df))
        return df

    # --------------------------
    # Usage example in PyQt MainWindow
    # --------------------------
    def load_cases(self):
        supervisor = self.sup_input.text().strip()
        replacement_supervisor = get_replacement_supervisor(login_id)
        # if not supervisor:
        #     QtWidgets.QMessageBox.warning(self, "Error", "Please enter Supervisor Name.")
        #     return

        conn = get_connection()
        check_updates = """SELECT * FROM evaluation."OpsData" 
            WHERE "UploadDate"=CURRENT_DATE 
            LIMIT 1"""
        Ops_df = pd.read_sql(check_updates, conn)
        if Ops_df.empty:
            if login_id in admin_users:
                message = "Database is not up to date."
            else:
                message = "Database is not up to date. Please notify the Admin."
            QtWidgets.QMessageBox.warning(self, "Error", message)
            return


        # Check if assignments exist
        check_sql = """
            SELECT COUNT(*) AS "COUNT" FROM evaluation."CaseAssignment"
            WHERE "AssignmentDate" = CURRENT_DATE
        """
        count = pd.read_sql(check_sql, conn)['COUNT'].iloc[0]

        if count==0:
            # self.check_unevaluateded_status()
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
                        # item.setBackground(QColor("#ffb3b3"))  # Light red
                        item.setBackground(QColor("#b48d83"))  # Light red
                    else:
                        # item.setBackground(QColor("#c2f0c2"))  # Light green
                        item.setBackground(QColor("#86acb2"))  # Light green

                self.table.setItem(r, c, item)
        rem, eval = self.getRemainingCount(supervisor, replacement_supervisor)
        self.remaining_label.setText(f"Evaluated: {eval}/Remaining: {rem}")

    def reset_filters(self):
        """Reset all filters to default state."""
        # self.sup_input.clear()
        self.editor_drop.clear()
        self.action_combo.setCurrentIndex(0)
        self.region_combo.setCurrentIndex(0)
        self.start_date.setDate(QtCore.QDate.currentDate().addDays(-7))
        self.end_date.setDate(QtCore.QDate.currentDate())#.addDays(-1))

    def open_evaluation(self, row, column):
        if self.cases_df.empty:
            return
        eval_window = EvaluationWindow(self.cases_df, row, self.sup_input.text().strip())
        ThemeManager.apply_theme()
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

        self.setFont(QFont("Cairo", 9))
        # self.setStyleSheet("""
        #     QGroupBox { font-weight: bold; color: #444; border: 1px solid #ccc; border-radius: 6px; margin-top: 8px; }
        #     QGroupBox::title { subcontrol-origin: margin; left: 10px; top: -4px; }
        #     QLabel { color: #333; }
        #     QPushButton {
        #         background-color: #0A3556; color: white;
        #         padding: 6px 12px; border-radius: 6px;
        #     }
        #     QPushButton:hover { background-color: #005a9e; }
        # """)

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
                background-color: #0A3556;
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
        self.header.setStyleSheet("font-size:16px; font-weight:bold; color:#824131; margin-bottom:6px;")
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
            "Group": "GroupID",
            "Region": "Region",
        }
        # Case info fields
        case_fields = {
            "Case Number": case.get("Case Number", ""),
            "REN": case.get("REN", ""),
            "Completion Date": case.get("CompletionDate", ""),
            "Editor Name": case.get("EditorName", ""),
            "GeoAction": case.get("GeoAction", ""),
            "Supervisor": case.get("SupervisorName", ""),
            "Group": case.get("GroupID", ""),
            "Region": case.get("Region", ""),
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
        comment = QtWidgets.QLabel("<b>Comments:</b>")
        self.comment_text = QtWidgets.QTextEdit()
        self.comment_text.setReadOnly(False)
        self.comment_text.setMaximumHeight(60)
        # eval_layout.addWidget(comment, (len(fields) // 2) + 1, 0, 1, 2)
        # eval_layout.addWidget(self.comment_text, len(fields)//2 + 2,0, 1, 4)
                
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
            topology_score     = score(topology, 0.25)
            completeness_score = score(completeness, 0.5)
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
        evaluatedCases = pd.read_sql("""SELECT "UniqueKey" FROM evaluation."EvaluationTable" """, conn)
        
        if case['UniqueKey'] in evaluatedCases["UniqueKey"].values:
            QtWidgets.QMessageBox.warning(self, "Duplicated Entry", f"Case {case['Case Number']} has already been evaluated.")
        
        else:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO evaluation."EvaluationTable"
                    ("UniqueKey","Case Number","CompletionDate","EditorRecommendation", "EditorName","SupervisorName","GroupID","GeoAction",
                    "Procedure","ProcedureScore","Recommendation","RecommendationScore", "Topology","TopologyScore","Completeness","CompletenessScore",
                    "BlockAlignment","BlockAlignmentScore","ProceduralAccuracy", "TechnicalAccuracy","EvaluatedBy","EvaluationDate")
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                            %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """, values)
                conn.commit()
            # Update EvaluationStatus On Assignment Table
            update_sql = """
                UPDATE evaluation."CaseAssignment"
                SET "IsEvaluated" = TRUE
                WHERE "UniqueKey" = %s
                AND "AssignedSupervisor" = %s
            """
            with conn.cursor() as cur:
                if replacement:
                    assigned_supervisor = replacement
                    
                else:
                    assigned_supervisor = self.supervisor_name
                
                cur.execute(update_sql, (case["UniqueKey"], assigned_supervisor))
                conn.commit()

            # self.remaining_label.setText(str(self.getRemainingCount()))
            
            conn.close()
            QtWidgets.QMessageBox.information(self, "Success", "Evaluation submitted!")

class ReplacementManager(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Supervisor Replacement Manager")
        self.setWindowIcon(QIcon(APP_ICON_PATH))
        self.resize(350, 200)

        layout = QtWidgets.QVBoxLayout(self)

        # Absent supervisor
        self.absent_combo = QtWidgets.QComboBox()
        self.absent_combo.addItems(current_supervisors)
        # self.absent_combo.setStyleSheet("""
        #     QComboBox {
        #     color: #ffffff;
        #     background-color: #0A3556;
        #     border-radius: 6px;
        #     padding: 4px;
        #     font-weight: bold;
        #     }
        #     QComboBox::drop-down {
        #     border: none;
        #     }
        #     QComboBox QAbstractItemView {
        #     color: #ffffff;
        #     background-color: #0A3556;
        #     selection-background-color: #367580;
        #     }
        # """)

        # Replacement supervisor
        self.replacement_combo = QtWidgets.QComboBox()
        self.replacement_combo.addItems(load_all_users())

        # Date pickers
        self.start_date = QtWidgets.QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QtCore.QDate.currentDate())

        self.end_date = QtWidgets.QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QtCore.QDate.currentDate())

        # Button
        save_btn = QtWidgets.QPushButton("Save Replacement")
        save_btn.clicked.connect(self.save_replacement)

        # Add fields
        layout.addWidget(QtWidgets.QLabel("Absent Supervisor:"))
        layout.addWidget(self.absent_combo)
        layout.addWidget(QtWidgets.QLabel("Replacement Supervisor:"))
        layout.addWidget(self.replacement_combo)
        layout.addWidget(QtWidgets.QLabel("Start Date:"))
        layout.addWidget(self.start_date)
        layout.addWidget(QtWidgets.QLabel("End Date:"))
        layout.addWidget(self.end_date)
        layout.addWidget(save_btn)

    def save_replacement(self):
        absent = self.absent_combo.currentText()
        replacement = self.replacement_combo.currentText()
        start = self.start_date.date().toPyDate()
        end = self.end_date.date().toPyDate()

        add_replacement(absent, replacement, start, end)

        QtWidgets.QMessageBox.information(self, "Success", "Replacement saved!")

class UpdateOpsData(QtWidgets.QDialog):
    def __init__(self, engine, parent=None):
        super().__init__(parent)
        self.engine = create_engine("postgresql+psycopg2://evalApp:app1234@10.150.40.74:5432/GRS")

        self.setWindowTitle("Update Ops Data")
        self.setMinimumWidth(400)
        self.setWindowIcon(QIcon(APP_ICON_PATH))

        # Title label
        self.title = QtWidgets.QLabel("Update Ops Data")
        self.title.setObjectName("TitleLabel")

        # --- UI Elements ---
        self.label = QtWidgets.QLabel("Select OpsData Excel file:")
        self.btn_select = QtWidgets.QPushButton("Browse")
        self.btn_select.setStyleSheet("""
           QPushButton {
                background-color: #0A3556;
                color: white;
                border-radius: 6px;
                padding: 4px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #a1503e; }
        """)
        self.btn_run = QtWidgets.QPushButton("Update OP Data")
        self.btn_run.setStyleSheet("""
           QPushButton {
                background-color: #824131;
                color: white;
                border-radius: 6px;
                padding: 4px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #a1503e; }
        """)
        self.status = QtWidgets.QLabel("")

        # Disable Run button until a file is chosen
        self.btn_run.setEnabled(False)

        # Layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.btn_select)
        layout.addWidget(self.btn_run)
        layout.addWidget(self.status)
        self.setLayout(layout)

        # Connect signals
        self.btn_select.clicked.connect(self.select_excel)
        # self.btn_run.clicked.connect(lambda: self.run_update
        self.btn_run.clicked.connect(self.run_update)
        ThemeManager.apply_theme()
        # ⭐ APPLY THE THEME
        # ThemeManager.apply_theme(self)

    def update_status(self, msg):
        self.status.setText(msg)
        QtWidgets.QApplication.processEvents()


    def select_excel(self):
        """Open file dialog and return selected Excel file."""
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Select Excel File",
            "",
            "Excel Files (*.xlsx *.xls)"
        )
        if file_path:
            self.file_path = file_path
            self.btn_run.setEnabled(True)
            return file_path
        else:    
            return None

    def load_excel_df(self, file_path):
        """Load Excel into DataFrame."""
        try:
            wb = openpyxl.load_workbook(file_path, read_only=True)
            ws = wb['Sheet1']
            header_row_idx = None
            for i, row in enumerate(ws.iter_rows(max_col=2, max_row=10, values_only=True)):
                if row and 'Case Number' in row:
                    header_row_idx = i
                    break
            wb.close()
            if header_row_idx is not None:
                df = pd.read_excel(file_path, sheet_name='Sheet1', skiprows=header_row_idx)
                df = df.drop_duplicates(subset="Case Number")
                df = df[(df['Geo Supervisor'].notnull()) & (df['GEO S Completion'].notnull())]
                df = df.reset_index(drop=True)
                print(len(df))
                df["UniqueKey"] = [str(i) + '_' + str(pd.to_datetime(j).round('s'))  for i, j in zip(df["Case Number"].values, df["GEO S Completion"].values)]
                df["UploadDate"] = datetime.now().date()
                df["UploadedBy"] = os.getlogin()
                df = convert_to_date(df)
                df = getGeoAction(df) 
                print("Excel file was loaded successfully")
                return df
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.parent, "Error", f"Failed to read Excel file:\n{e}")
            return None

    def load_editorsList(self):
        """Load userlist table from DB."""
        print("Loading Editors' List")
        try:
            # engine = create_engine("postgresql://app_user:app1234@10.150.40.74:5432/GSA")
            engine2 = create_engine("postgresql://postgres:1234@localhost:5432/GSA")
            editors_list = pd.read_sql("SELECT * FROM public.\"EditorsList\" ", engine2)
            editors_list = convert_to_date(editors_list)
            print("Successfully Loaded Editors' List ✅")
            return editors_list
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.parent, "Error", f"Failed to load userlist:\n{e}")
            return None

    def join_editors_list(self, ops_df, editorsList):
        """Join Excel data with userlist on a given key."""
        print("🔁Joining Editors' List")
        
        try:
            ops_df['GEO S Completion'] = pd.to_datetime(ops_df['GEO S Completion']).dt.normalize()
            editorsList = editorsList.rename({'CaseProtalName': 'Geo Supervisor'}, axis=1)
            editorsList["ListDate"] = pd.to_datetime(editorsList["ListDate"]).dt.normalize()
            print("✅ Date Normalization!")
            print(ops_df.columns[-15:])
            print(editorsList.columns)
            ops_df = ops_df.sort_values(by=["GEO S Completion", "Geo Supervisor"])
            editorsList = editorsList.sort_values(by=["ListDate", "Geo Supervisor"])
            print("✅ Sorted Dataframes")
            ops_df = pd.merge_asof(ops_df, editorsList, by="Geo Supervisor", left_on="GEO S Completion", 
                                    right_on="ListDate", direction='backward')
            print("✅ Merged")
            ops_df['GEO S Completion'] = [pd.to_datetime(i).date() for i in ops_df['GEO S Completion']]
            print("✅ GEO S Completion Converted")
            # print(ops_df.columns[-10:])
            ops_df['ListDate'] = [pd.to_datetime(i).date() for i in ops_df['ListDate']]
            print("✅ Ops Data was joined successfully")
            return ops_df
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to join data:\n{e}")
            return None

    def replace_opsdata(self, ops_df):
        """Replace OpsData table in the DB."""
        try:
            with self.engine.begin() as conn:
            # cur = conn.cursor()
                conn.execute(text("""TRUNCATE evaluation."OpsData" RESTART IDENTITY"""))
            print("✅ Cleared Op Data")
            # Pandas table and inserts
            ops_df.to_sql("OpsData", self.engine, schema='evaluation', if_exists='append', index=False)#, method="multi", chunksize=5000)
            # print("✅ Loaded New Op Data")
            self.update_status("⬆️ Updating database...")
            # conn.commit()
            QtWidgets.QMessageBox.information(self, "Success", "Ops Data updated successfully!")

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to update OpsData:\n{e}")

    def run_update(self):
        """Main workflow to update OpsData."""
        file_path = self.file_path
        if not file_path:
            QtWidgets.QMessageBox.warning(self, "Error", "Please select an Excel file.")
            return

        self.update_status("📄 Loading Excel file...")
        ops_data = self.load_excel_df(file_path)
        if ops_data is None:
            return

        self.update_status("👥 Loading Editors List...")
        df_editorList = self.load_editorsList()
        if df_editorList is None:
            return

        self.update_status("🔗 Joining editors list...")
        df_joined = self.join_editors_list(ops_data, df_editorList)
        if df_joined is None:
            return
        self.update_status("⬆️ Updating database...")
        self.replace_opsdata(df_joined)
        
# ------------------
# THEME Manager
# ------------------
# class ThemeManager:
#     is_dark = False

#     @staticmethod
#     def set_theme(is_dark: bool):
#         ThemeManager.is_dark = is_dark
#         ThemeManager.apply_theme()

#     @staticmethod
#     def toggle_theme():
#         # Flip the current theme
#         ThemeManager.is_dark = not ThemeManager.is_dark
#         # Apply the new theme to the app
#         ThemeManager.apply_theme()

#     @staticmethod
#     def fix_input_text_color():
#         palette = QtWidgets.QApplication.palette()

#         for w in QtWidgets.QApplication.allWidgets():
#             if isinstance(w, (QtWidgets.QLineEdit,
#                             QtWidgets.QComboBox,
#                             QtWidgets.QSpinBox,
#                             QtWidgets.QDoubleSpinBox,
#                             QtWidgets.QDateEdit,
#                             QtWidgets.QDateTimeEdit,
#                             QtWidgets.QTextEdit,
#                             QtWidgets.QPlainTextEdit)):

#                 w.setPalette(palette)

#     @staticmethod
#     def apply_theme():
#         if ThemeManager.is_dark:
#             bg = QtGui.QColor(45, 45, 45)
#             fg = QtGui.QColor(240, 240, 240)
#             base = QtGui.QColor(60, 60, 60)
#         else:
#             bg = QtGui.QColor(240, 240, 240)
#             fg = QtGui.QColor(0, 0, 0)
#             base = QtGui.QColor(255, 255, 255)

#         palette = QtGui.QPalette()
#         palette.setColor(QtGui.QPalette.Window, bg)
#         palette.setColor(QtGui.QPalette.WindowText, fg)
#         palette.setColor(QtGui.QPalette.Base, base)
#         palette.setColor(QtGui.QPalette.AlternateBase, bg)
#         palette.setColor(QtGui.QPalette.Text, fg)
#         palette.setColor(QtGui.QPalette.Button, bg)
#         palette.setColor(QtGui.QPalette.ButtonText, fg)
#         palette.setColor(QtGui.QPalette.PlaceholderText, fg)
#         palette.setColor(QtGui.QPalette.ToolTipText, fg)
#         palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(53, 132, 228))
#         palette.setColor(QtGui.QPalette.HighlightedText, QtGui.QColor(255, 255, 255))

#         QtWidgets.QApplication.setPalette(palette)

#         ThemeManager.fix_input_text_color()
        

from PyQt5 import QtWidgets, QtGui

class ThemeManager:
    is_dark = False

    @staticmethod
    def set_theme(is_dark: bool):
        ThemeManager.is_dark = is_dark
        ThemeManager.apply_theme()

    @staticmethod
    def toggle_theme():
        ThemeManager.is_dark = not ThemeManager.is_dark
        ThemeManager.apply_theme()

    @staticmethod
    def apply_theme():
        # colors
        if ThemeManager.is_dark:
            bg = QtGui.QColor(45, 45, 45)
            fg = QtGui.QColor(240, 240, 240)
            base = QtGui.QColor(60, 60, 60)
        else:
            bg = QtGui.QColor(240, 240, 240)
            fg = QtGui.QColor(0, 0, 0)
            base = QtGui.QColor(255, 255, 255)

        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Window, bg)
        palette.setColor(QtGui.QPalette.WindowText, fg)
        palette.setColor(QtGui.QPalette.Base, base)
        palette.setColor(QtGui.QPalette.AlternateBase, bg)
        palette.setColor(QtGui.QPalette.Text, fg)
        palette.setColor(QtGui.QPalette.Button, bg)
        palette.setColor(QtGui.QPalette.ButtonText, fg)
        palette.setColor(QtGui.QPalette.ToolTipText, fg)
        palette.setColor(QtGui.QPalette.PlaceholderText, fg)
        palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(53, 132, 228))
        palette.setColor(QtGui.QPalette.HighlightedText, QtGui.QColor(255, 255, 255))

        QtWidgets.QApplication.setPalette(palette)

        # Apply palette/explicit role fixes to existing widgets
        ThemeManager._apply_palette_to_existing_widgets(palette, base, fg)

    @staticmethod
    def _apply_palette_to_existing_widgets(palette: QtGui.QPalette, base: QtGui.QColor=None, fg: QtGui.QColor=None):
        """
        Apply palette to all existing widgets. For input widgets, we patch the
        widget's own palette so that QPalette.Text and QPalette.Base are set.
        This avoids using stylesheets and preserves native rendering.
        """

        app = QtWidgets.QApplication.instance()
        if app is None:
            return

        # First: apply the application palette to top-level widgets (makes most widgets inherit)
        for w in app.topLevelWidgets():
            w.setPalette(palette)
            # sometimes needed to force a repaint
            w.update()

        # Now: individually patch input widgets that commonly ignore app palette roles
        for w in app.allWidgets():
            # Skip if widget has its own stylesheet — that will override palette
            if hasattr(w, "styleSheet") and w.styleSheet():
                # If you intended to use stylesheets, then palette changes may not show.
                # You can either clear the stylesheet here (w.setStyleSheet("")) or leave it.
                # For safety we don't clear it, but inform the user in debug.
                # print(f"Widget {w} has stylesheet -> palette may be ignored")
                continue

            if isinstance(w, (QtWidgets.QLineEdit, QtWidgets.QTextEdit, QtWidgets.QPlainTextEdit)):
                wp = w.palette()
                wp.setColor(QtGui.QPalette.Text, palette.color(QtGui.QPalette.Text))
                wp.setColor(QtGui.QPalette.Base, palette.color(QtGui.QPalette.Base))
                wp.setColor(QtGui.QPalette.PlaceholderText, palette.color(QtGui.QPalette.PlaceholderText))
                w.setPalette(wp)
                w.update()

            elif isinstance(w, QtWidgets.QComboBox):
                # For combobox, set palette for the widget and its internal lineEdit if present
                wp = w.palette()
                wp.setColor(QtGui.QPalette.Text, palette.color(QtGui.QPalette.Text))
                wp.setColor(QtGui.QPalette.Base, palette.color(QtGui.QPalette.Base))
                w.setPalette(wp)
                # If the combobox has an editable line edit, patch it too
                le = w.lineEdit()
                if le is not None:
                    lep = le.palette()
                    lep.setColor(QtGui.QPalette.Text, palette.color(QtGui.QPalette.Text))
                    lep.setColor(QtGui.QPalette.Base, palette.color(QtGui.QPalette.Base))
                    le.setPalette(lep)
                    le.update()
                w.update()

            elif isinstance(w, (QtWidgets.QSpinBox, QtWidgets.QDoubleSpinBox, QtWidgets.QDateEdit, QtWidgets.QDateTimeEdit)):
                wp = w.palette()
                wp.setColor(QtGui.QPalette.Text, palette.color(QtGui.QPalette.Text))
                wp.setColor(QtGui.QPalette.Base, palette.color(QtGui.QPalette.Base))
                w.setPalette(wp)
                w.update()

            elif isinstance(w, QtWidgets.QTableWidget):
                # TableWidget uses Text and Base for cells; also update header views
                wp = w.palette()
                wp.setColor(QtGui.QPalette.Text, palette.color(QtGui.QPalette.Text))
                wp.setColor(QtGui.QPalette.Base, palette.color(QtGui.QPalette.Base))
                w.setPalette(wp)
                # Headers:
                header = w.horizontalHeader()
                if header is not None:
                    hp = header.palette()
                    hp.setColor(QtGui.QPalette.WindowText, palette.color(QtGui.QPalette.WindowText))
                    header.setPalette(hp)
                w.viewport().update()
                w.update()

            elif isinstance(w, QtWidgets.QPushButton):
                # Buttons usually respect ButtonText, but patch if needed
                bp = w.palette()
                bp.setColor(QtGui.QPalette.ButtonText, palette.color(QtGui.QPalette.ButtonText))
                bp.setColor(QtGui.QPalette.Button, palette.color(QtGui.QPalette.Button))
                w.setPalette(bp)
                w.update()

        # Process events to force redraw
        QtWidgets.QApplication.processEvents()


# ----------------------------
# Main
# ----------------------------
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    # if supervisorName is None:
        
    #     QtWidgets.QMessageBox.critical(
    #         None,
    #         "Access Denied",
    #         f"Your login ID '{login_id}' is not registered as a supervisor."
    #     )
    #     sys.exit()  # block app launch
    replacement = get_replacement_supervisor(login_id)
    print(f'------------------{replacement}, {is_allowed_user(login_id)}, {supervisorName}')
    if not is_allowed_user(login_id) and not replacement:
        QtWidgets.QMessageBox.critical(None, "Access Denied", "You do not have permission to use this application.")
        sys.exit(1)

    # Load saved theme
    # dark = load_theme_setting()
    ThemeManager.set_theme(True)
    ThemeManager.toggle_theme()
    # ThemeManager.apply_theme(app)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
