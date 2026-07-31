####################################################
# Write HTML
####################################################

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

template_file = os.path.join(
    BASE_DIR,
    "templates",
    "report_template.html"
)

with open(template_file, encoding="utf-8") as f:
    template = f.read()

html = template.replace("{{CONTENT}}", report)

report_file = os.path.join(
    output_folder,
    "Executive_Report.html"
)

with open(report_file, "w", encoding="utf-8") as f:
    f.write(html)

# ---------------------------------------------------
# Copy Latest Report
# ---------------------------------------------------

latest_folder = os.path.join(
    BASE_DIR,
    "output",
    "latest"
)

os.makedirs(latest_folder, exist_ok=True)

latest_report = os.path.join(
    latest_folder,
    "Executive_Report.html"
)

with open(latest_report, "w", encoding="utf-8") as f:
    f.write(html)

print()
print("=" * 70)
print("HTML REPORT GENERATED")
print("=" * 70)
print(report_file)
print()
print("Latest Report")
print(latest_report)

return report_file