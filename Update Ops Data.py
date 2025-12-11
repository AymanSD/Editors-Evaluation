import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import openpyxl
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta
import urllib.parse
import os
import sys

# ---------------------------------------------------------
#  ORIGINAL FUNCTIONS (unchanged)
# ---------------------------------------------------------

def getGeoAction(df):
    if 'City Name' in df.columns:
        df['Region'] = ''
        for regionName, cities in regions_dict.items():
            df.loc[df["City Name"].isin(cities), 'Region'] = regionName

    if not {'Geo Supervisor Recommendation','GEO Recommendation'}.issubset(df.columns):
        return df

    df['GeoAction'] = ''
    df['Rejection'] = ''

    for i in range(len(df)):
        recomm = df.at[i, 'Geo Supervisor Recommendation']
        recomm2 = df.at[i, 'GEO Recommendation']

        if pd.isna(recomm) or recomm == '':
            recomm = recomm2
        if pd.isna(recomm) or recomm == '':
            df.at[i, 'GeoAction'] = 'No Action'
            continue

        text_val = str(recomm)
        action_found = False

        for action, keywords in geoActions.items():
            if any(k in text_val for k in keywords):
                df.at[i, 'GeoAction'] = action
                action_found = True

                if action == 'رفض':
                    for reject, r_words in rejectionReasons.items():
                        if any(k in text_val for k in r_words):
                            df.at[i, 'Rejection'] = reject
                break

        if not action_found:
            if any(k in text_val for k in ['شطفة', 'الشطفة', 'شطفه']):
                df.at[i, 'GeoAction'] = 'شطفة'
                continue

        if not action_found:
            if any(k in text_val for k in ['كهرب', 'غرف', 'غرفة كهرباء', 'غرفة الكهرباء', 'غرفة', 'الكهرباء']):
                df.at[i, 'GeoAction'] = 'غرفة كهرباء'
                continue

        if not action_found:
            df.at[i, 'GeoAction'] = 'No Action'

    return df


def load_excel(filename):
    wb = openpyxl.load_workbook(filename, read_only=True)
    ws = wb['Sheet1']
    header_row_idx = None

    for i, row in enumerate(ws.iter_rows(max_col=2, max_row=10, values_only=True)):
        if row and 'Case Number' in row:
            header_row_idx = i
            break

    wb.close()

    if header_row_idx is not None:
        return pd.read_excel(filename, sheet_name='Sheet1', skiprows=header_row_idx)
    else:
        raise ValueError("Header row containing 'Case Number' not found.")


def convert_to_date(df):
    dtimeFields = [
        'Case Date', 'Case Submission Date','Latest Action Date',
        'Transferred to Geospatial','GEO Completion','GEO S Completion',
        'Transferred to Ops', 'Attachment Added Date', "ListDate"
    ]
    for field in dtimeFields:
        if field in df.columns:
            df[field] = pd.to_datetime(df[field]).dt.date
    return df


def join_userlist(comp_df, editorlist):
    comp_df['GEO S Completion'] = pd.to_datetime(comp_df['GEO S Completion']).dt.normalize()
    editorlist = editorlist.rename({'CaseProtalName': 'Geo Supervisor'}, axis=1)
    editorlist["ListDate"] = pd.to_datetime(editorlist["ListDate"]).dt.normalize()

    comp_df = comp_df.sort_values(by=["GEO S Completion", "Geo Supervisor"])
    editorlist = editorlist.sort_values(by=["ListDate", "Geo Supervisor"])

    comp_df = pd.merge_asof(comp_df, editorlist, by="Geo Supervisor",
                            left_on="GEO S Completion", right_on="ListDate",
                            direction='backward')

    comp_df['GEO S Completion'] = comp_df['GEO S Completion'].dt.date
    comp_df['ListDate'] = comp_df['ListDate'].dt.date
    return comp_df


# ---------------------------------------------------------
# CONSTANTS
# ---------------------------------------------------------

regions_dict = {
    'Makka': ['مكة المكرمة', 'الجموم', 'جدة'], 
    'Madinah': ['المدينة المنورة'],
    'Riyadh': ['الرياض', 'المزاحمية', 'الدرعية', 'حريملاء','مرات', "القويعية",
               'الخرج', 'الدلم','الزلفى', 'الغاط', 'المجمعه','جلاجل','حوطة سدير',
               'روضة سدير', 'الرين','الافلاج', 'السليل'],
    'Eastern': ['الدمام', 'الخبر', 'القطيف', 'الاحساء', 'الجبيل','النعيرية',
                'ابقيق','راس تنوره', 'الخفجي',"حفر الباطن", "القيصومة"],
    'Qasim': ['بريدة','رياض الخبراء','عنيزة','الرس','البكيرية','البدائع','البطين', 
              'الخبراء والسحابين','عيون الجواء','القوارة'],
    "Hael":["حائل"]
}

geoActions = {
    'البيانات الجيومكانية صحيحة': ['الجيومكانية صحيحة','الجيومكانية صحيحه','الجيومكانيه صحيحه','جيومكانية صحيحة'],
    'تعديل بيانات وصفية': ['بيانات وصفية','بيانات وصفيه','البيانات الوصفية','البيانات الوصفيه'],
    'تعديل أبعاد الأرض': ['أبعاد','ابعاد','تعديل أبعاد','تعديل ابعاد','تعديل الأبعاد','تعديل الابعاد'], 
    'تجزئة': ['تجزئة','التجزئة'], 
    'دمج': ['دمج','الدمج'], 
    'رفض': ["يعاد",'رفض','نقص','مرفوض',"مستندات","ارفاق","إرفاق",
            "غير صحيحة","الارض المختارة غير صحيحة"]
}

rejectionReasons = {
    'محضر الدمج/التجزئة': ['محضر','المحضر','المحضر المطلوب','محضر اللجنة الفنية'], 
    'إزدواجية صكوك': ['ازدواجية صكوك','إزدواجية صكوك','ازدواجيه','إزدواجيه صكوك'],
    "خطأ في بيانات الصك": ['خطأ في بيانات الصك','خطأ في الصك'],
    'صك الأرض': ['صك الأرض','صك الارض','صك','الصك'], 
    "إرفاق المؤشرات": ["مؤشرات","إرفاق كافه المؤشرات","ارفاق كافة المؤشرات","ارفاق كافه المؤشرات"],
    'طلب لوحدة عقارية': ['طلب لوحدة عقارية','وحدة','وحده','وحده عقارية','وحدة عقاريه','عقارية'], 
    'طلب مسجل مسبقاً': ['سابق','مسبقا','مسبقاً','مسبق','طلب آخر','مكرر','طلب تسجيل اول مكرر'], 
    'إختيار خاطئ': ['اختيار خاطئ','المختارة غير صحيحة','إختيار خاطئ','المختارة غير صحيحه'],
    "المخطط المعتمد": ["المخطط","مخطط"]
}

# ---------------------------------------------------------
# DB CONFIG
# ---------------------------------------------------------

odbc_params = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=0003-MAAL-01\\LASSQLSERVER;"
    "DATABASE=GRSDASHBOARD;"
    "UID=lasapp;"
    "PWD=lasapp@LAS123;"
)

odbc_connect_str = urllib.parse.quote_plus(odbc_params)
engine_postgres = create_engine("postgresql://app_user:app1234@10.150.40.74:5432/GSA")
engine_postgres2 = create_engine("postgresql://admin_user:admin1234@10.150.40.74:5432/GRS")


# ---------------------------------------------------------
# GUI LOGIC
# ---------------------------------------------------------

selected_file = None

def browse_file():
    global selected_file
    selected_file = filedialog.askopenfilename(
        title="Select Excel File",
        filetypes=[("Excel Files", "*.xlsx *.xlsm")]
    )
    if selected_file:
        log_box.insert(tk.END, f"Selected file: {selected_file}\n")


def run_process():
    if not selected_file:
        messagebox.showwarning("No File", "Please select an Excel file first.")
        return

    # ----- Loading window -----
    loading = tk.Toplevel(root)
    loading.title("Processing")
    loading.geometry("300x120")
    loading.resizable(False, False)
    tk.Label(loading, text="Processing… Please wait", font=("Arial", 12)).pack(pady=10)

    pb = ttk.Progressbar(loading, mode="indeterminate")
    pb.pack(fill="x", padx=20, pady=10)
    pb.start()

    loading.update()

    # ---- Run processing ----
    try:
        # Load Excel
        ops = load_excel(selected_file)
        log_box.insert(tk.END, "Excel loaded.\n")

        ops = ops.drop_duplicates(subset="Case Number")
        ops = ops[(ops['Geo Supervisor'].notnull()) & (ops['GEO S Completion'].notnull())]
        ops = ops.reset_index(drop=True)

        ops["UniqueKey"] = [
            f"{i}_{pd.to_datetime(j).round('s')}"
            for i, j in zip(ops["Case Number"], ops["GEO S Completion"])
        ]
        ops["UploadDate"] = datetime.now().date()#-timedelta(days=1)
        ops["UploadedBy"] = os.getlogin()

        ops = convert_to_date(ops)
        ops = getGeoAction(ops)

        editorlist = pd.read_sql('SELECT * FROM public."EditorsList"', engine_postgres)
        editorlist = convert_to_date(editorlist)

        ops_joined = join_userlist(ops, editorlist)
        ops_final = ops_joined[ops_joined["ListDate"].notna()]

        log_box.insert(tk.END, f"Valid cases: {len(ops_final)}\nUploading...\n")
        with engine_postgres2.begin() as conn:
            conn.execute(text("""DELETE FROM evaluation."OpsData" """))

        ops_final.to_sql("OpsData", engine_postgres2,
                         schema="evaluation", if_exists="append", index=False)

        log_box.insert(tk.END, "Upload complete.\n")

    except Exception as e:
        messagebox.showerror("Error", str(e))
        log_box.insert(tk.END, f"Error: {e}\n")

    finally:
        pb.stop()
        loading.destroy()


# ---------------------------------------------------------
# GUI LAYOUT
# ---------------------------------------------------------

root = tk.Tk()
root.title("Update Ops Data")
root.geometry("650x400")
root.configure(bg="#E6EDF4")

icon_path = os.path.dirname(os.path.abspath(__file__)) + r"\Logo_icon.ico"
if not os.path.exists(icon_path):
    icon_path = r"\\10.150.40.49\las\Ayman\Tools & Apps\Data For Tools\Icons\Logo_icon.ico"

root.iconbitmap(icon_path)

tk.Label(root, text="Update Op Data",
         font=("Cairo", 16, 'bold'), bg='#0A3556', fg='white').pack(pady=15, fill='both')

btn_select = tk.Button(root, text="Select Excel File", font=("Cairo", 12), bg='#0A3556', fg='white',
                       command=browse_file)
btn_select.pack(pady=5)

log_box = tk.Text(root, height=10, width=75, bg="#C5C4C4")
log_box.pack(pady=10)

btn_run = tk.Button(root, text="Run Process", font=("Cairo", 12), bg='#0A3556', fg='white',
                    command=run_process)
btn_run.pack(pady=5, anchor='e', padx=21)

root.mainloop()
