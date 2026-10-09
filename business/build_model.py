"""Builds the JS Contracting & Electrical Services 3-year financial model (openpyxl, formulas only)."""
import sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter as L
from openpyxl.comments import Comment

OUT = sys.argv[1]
wb = Workbook()

ARIAL = "Arial"
BLUE = Font(name=ARIAL, color="0000FF", size=10)
BLACK = Font(name=ARIAL, color="000000", size=10)
GREEN = Font(name=ARIAL, color="008000", size=10)
BOLD = Font(name=ARIAL, bold=True, size=10)
H1 = Font(name=ARIAL, bold=True, size=14)
H2 = Font(name=ARIAL, bold=True, size=11, color="FFFFFF")
NOTE = Font(name=ARIAL, italic=True, size=9, color="555555")
YELLOW = PatternFill("solid", fgColor="FFFF00")
NAVY = PatternFill("solid", fgColor="0B1F3F")
GREY = PatternFill("solid", fgColor="E6EBF2")
thin = Side(style="thin", color="B0B8C4")
TOPLINE = Border(top=Side(style="thin", color="000000"))
CUR = '$#,##0;($#,##0);"-"'
CUR2 = '$#,##0.00;($#,##0.00);"-"'
PCT = '0.0%;(0.0%);"-"'
NUM = '#,##0.0;(#,##0.0);"-"'
INT = '#,##0;(#,##0);"-"'

def hdr(ws, row, text, width=None):
    c = ws.cell(row=row, column=1, value=text); c.font = H2; c.fill = NAVY
    for col in range(2, (width or 8) + 1):
        ws.cell(row=row, column=col).fill = NAVY

def put(ws, ref, value, font=BLACK, fmt=None, fill=None, bold=False):
    c = ws[ref]; c.value = value; c.font = Font(name=ARIAL, bold=bold, size=10, color=font.color)
    if fmt: c.number_format = fmt
    if fill: c.fill = fill
    return c

def inp(ws, ref, value, fmt=None, key=False, note=None):
    c = put(ws, ref, value, BLUE, fmt, YELLOW if key else None)
    if note: c.comment = Comment(note, "Model")
    return c

# ===========================================================================
# Assumptions
# ===========================================================================
A = wb.active; A.title = "Assumptions"
A.column_dimensions["A"].width = 44; A.column_dimensions["B"].width = 16
for col in "CDEFGHIJKLMN": A.column_dimensions[col].width = 11
A["A1"] = "JS Contracting & Electrical Services: financial model assumptions"; A["A1"].font = H1
A["A2"] = "Blue cells are inputs; yellow cells are the key levers. Black cells are formulas. Every other sheet is driven from here. Month 1 is the first month of operations."; A["A2"].font = NOTE
A["A3"] = "Figures are planning assumptions set from the market research in business/research (October 2026) and should be replaced by the owner's own numbers."; A["A3"].font = NOTE

hdr(A, 5, "Service lines (year 1 run rate; months 1 to 6 ramp up via the seasonal factors)", 8)
for i, h in enumerate(["Service line", "Jobs per month at run rate", "Average ticket ($)", "Materials, equipment and subs (% of price)", "Revenue per month at run rate ($)", "Source / note"]):
    c = A.cell(row=6, column=i + 1, value=h); c.font = BOLD; c.fill = GREY; c.alignment = Alignment(wrap_text=True, vertical="top")
A.row_dimensions[6].height = 42
LINES = [
    ("Service calls and repairs", 14, 350, 0.20, "First-hour $175 to $250 then hourly; MA service fees $75 to $175 (HomeGuide Lowell)"),
    ("Panel upgrades and service changes", 2, 4200, 0.35, "JS price $3,000 to $6,000; MA market $2,500 to $8,000, avg about $4,000 (EngineerFix)"),
    ("EV charger installations", 2.5, 1600, 0.30, "JS $900 to $2,500 wiring; MA installed $1,200 to $3,000 (NuWatt); charger supplied on some jobs"),
    ("Standby generators", 0.4, 14000, 0.58, "20 to 26 kW with transfer switch; Boston area $12,000 to $22,000 (ConsumerAffairs); unit and ATS are most of the cost"),
    ("Generator inlets and interlocks", 0.8, 1300, 0.35, "JS $900 to $1,800"),
    ("Lighting and fans", 3, 1100, 0.35, "Six-light kitchen $1,200 to $2,000; fan $200 to $450"),
    ("Remodel contracting", 0.12, 35000, 0.60, "Basement, kitchen or bath at fixed price; subs and materials about 60%"),
]
LINE_ROWS = []
for i, (name, jobs, ticket, cost, note) in enumerate(LINES):
    r = 7 + i; LINE_ROWS.append(r)
    put(A, f"A{r}", name)
    inp(A, f"B{r}", jobs, NUM, key=True); inp(A, f"C{r}", ticket, CUR, key=True); inp(A, f"D{r}", cost, PCT)
    put(A, f"E{r}", f"=B{r}*C{r}", fmt=CUR); put(A, f"F{r}", note, NOTE)
rT = 7 + len(LINES)
put(A, f"A{rT}", "Total at run rate", bold=True); put(A, f"B{rT}", f"=SUM(B7:B{rT-1})", fmt=NUM, bold=True); put(A, f"E{rT}", f"=SUM(E7:E{rT-1})", fmt=CUR, bold=True)
put(A, f"D{rT}", f"=IF(E{rT}=0,0,SUMPRODUCT(D7:D{rT-1},E7:E{rT-1})/E{rT})", fmt=PCT); A[f"F{rT}"] = "Blended material cost share"; A[f"F{rT}"].font = NOTE

hdr(A, 16, "Growth and pricing", 8)
put(A, "A17", "Price increase, year 2 (applies to all tickets)"); inp(A, "B17", 0.03, PCT)
put(A, "A18", "Price increase, year 3"); inp(A, "B18", 0.03, PCT)
put(A, "A19", "Volume growth of the base lines, year 2 (owner + apprentice efficiency, referrals)"); inp(A, "B19", 0.12, PCT, key=True)
put(A, "A20", "Volume growth of the base lines, year 3"); inp(A, "B20", 0.06, PCT, key=True)
put(A, "A21", "Revenue added per journeyman at full productivity ($ per month)"); inp(A, "B21", 17000, CUR, key=True, note="About $204k a year per journeyman: 1,250 billable hours at $150 plus materials. Benchmark $207k to $400k revenue per technician (Simpro, BuildOps).")
put(A, "A22", "Material and sub cost on journeyman revenue (% of price)"); inp(A, "B22", 0.35, PCT)
put(A, "A23", "Journeyman ramp: month 1 of hire at 50%, month 2 at 75%, full from month 3", NOTE)

hdr(A, 25, "Seasonality (multiplies run-rate revenue; year 1 row includes the start-up ramp)", 14)
put(A, "A26", "Month of year"); 
for m in range(12): put(A, f"{L(3+m)}26", m + 1, bold=True)
put(A, "A27", "Year 1 factor (ramp plus seasons)"); 
for m, v in enumerate([0.45, 0.55, 0.65, 0.80, 0.90, 1.00, 1.10, 1.10, 1.00, 1.10, 1.00, 0.85]): inp(A, f"{L(3+m)}27", v, NUM)
put(A, "A28", "Years 2 and 3 factor (seasons only, averages 1.0)")
for m, v in enumerate([0.75, 0.80, 0.90, 1.00, 1.10, 1.15, 1.15, 1.10, 1.05, 1.10, 1.00, 0.90]): inp(A, f"{L(3+m)}28", v, NUM)
put(A, "B27", "=AVERAGE(C27:N27)", fmt=NUM); put(A, "B28", "=AVERAGE(C28:N28)", fmt=NUM); A["B26"] = "Average"; A["B26"].font = BOLD
A["A29"] = "Winter trough January and February, peak June to August, rebate-deadline push in October (TCNECA, ServiceTitan seasonality data)."; A["A29"].font = NOTE

hdr(A, 31, "Staffing", 8)
for i, h in enumerate(["Role", "Hourly wage ($)", "Start month", "Hours per month", "Burden (payroll tax, workers comp, PTO)", "Annual raise"]):
    c = A.cell(row=32, column=i + 1, value=h); c.font = BOLD; c.fill = GREY; c.alignment = Alignment(wrap_text=True, vertical="top")
A.row_dimensions[32].height = 42
STAFF = [("Apprentice (registered, works 1:1 with a licensed electrician)", 24, 2), ("Journeyman electrician 1", 40, 16), ("Journeyman electrician 2 (second van)", 40, 28)]
for i, (role, wage, start) in enumerate(STAFF):
    r = 33 + i
    put(A, f"A{r}", role); inp(A, f"B{r}", wage, CUR2, key=True); inp(A, f"C{r}", start, INT, key=True); inp(A, f"D{r}", 173.33, NUM); inp(A, f"E{r}", 0.15, PCT); inp(A, f"F{r}", 0.03, PCT)
A["A36"] = "Boston journeyman median $38.59 per hour (PayScale 2026); MA electrician median wage about $80k (BLS OEWS). Burden: FICA 7.65% + MA workers comp class 5190 about 1.5% + PTO and training."; A["A36"].font = NOTE
put(A, "A37", "Owner draw per month, months 1 to 3 ($)"); inp(A, "B37", 4000, CUR, key=True)
put(A, "A38", "Owner draw per month, months 4 to 6 ($)"); inp(A, "B38", 6000, CUR, key=True)
put(A, "A39", "Owner draw per month, months 7 to 12 ($)"); inp(A, "B39", 7000, CUR, key=True)
put(A, "A40", "Owner draw per month, year 2 ($)"); inp(A, "B40", 7500, CUR, key=True)
put(A, "A41", "Owner draw per month, year 3 ($)"); inp(A, "B41", 8333, CUR, key=True)
put(A, "A42", "Office help from month 4 ($ per month, about 10 hours a week)"); inp(A, "B42", 500, CUR); inp(A, "C42", 4, INT)

hdr(A, 44, "Overhead ($ per month unless noted)", 8)
OVH = [("Field-service software (Jobber Connect or Housecall Pro Essentials)", 150), ("Accounting software (QuickBooks Online Essentials)", 80),
       ("Google Workspace and business phone (VoIP)", 60), ("Cell and data, two lines", 110), ("Bookkeeper", 400), ("CPA (annual $1,500 spread monthly)", 125),
       ("Licenses, continuing education, chamber dues", 60), ("Tool replacement and small equipment", 200), ("Uniforms and PPE", 60),
       ("Office supplies and misc", 100), ("Storage unit or yard space", 150)]
OVH_ROWS = []
for i, (name, v) in enumerate(OVH):
    r = 45 + i; OVH_ROWS.append(r); put(A, f"A{r}", name); inp(A, f"B{r}", v, CUR)
rO = 45 + len(OVH)
put(A, f"A{rO}", "Fixed overhead per month, before vehicles and insurance", bold=True); put(A, f"B{rO}", f"=SUM(B45:B{rO-1})", fmt=CUR, bold=True)
put(A, f"A{rO+1}", "Overhead inflation per year"); inp(A, f"B{rO+1}", 0.03, PCT)
R_OVH_TOTAL, R_INFL = rO, rO + 1

r = rO + 3
hdr(A, r, "Vehicles", 8); R_VEH = r + 1
put(A, f"A{r+1}", "Van 1 purchase price ($, used 2021 to 2023 Transit or ProMaster)"); inp(A, f"B{r+1}", 36000, CUR, key=True)
put(A, f"A{r+2}", "Van 1 down payment ($)"); inp(A, f"B{r+2}", 6000, CUR)
put(A, f"A{r+3}", "Van loan interest rate (annual)"); inp(A, f"B{r+3}", 0.09, PCT)
put(A, f"A{r+4}", "Van loan term (months)"); inp(A, f"B{r+4}", 60, INT)
put(A, f"A{r+5}", "Van loan payment ($ per month)"); put(A, f"B{r+5}", f"=-PMT(B{r+3}/12,B{r+4},B{r+1}-B{r+2})", fmt=CUR)
put(A, f"A{r+6}", "Depreciation per van ($ per month, 5-year straight line)"); put(A, f"B{r+6}", f"=B{r+1}/60", fmt=CUR)
put(A, f"A{r+7}", "Fuel per van ($ per month)"); inp(A, f"B{r+7}", 450, CUR)
put(A, f"A{r+8}", "Maintenance and tires per van ($ per month)"); inp(A, f"B{r+8}", 150, CUR)
put(A, f"A{r+9}", "Van 2 purchased in month (same price and terms as van 1)"); inp(A, f"B{r+9}", 28, INT, key=True)
A[f"A{r+10}"] = "Used-van pricing from CarGurus and TrueCar averages; financing 5 to 15% APR market (Crestmont Capital)."; A[f"A{r+10}"].font = NOTE
V = {"price": f"Assumptions!$B${r+1}", "down": f"Assumptions!$B${r+2}", "rate": f"Assumptions!$B${r+3}", "term": f"Assumptions!$B${r+4}",
     "pmt": f"Assumptions!$B${r+5}", "dep": f"Assumptions!$B${r+6}", "fuel": f"Assumptions!$B${r+7}", "maint": f"Assumptions!$B${r+8}", "van2": f"Assumptions!$B${r+9}"}

r = r + 12
hdr(A, r, "Insurance ($ per year)", 8)
put(A, f"A{r+1}", "General liability, $1M per occurrence / $2M aggregate"); inp(A, f"B{r+1}", 900, CUR)
put(A, f"A{r+2}", "Commercial auto, per van"); inp(A, f"B{r+2}", 2000, CUR)
put(A, f"A{r+3}", "Workers compensation rate, MA class 5190 (per $1 of payroll)"); inp(A, f"B{r+3}", 0.01475, '0.000%', note="WCRIBMA rate $1.475 per $100 of payroll effective 7/1/2024; subject to revision.")
put(A, f"A{r+4}", "Tools and equipment (inland marine)"); inp(A, f"B{r+4}", 400, CUR)
put(A, f"A{r+5}", "Umbrella, $1M"); inp(A, f"B{r+5}", 1000, CUR)
put(A, f"A{r+6}", "Fixed insurance per month, one van"); put(A, f"B{r+6}", f"=(B{r+1}+B{r+2}+B{r+4}+B{r+5})/12", fmt=CUR)
A[f"A{r+7}"] = "Insureon medians for electricians: GL $684, auto $1,682, tools $169 to $494 per year. Workers comp is computed from payroll in the Monthly sheet."; A[f"A{r+7}"].font = NOTE
INS = {"gl": f"Assumptions!$B${r+1}", "auto": f"Assumptions!$B${r+2}", "wc": f"Assumptions!$B${r+3}", "fixed_mo": f"Assumptions!$B${r+6}"}

r = r + 9
hdr(A, r, "Marketing", 14)
put(A, f"A{r+1}", "Year 1 spend by month ($)")
for m, v in enumerate([6000, 3200, 2600, 2300, 2300, 2300, 2100, 2100, 2000, 2000, 1900, 1700]): inp(A, f"{L(3+m)}{r+1}", v, CUR, key=True)
put(A, f"B{r+1}", f"=SUM(C{r+1}:N{r+1})", fmt=CUR)
put(A, f"A{r+2}", "Year 2 marketing (% of revenue)"); inp(A, f"B{r+2}", 0.08, PCT, key=True)
put(A, f"A{r+3}", "Year 3 marketing (% of revenue)"); inp(A, f"B{r+3}", 0.07, PCT, key=True)
A[f"A{r+4}"] = "Month 1 includes the van wrap, citations and launch; Local Services Ads $1,000 to $1,500 a month from month 2 or 3. Home-services benchmark 5 to 12% of revenue."; A[f"A{r+4}"].font = NOTE
MK = {"y1row": r + 1, "y2": f"Assumptions!$B${r+2}", "y3": f"Assumptions!$B${r+3}"}

r = r + 6
hdr(A, r, "Collections and fees", 8)
put(A, f"A{r+1}", "Card and bank fees (% of revenue)"); inp(A, f"B{r+1}", 0.015, PCT)
put(A, f"A{r+2}", "Revenue collected in the month of the job (%)"); inp(A, f"B{r+2}", 0.90, PCT)
put(A, f"A{r+3}", "Revenue collected the following month (%)"); put(A, f"B{r+3}", f"=1-B{r+2}", fmt=PCT)
put(A, f"A{r+4}", "Materials paid in the month of the job (%; supply houses on net-30 shift the rest)"); inp(A, f"B{r+4}", 1.0, PCT)
put(A, f"A{r+5}", "Line of credit available ($, undrawn)"); inp(A, f"B{r+5}", 25000, CUR)
A[f"A{r+6}"] = "Residential service and installs are paid at completion by card or bank transfer; deposits on installs are capped at one-third under MA home-improvement law."; A[f"A{r+6}"].font = NOTE
FEES = {"card": f"Assumptions!$B${r+1}", "col_now": f"Assumptions!$B${r+2}", "col_next": f"Assumptions!$B${r+3}", "loc": f"Assumptions!$B${r+5}"}

# ===========================================================================
# Startup costs
# ===========================================================================
S = wb.create_sheet("Startup Costs")
S.column_dimensions["A"].width = 50
for col in "BCD": S.column_dimensions[col].width = 14
S.column_dimensions["E"].width = 60
S["A1"] = "Startup costs and sources of funds"; S["A1"].font = H1
S["A2"] = "Low and high are researched 2025 to 2026 price ranges; Plan is the budget used in the model. Edit the Plan column."; S["A2"].font = NOTE
for i, h in enumerate(["Item", "Low ($)", "High ($)", "Plan ($)", "Basis"]):
    c = S.cell(row=4, column=i + 1, value=h); c.font = BOLD; c.fill = GREY
ITEMS = [
    ("Work van, used 2021 to 2023 (financed; see Vehicles)", 34000, 43000, f"={V['price']}", "CarGurus and TrueCar used-van averages; financed with the down payment below"),
    ("Van upfit: shelving, partition, ladder rack", 2500, 6500, 4000, "Ranger Design and Adrian Steel packages; DIY builds about $2,500"),
    ("Vehicle wrap or lettering", 1200, 7500, 3000, "Partial wrap $1,200 to $3,500; full wrap to $7,500"),
    ("Hand and power tools (top-up; owner keeps his own)", 1000, 12000, 4500, "Jobber tool list $1,000 to $2,800; pro kits to $12,000"),
    ("Test equipment: multimeter, clamp meter, insulation tester", 1500, 4000, 2500, "Fluke 87V about $500; Fluke 1587 about $1,250; clamp $600 to $1,150"),
    ("Ladders, bender, fish tapes", 520, 1320, 900, "28-ft fiberglass $420 to $920; bender and tapes $100 to $400"),
    ("Initial parts and wire inventory", 4000, 7000, 5000, "Stocked service van carries $5,000 to $7,000"),
    ("Tablet, laptop and phone", 600, 3500, 1800, "iPad plus case, or a rugged tablet"),
    ("Software setup and first two months", 300, 1200, 600, "Jobber or Housecall Pro, QuickBooks, Workspace, VoIP"),
    ("Uniforms and PPE", 300, 800, 600, "Embroidered shirts about $26.50 each"),
    ("Domain, hosting, listings (website already built)", 200, 1500, 600, "Netlify free tier; domain; citation listings"),
    ("Licenses and registrations: LLC, HIC and Guaranty Fund, CSL, DBA", 900, 1300, 1100, "LLC $500; HIC $150 + $100 fund; CSL $150 + exam; DBA $25 to $65"),
    ("Insurance down payments (about 25% of the annual program)", 1000, 2500, 1400, "GL, auto, workers comp, tools, umbrella about $5,500 a year"),
    ("Legal: entity, HIC-compliant contract templates, review of the S&T sale terms", 1500, 4000, 2500, "Attorney at $300 to $450 per hour"),
    ("Accounting setup (chart of accounts, payroll, S-corp election)", 300, 800, 500, "Bookkeeper and CPA onboarding"),
    ("Yard signs, door hangers, business cards", 400, 1200, 800, "Brand package is complete; print only"),
    ("Working capital reserve (covers the slow first months)", 15000, 40000, 30000, "About three months of overhead plus owner draw at the reduced early rate"),
]
for i, (name, lo, hi, plan, basis) in enumerate(ITEMS):
    r = 5 + i
    put(S, f"A{r}", name); inp(S, f"B{r}", lo, CUR); inp(S, f"C{r}", hi, CUR)
    if isinstance(plan, str): put(S, f"D{r}", plan, GREEN, CUR)
    else: inp(S, f"D{r}", plan, CUR, key=True)
    put(S, f"E{r}", basis, NOTE)
rS = 5 + len(ITEMS)
put(S, f"A{rS}", "Total startup uses", bold=True)
for col in "BCD": put(S, f"{col}{rS}", f"=SUM({col}5:{col}{rS-1})", fmt=CUR, bold=True); S[f"{col}{rS}"].border = TOPLINE
R_USES = rS
rr = rS + 2
put(S, f"A{rr}", "Sources of funds", bold=True); S[f"A{rr}"].fill = GREY; S[f"D{rr}"].fill = GREY; S[f"D{rr}"] = "Plan ($)"; S[f"D{rr}"].font = BOLD
put(S, f"A{rr+1}", "Van loan (purchase price less down payment)"); put(S, f"D{rr+1}", f"={V['price']}-{V['down']}", GREEN, CUR)
put(S, f"A{rr+2}", "Owner cash injection from the S&T Electrical sale proceeds"); put(S, f"D{rr+2}", f"=D{rS}-D{rr+1}", fmt=CUR)
put(S, f"A{rr+3}", "Line of credit, arranged but undrawn (seasonal buffer)"); put(S, f"D{rr+3}", f"={FEES['loc']}", GREEN, CUR)
put(S, f"A{rr+4}", "Total sources used at launch", bold=True); put(S, f"D{rr+4}", f"=D{rr+1}+D{rr+2}", fmt=CUR, bold=True); S[f"D{rr+4}"].border = TOPLINE
put(S, f"A{rr+5}", "Owner injection as a share of uses (lenders look for 10 to 20% minimum)"); put(S, f"D{rr+5}", f"=IF(D{rS}=0,0,D{rr+2}/D{rS})", fmt=PCT)
R_OWNER_INJ = rr + 2; R_RESERVE = 5 + len(ITEMS) - 1

# ===========================================================================
# Monthly (36 months)
# ===========================================================================
M = wb.create_sheet("Monthly")
M.column_dimensions["A"].width = 46; M.column_dimensions["B"].width = 10
NM = 36
for m in range(NM): M.column_dimensions[L(3 + m)].width = 10.5
M.freeze_panes = "C5"
M["A1"] = "Monthly projection, months 1 to 36 (P&L and cash flow)"; M["A1"].font = H1
M["A2"] = "All cells are formulas driven by the Assumptions sheet. Month 1 is the first month of operations."; M["A2"].font = NOTE
put(M, "A3", "Year", bold=True); put(M, "A4", "Month", bold=True)
cols = [L(3 + m) for m in range(NM)]
for m, c in enumerate(cols):
    put(M, f"{c}4", m + 1, bold=True); M[f"{c}4"].fill = GREY
    put(M, f"{c}3", f"=IF({c}4<=12,1,IF({c}4<=24,2,3))", fmt=INT, bold=True); M[f"{c}3"].fill = GREY

row = 5
def label(r, text, bold=False, unit=""):
    put(M, f"A{r}", text, bold=bold); 
    if unit: put(M, f"B{r}", unit, NOTE)
def line(r, text, fmt, expr, bold=False, unit="$", font=BLACK, border=False):
    label(r, text, bold, unit)
    for m, c in enumerate(cols):
        e = expr(c, m)
        cell = put(M, f"{c}{r}", e, font, fmt, bold=bold)
        if border: cell.border = TOPLINE

# factors
R_SEAS, R_VOL, R_PRICE = 6, 7, 8
label(5, "Factors", True)
line(R_SEAS, "Seasonal factor", NUM, lambda c, m: f"=IF({c}$3=1,INDEX(Assumptions!$C$27:$N$27,1,MOD({c}$4-1,12)+1),INDEX(Assumptions!$C$28:$N$28,1,MOD({c}$4-1,12)+1))", unit="x", font=GREEN)
line(R_VOL, "Base volume factor", NUM, lambda c, m: f"=IF({c}$3=1,1,IF({c}$3=2,1+Assumptions!$B$19,(1+Assumptions!$B$19)*(1+Assumptions!$B$20)))", unit="x", font=GREEN)
line(R_PRICE, "Price factor", NUM, lambda c, m: f"=IF({c}$3=1,1,IF({c}$3=2,1+Assumptions!$B$17,(1+Assumptions!$B$17)*(1+Assumptions!$B$18)))", unit="x", font=GREEN)

# revenue
label(10, "Revenue", True)
REV_ROWS = []
for i, lr in enumerate(LINE_ROWS):
    r = 11 + i; REV_ROWS.append(r)
    line(r, LINES[i][0], CUR, lambda c, m, lr=lr: f"=Assumptions!$B${lr}*Assumptions!$C${lr}*{c}${R_SEAS}*{c}${R_VOL}*{c}${R_PRICE}")
R_J1REV = 11 + len(LINE_ROWS); R_J2REV = R_J1REV + 1
line(R_J1REV, "Journeyman 1 added revenue", CUR, lambda c, m: f"=IF({c}$4<Assumptions!$C$34,0,Assumptions!$B$21*MIN(1,0.5+0.25*({c}$4-Assumptions!$C$34))*{c}${R_SEAS}*{c}${R_PRICE})")
line(R_J2REV, "Journeyman 2 added revenue", CUR, lambda c, m: f"=IF({c}$4<Assumptions!$C$35,0,Assumptions!$B$21*MIN(1,0.5+0.25*({c}$4-Assumptions!$C$35))*{c}${R_SEAS}*{c}${R_PRICE})")
R_REV = R_J2REV + 1
line(R_REV, "Total revenue", CUR, lambda c, m: f"=SUM({c}11:{c}{R_J2REV})", bold=True, border=True)

# jobs
R_JOBS = R_REV + 1
line(R_JOBS, "Jobs completed (base lines)", NUM, lambda c, m: "=" + "+".join(f"Assumptions!$B${lr}*{c}${R_SEAS}*{c}${R_VOL}" for lr in LINE_ROWS), unit="#")

# cost of sales
R_COGS0 = R_JOBS + 2
label(R_COGS0, "Materials, equipment and subcontractors", True)
COGS_ROWS = []
for i, lr in enumerate(LINE_ROWS):
    r = R_COGS0 + 1 + i; COGS_ROWS.append(r)
    line(r, LINES[i][0], CUR, lambda c, m, lr=lr, rr=REV_ROWS[i]: f"={c}{rr}*Assumptions!$D${lr}")
R_JCOGS = R_COGS0 + 1 + len(LINE_ROWS)
line(R_JCOGS, "On journeyman revenue", CUR, lambda c, m: f"=({c}{R_J1REV}+{c}{R_J2REV})*Assumptions!$B$22")
R_COGS = R_JCOGS + 1
line(R_COGS, "Total materials, equipment and subs", CUR, lambda c, m: f"=SUM({c}{R_COGS0+1}:{c}{R_JCOGS})", bold=True, border=True)
R_GP = R_COGS + 1
line(R_GP, "Gross profit after materials", CUR, lambda c, m: f"={c}{R_REV}-{c}{R_COGS}", bold=True)
R_GPM = R_GP + 1
line(R_GPM, "Gross margin after materials", PCT, lambda c, m: f"=IF({c}{R_REV}=0,0,{c}{R_GP}/{c}{R_REV})", unit="%")

# direct labor
R_LAB0 = R_GPM + 2
label(R_LAB0, "Field labor (wages plus burden)", True)
R_APP, R_J1, R_J2 = R_LAB0 + 1, R_LAB0 + 2, R_LAB0 + 3
line(R_APP, "Apprentice", CUR, lambda c, m: f"=IF({c}$4<Assumptions!$C$33,0,Assumptions!$B$33*Assumptions!$D$33*(1+Assumptions!$E$33)*(1+Assumptions!$F$33)^({c}$3-1))")
line(R_J1, "Journeyman 1", CUR, lambda c, m: f"=IF({c}$4<Assumptions!$C$34,0,Assumptions!$B$34*Assumptions!$D$34*(1+Assumptions!$E$34)*(1+Assumptions!$F$34)^({c}$3-1))")
line(R_J2, "Journeyman 2", CUR, lambda c, m: f"=IF({c}$4<Assumptions!$C$35,0,Assumptions!$B$35*Assumptions!$D$35*(1+Assumptions!$E$35)*(1+Assumptions!$F$35)^({c}$3-1))")
R_LAB = R_J2 + 1
line(R_LAB, "Total field labor", CUR, lambda c, m: f"=SUM({c}{R_APP}:{c}{R_J2})", bold=True, border=True)
R_GP2 = R_LAB + 1
line(R_GP2, "Gross profit after labor", CUR, lambda c, m: f"={c}{R_GP}-{c}{R_LAB}", bold=True)

# overhead
R_OV0 = R_GP2 + 2
label(R_OV0, "Operating expenses", True)
R_FIX = R_OV0 + 1
line(R_FIX, "Fixed overhead (software, phone, bookkeeping, tools, misc)", CUR, lambda c, m: f"=Assumptions!$B${R_OVH_TOTAL}*(1+Assumptions!$B${R_INFL})^({c}$3-1)")
R_OFF = R_FIX + 1
line(R_OFF, "Office help", CUR, lambda c, m: f"=IF({c}$4<Assumptions!$C$42,0,Assumptions!$B$42*(1+Assumptions!$B${R_INFL})^({c}$3-1))")
R_VANS = R_OFF + 1
line(R_VANS, "Vans in service", INT, lambda c, m: f"=1+IF({c}$4>={V['van2']},1,0)", unit="#")
R_FUEL = R_VANS + 1
line(R_FUEL, "Fuel, maintenance and tires", CUR, lambda c, m: f"={c}{R_VANS}*({V['fuel']}+{V['maint']})*(1+Assumptions!$B${R_INFL})^({c}$3-1)")
R_INSF = R_FUEL + 1
line(R_INSF, "Insurance: liability, auto, tools, umbrella", CUR, lambda c, m: f"=({INS['fixed_mo']}+({c}{R_VANS}-1)*{INS['auto']}/12)*(1+Assumptions!$B${R_INFL})^({c}$3-1)")
R_WC = R_INSF + 1
line(R_WC, "Workers compensation (on field payroll)", CUR, lambda c, m: f"=({c}{R_LAB}/1.15)*{INS['wc']}")
R_MKT = R_WC + 1
line(R_MKT, "Marketing", CUR, lambda c, m: f"=IF({c}$3=1,INDEX(Assumptions!$C${MK['y1row']}:$N${MK['y1row']},1,{c}$4),IF({c}$3=2,{c}{R_REV}*{MK['y2']},{c}{R_REV}*{MK['y3']}))")
R_FEE = R_MKT + 1
line(R_FEE, "Card and bank fees", CUR, lambda c, m: f"={c}{R_REV}*{FEES['card']}")
R_DEP = R_FEE + 1
line(R_DEP, "Depreciation (vans)", CUR, lambda c, m: f"={c}{R_VANS}*{V['dep']}")
R_INT = R_DEP + 1
line(R_INT, "Interest on van loans", CUR, lambda c, m: f"=-IPMT({V['rate']}/12,{c}$4,{V['term']},{V['price']}-{V['down']})*IF({c}$4<={V['term']},1,0)-IF({c}$4>={V['van2']},IPMT({V['rate']}/12,{c}$4-{V['van2']}+1,{V['term']},{V['price']}-{V['down']}),0)")
R_OPEX = R_INT + 1
line(R_OPEX, "Total operating expenses", CUR, lambda c, m: f"=SUM({c}{R_FIX}:{c}{R_OFF})+SUM({c}{R_FUEL}:{c}{R_INT})", bold=True, border=True)
R_EBIT0 = R_OPEX + 1
line(R_EBIT0, "Operating profit before owner compensation", CUR, lambda c, m: f"={c}{R_GP2}-{c}{R_OPEX}", bold=True)
R_OWN = R_EBIT0 + 1
line(R_OWN, "Owner draw (salary)", CUR, lambda c, m: f"=IF({c}$3=1,IF({c}$4<=3,Assumptions!$B$37,IF({c}$4<=6,Assumptions!$B$38,Assumptions!$B$39)),IF({c}$3=2,Assumptions!$B$40,Assumptions!$B$41))")
R_NET = R_OWN + 1
line(R_NET, "Net profit before tax", CUR, lambda c, m: f"={c}{R_EBIT0}-{c}{R_OWN}", bold=True, border=True)
R_NETM = R_NET + 1
line(R_NETM, "Net margin", PCT, lambda c, m: f"=IF({c}{R_REV}=0,0,{c}{R_NET}/{c}{R_REV})", unit="%")

# cash flow
R_CF0 = R_NETM + 2
label(R_CF0, "Cash flow", True)
R_COLL = R_CF0 + 1
line(R_COLL, "Collections from customers", CUR, lambda c, m: f"={c}{R_REV}*{FEES['col_now']}" + (f"+{cols[m-1]}{R_REV}*{FEES['col_next']}" if m > 0 else ""))
R_CPAY = R_COLL + 1
line(R_CPAY, "Materials, equipment and subs paid", CUR, lambda c, m: f"={c}{R_COGS}")
R_CLAB = R_CPAY + 1
line(R_CLAB, "Field labor paid", CUR, lambda c, m: f"={c}{R_LAB}")
R_COPX = R_CLAB + 1
line(R_COPX, "Operating expenses paid (excluding depreciation and interest)", CUR, lambda c, m: f"={c}{R_OPEX}-{c}{R_DEP}-{c}{R_INT}")
R_CVAN = R_COPX + 1
line(R_CVAN, "Van loan payments (principal and interest)", CUR, lambda c, m: f"={V['pmt']}*IF({c}$4<={V['term']},1,0)+IF({c}$4>={V['van2']},{V['pmt']},0)")
R_CVAN2 = R_CVAN + 1
line(R_CVAN2, "Van 2 down payment", CUR, lambda c, m: f"=IF({c}$4={V['van2']},{V['down']},0)")
R_COWN = R_CVAN2 + 1
line(R_COWN, "Owner draw", CUR, lambda c, m: f"={c}{R_OWN}")
R_NCF = R_COWN + 1
line(R_NCF, "Net cash flow", CUR, lambda c, m: f"={c}{R_COLL}-{c}{R_CPAY}-{c}{R_CLAB}-{c}{R_COPX}-{c}{R_CVAN}-{c}{R_CVAN2}-{c}{R_COWN}", bold=True, border=True)
R_OPEN = R_NCF + 1
line(R_OPEN, "Opening cash", CUR, lambda c, m: (f"='Startup Costs'!$D${R_RESERVE}" if m == 0 else f"={cols[m-1]}{R_OPEN+1}"), font=GREEN)
R_CLOSE = R_OPEN + 1
line(R_CLOSE, "Ending cash", CUR, lambda c, m: f"={c}{R_OPEN}+{c}{R_NCF}", bold=True)
M[f"A{R_OPEN}"].comment = Comment("Month 1 opens with the working-capital reserve from the Startup Costs sheet; all other startup purchases are made before month 1.", "Model")

# ===========================================================================
# Annual summary
# ===========================================================================
Y = wb.create_sheet("Annual Summary", 1)
Y.column_dimensions["A"].width = 50
for col in "BCD": Y.column_dimensions[col].width = 16
Y.column_dimensions["E"].width = 50
Y["A1"] = "Three-year summary"; Y["A1"].font = H1
Y["A2"] = "Sums of the Monthly sheet by year. Net profit is after a market-rate owner salary (the owner draw)."; Y["A2"].font = NOTE
for i, h in enumerate(["", "Year 1", "Year 2", "Year 3", "Note"]):
    c = Y.cell(row=4, column=i + 1, value=h); c.font = BOLD; c.fill = GREY
def yrow(r, text, mrow, fmt=CUR, bold=False, kind="sum", note=""):
    put(Y, f"A{r}", text, bold=bold)
    for i, col in enumerate("BCD"):
        y = i + 1
        if kind == "sum": e = f"=SUMIFS(Monthly!$C${mrow}:$AL${mrow},Monthly!$C$3:$AL$3,{y})"
        elif kind == "last": e = f"=INDEX(Monthly!$C${mrow}:$AL${mrow},1,{12*y})"
        elif kind == "min": e = f"=MIN(INDEX(Monthly!$C${mrow}:$AL${mrow},1,{12*y-11}):INDEX(Monthly!$C${mrow}:$AL${mrow},1,{12*y}))"
        else: e = kind(col, y)
        put(Y, f"{col}{r}", e, GREEN if kind in ("sum", "last", "min") else BLACK, fmt, bold=bold)
    if note: put(Y, f"E{r}", note, NOTE)
yrow(5, "Revenue", R_REV, bold=True)
yrow(6, "Materials, equipment and subcontractors", R_COGS)
yrow(7, "Gross profit after materials", R_GP, bold=True)
yrow(8, "Gross margin after materials", None, PCT, kind=lambda col, y: f"=IF({col}5=0,0,{col}7/{col}5)", note="Benchmark 55%+ on residential service, 30 to 50% service-focused shops (Simpro, Lightning Path)")
yrow(9, "Field labor", R_LAB)
yrow(10, "Gross profit after labor", R_GP2, bold=True)
yrow(11, "Operating expenses (incl. marketing, depreciation, interest)", R_OPEX)
yrow(12, "of which marketing", R_MKT, note="Year 1 about 9 to 11% of revenue, then 8% and 7%")
yrow(13, "Operating profit before owner compensation", R_EBIT0, bold=True)
yrow(14, "Owner draw (salary)", R_OWN)
yrow(15, "Net profit before tax", R_NET, bold=True, note="After the owner's salary. Industry median net 5 to 6%, top quartile 10 to 12% (NECA via Simpro)")
yrow(16, "Net margin", None, PCT, kind=lambda col, y: f"=IF({col}5=0,0,{col}15/{col}5)")
yrow(17, "Owner's total take (draw plus net profit)", None, CUR, kind=lambda col, y: f"={col}14+{col}15", bold=True)
put(Y, "A19", "Operations", bold=True); Y["A19"].fill = GREY
yrow(20, "Jobs completed (base lines)", R_JOBS, INT)
yrow(21, "Average revenue per base job", None, CUR, kind=lambda col, y: f"=IF({col}20=0,0,({col}5-{col}24)/{col}20)")
yrow(22, "Vans in service at year end", R_VANS, INT, kind="last")
yrow(23, "Field people incl. owner at year end", None, INT, kind=lambda col, y: f"=1+IF(12*{y}>=Assumptions!$C$33,1,0)+IF(12*{y}>=Assumptions!$C$34,1,0)+IF(12*{y}>=Assumptions!$C$35,1,0)")
yrow(24, "Revenue added by journeymen", None, CUR, kind=lambda col, y: f"=SUMIFS(Monthly!$C${R_J1REV}:$AL${R_J1REV},Monthly!$C$3:$AL$3,{y})+SUMIFS(Monthly!$C${R_J2REV}:$AL${R_J2REV},Monthly!$C$3:$AL$3,{y})")
yrow(25, "Revenue per field person", None, CUR, kind=lambda col, y: f"=IF({col}23=0,0,{col}5/{col}23)", note="Benchmark $207k to $400k per technician; the owner spends about half his time off the tools")
put(Y, "A27", "Cash and debt", bold=True); Y["A27"].fill = GREY
yrow(28, "Lowest month-end cash in the year", R_CLOSE, CUR, kind="min", note="Must stay above zero without drawing the line of credit")
yrow(29, "Cash at year end", R_CLOSE, CUR, kind="last")
yrow(30, "Annual debt service (van loans)", R_CVAN)
yrow(31, "Debt service coverage (net profit + interest + depreciation) / debt service", None, '0.00"x";(0.00"x");"-"', kind=lambda col, y: f"=IF({col}30=0,0,({col}15+SUMIFS(Monthly!$C${R_INT}:$AL${R_INT},Monthly!$C$3:$AL$3,{y})+SUMIFS(Monthly!$C${R_DEP}:$AL${R_DEP},Monthly!$C$3:$AL$3,{y}))/{col}30)", note="Lenders look for 1.25x or better")
put(Y, "A33", "Break-even", bold=True); Y["A33"].fill = GREY
yrow(34, "Fixed costs (labor, operating expenses, owner draw)", None, CUR, kind=lambda col, y: f"={col}9+{col}11+{col}14")
yrow(35, "Break-even revenue at the year's gross margin", None, CUR, kind=lambda col, y: f"=IF({col}8=0,0,{col}34/{col}8)", bold=True, note="Revenue needed to cover all costs including the owner's salary")
yrow(36, "Revenue above (below) break-even", None, CUR, kind=lambda col, y: f"={col}5-{col}35")
yrow(37, "Break-even revenue per month", None, CUR, kind=lambda col, y: f"={col}35/12")

wb.move_sheet("Startup Costs", offset=-1)  # order: Assumptions, Startup Costs, Annual Summary, Monthly
for ws in wb.worksheets:
    ws.sheet_view.showGridLines = True
wb.save(OUT)
print("saved", OUT, "rows:", dict(REV=R_REV, COGS=R_COGS, GP=R_GP, LAB=R_LAB, OPEX=R_OPEX, NET=R_NET, CLOSE=R_CLOSE, MKT=R_MKT, OWN=R_OWN, JOBS=R_JOBS))
