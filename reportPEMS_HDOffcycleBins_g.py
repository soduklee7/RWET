from fpdf import FPDF
import time

class PEMSReport(FPDF):
    def __init__(self, veh_title):
        super().__init__(orientation="P", unit="in", format="Letter")
        self.veh_title = veh_title
        self.set_margins(left=0.5, top=0.25, right=0.5)
        self.set_auto_page_break(auto=True, margin=0.5)

    def header(self):
        # Header with Horizontal Rule
        self.set_font("Arial", size=9)
        self.cell(0, 0.2, self.veh_title, align="C", ln=True)
        # Draw Line (Horizontal Rule)
        self.line(0.5, 0.45, 8.0, 0.45)
        self.ln(0.3)

    def footer(self):
        # Footer with Horizontal Rule and Page Number
        self.set_y(-0.5)
        self.line(0.5, self.get_y(), 8.0, self.get_y())
        self.set_font("Arial", size=9)
        self.cell(0, 0.3, f"Page {self.page_no()}", align="C")

def report_pems_hd_offcycle_bins(set_idx, filename, veh_data, udp, bin_data):
    start_time = time.time()
    
    # Extract data strings (Simulating MATLAB's logData access)
    log = veh_data[set_idx]['log_data']
    scalar = veh_data[set_idx]['scalar_data']
    veh_model = f"{log['oem']} {log['model']} {log['my']}"
    header_title = f"NVFEL Laboratory: PEMS Test Report: {veh_model}"

    # Initialize PDF
    pdf = PEMSReport(header_title)
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)

    # --- Section: Test Information
    pdf.cell(0, 0.4, "Test Information", ln=True)
    pdf.set_font("Arial", size=11)
    
    # Table Data
    test_info = [
        ["Date and Time", str(log['date_time'])],
        ["Vehicle Model", veh_model],
        ["Vehicle ID", str(log['vehid'])],
        ["File Name", str(veh_data[set_idx]['filename'])]
    ]
    
    # Render Table 1
    create_table(pdf, test_info, col_widths=(2, 5))

    # --- Section: Vehicle and Cycle
    pdf.ln(0.2)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 0.4, "Vehicle and Cycle", ln=True)
    pdf.set_font("Arial", size=11)
    
    dist_val = scalar['Distance_Mile']
    dist_unit = "miles" # Usually from scalar['Properties']['VariableUnits']
    
    vc_data = [
        ["Test Cycle", log['test_cycle'], "", "Fuel", log['fuel']],
        ["Cycle Distance", f"{dist_val:10.2f} {dist_unit}", "", "VIN", log['vin']],
        ["Odometer", str(log['odo']), "", "Notes", log['notes']]
    ]
    create_table(pdf, vc_data, col_widths=(1.5, 2, 0.5, 1, 2))

    # --- Section: Mass Emissions
    pdf.ln(0.2)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 0.4, "Test Cycle Mass Emissions", ln=True)
    pdf.set_font("Arial", size=11)
    
    # Extract emission values
    emissions = [
        ["NOx", "CO", "HC", "CO2"],
        ["(g/mi)", "(g/mi)", "(g/mi)", "(g/mi)"], # Units
        [f"{scalar['kNOx_Gms_Per_Mile']:8.4f}", 
         f"{scalar['CO_Gms_Per_Mile']:8.4f}", 
         f"{scalar['HC_Gms_Per_Mile']:8.4f}", 
         f"{scalar['CO2_Gms_Per_Mile']:8.4f}"]
    ]
    create_table(pdf, emissions, col_widths=(1.75, 1.75, 1.75, 1.75), align="C")

    # Output PDF
    pdf.output(filename)
    print(f"Report generated in {time.time() - start_time:.2f}s")

def create_table(pdf, data, col_widths, align="L"):
    """Helper to draw a bordered table"""
    for row in data:
        for i, datum in enumerate(row):
            width = col_widths[i]
            pdf.cell(width, 0.3, str(datum), border=1, align=align)
        pdf.ln()

# Note: You will need to install fpdf2 via 'pip install fpdf2'
