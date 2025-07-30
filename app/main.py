from datetime import datetime, date
import calendar
from flask import Flask, jsonify, render_template, render_template_string, request, redirect, session, url_for 
from flask_sqlalchemy import SQLAlchemy
import json
import logging
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
import os
import pandas as pd
import uuid

app = Flask(__name__)

# Foloseste un secret key aleator la fiecare pornire, astfel incat sesiunile vechi sa fie invalidate
app.secret_key = os.environ.get('SECRET_KEY') or os.urandom(24)

#DB configuration
app.config['SQLALCHEMY_DATABASE_URI'] = (os.environ.get('DATABASE_URL') or 'postgresql://postgres:postgres@localhost:5432/master')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ----------------------------- HTML TEMPLATE ----------------------------------

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{{ title }}</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            background-color: #f0f0f0;
        }
        .window {
            position: absolute;
            left: {{ x }}px;
            top: {{ y }}px;
            width: {{ w }}px;
            height: {{ h }}px;
            border: 2px solid #333;
            background-color: #ccc;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.5);
            padding: 10px;
        }
        .display-container {
            position: absolute;
            top: 50px;
            left: 100px;
            display: flex;
            align-items: center;
        }
        .display-label {
            font-family: sans-serif;
            font-size: 14px;
            margin-right: 10px;
        }
        .display-box {
            width: 200px;
            height: 50px;
            border: 1px solid #666;
            background-color: #fff;
            font-family: monospace;
            font-size: 14px;
            padding: 5px;
            box-sizing: border-box;
        }
        .radio-button {
            position: absolute;
            top: 120px;
            left: 100px;
            font-family: sans-serif;
            font-size: 14px;
        }
        .return-button {
            position: absolute;
            left: {{ ret_x }}px;
            top: {{ ret_y }}px;
            width: {{ ret_w }}px;
            height: {{ ret_h }}px;
            font-size: 12px;
        }
        .radio-group {
            position: absolute;
            top: 150px;
            left: 160px;
            width: 200px;
            border: 1px solid #333;
            background-color: #eee;
            padding: 10px;
        }
    </style>
    <script>
        // Enforce max 256 characters per line and allow Enter key
        document.addEventListener('DOMContentLoaded', function() {
            function enforceMaxLineLength(textarea) {
                const lines = textarea.value.split('\n');
                for (let i = 0; i < lines.length; i++) {
                    if (lines[i].length > 256) {
                        lines[i] = lines[i].substring(0, 256);
                    }
                }
                textarea.value = lines.join('\n');
            }
            ['edit_box', 'edit_box2'].forEach(function(id) {
                const ta = document.getElementById(id);
                if (ta) {
                    ta.addEventListener('input', function() { enforceMaxLineLength(ta); });
                }
            });
        });
    </script>
</head>
<body>
    <div class="window">
        <div class="display-container">
            <div class="display-label">export Excel</div>
            <input class="display-box" type="text" value="{{ first_text }}" readonly>

            <div class="display-label" style="margin-left: 20px;">export PDF</div>
            <input class="display-box" type="text" value="{{ second_text }}" readonly>

            <div class="display-label" style="margin-left: 20px;">send Excel</div>
            <input class="display-box" type="text" value="{{ third_text }}" readonly>
            
            <div class="display-label" style="margin-left: 20px;">send PDF</div>
            <input class="display-box" type="text" value="{{ fourth_text }}" readonly>
        </div>
        
        <form method="post">
            <div class="radio-group">
                {% set custom_labels = ["export Excel", "export PDF", "send Excel", "send PDF"] %}
                {% for i in range(radio_buttons | length) %}
                <div class="radio-option">
                    <input type="radio" id="{{ radio_buttons[i].id }}" name="radio_option" value="{{ i + 1 }}" 
                        {% if selected_choice == i + 1 %}checked{% endif %}>
                    <label for="{{ radio_buttons[i].id }}">{{ custom_labels[i] }}</label>
                </div>
                {% endfor %}
            </div>
            
            <div style="position: absolute; top: 130px; left: 400px;">
                <label for="edit_box" style="font-family: sans-serif; font-size: 14px;">My Input</label><br>
                <textarea id="edit_box" name="edit_box" style="width: 150px; height: 100px; font-family: monospace; font-size: 14px;">{{ current_input }}</textarea>
            </div>
            
            <div style="position: absolute; top: 130px; left: 620px;">
                <label for="edit_box2" style="font-family: sans-serif; font-size: 14px;">My Input&nbsp;2</label><br>
                <textarea id="edit_box2" name="edit_box2" style="width: 150px; height: 100px; font-family: monospace; font-size: 14px;">{{ second_input }}</textarea>
            </div>
            
            <button class="return-button" type="submit">&Return</button>
        </form>
    </div>
</body>
</html>
"""

# ----------------------------- DATABASE Models ---------------------

# model mapping la tabela users
class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column('password', db.String(128), nullable=False)
    email    = db.Column(db.String(120))
    role     = db.Column(db.String(20))
    organization_name  = db.Column(db.String(),    nullable=True)
    created_at         = db.Column(db.DateTime,    nullable=True, default=datetime.utcnow)

# Employee model conform structurii existente
class Employee(db.Model):
    __tablename__ = 'employees'
    employee_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    cnp = db.Column(db.String(20), unique=True, nullable=False)
    username = db.Column(db.String(64))
    password = db.Column(db.String(128))
    email = db.Column(db.String(120))
    address = db.Column(db.String(200))
    city = db.Column(db.String(100))
    country = db.Column(db.String(100))

    @property
    def full_name(self):
        """Returnează numele complet al angajatului"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        else:
            return self.username or "N/A"

class Salary(db.Model):
    __tablename__ = 'salaries'
    salary_id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.employee_id'))
    base_salary = db.Column(db.Numeric(10, 2))
    month = db.Column(db.Date)

class Bonus(db.Model):
    __tablename__ = 'bonuses'
    bonus_id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.employee_id'))
    amount = db.Column(db.Numeric(10, 2))
    description = db.Column(db.String(255))
    month = db.Column(db.Date)

class Vacation(db.Model):
    __tablename__ = 'vacations'
    vacation_id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.employee_id'))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    number_of_days = db.Column(db.Integer)
    reason = db.Column(db.String(255))

class WorkDay(db.Model):
    __tablename__ = 'work_days'
    work_day_id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.employee_id'))
    month = db.Column(db.Date)
    number_of_days = db.Column(db.Integer)

class ArchivedFile(db.Model):
    __tablename__ = 'archived_files'
    file_id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.employee_id'))
    file_name = db.Column(db.String(255))
    file_type = db.Column(db.String(50))
    path = db.Column(db.String(500))
    sent_date = db.Column(db.Date)

# ----------------------------- HELPER FUNCTIONS FOR EXCEL ---------------------

def get_current_month_start():
    """Returneaza primul zi din luna curenta"""
    today = date.today()
    return date(today.year, today.month, 1)

def get_current_month_end():
    """ReturneazA ultima zi din luna curentA"""
    today = date.today()
    last_day = calendar.monthrange(today.year, today.month)[1]
    return date(today.year, today.month, last_day)

def get_employee_data_for_excel(email_addresses):
    """
    ColecteazA datele pentru toTi angajaTii cu adresele de email specificate
    pentru luna curenta
    """
    try:
        employees_data = []
        current_month_start = get_current_month_start()
        current_month_end = get_current_month_end()
        
        for email in email_addresses:
            email = email.strip()
            if not email:
                continue
                
            # Find the employee by email
            employee = Employee.query.filter_by(email=email).first()
            if not employee:
                continue
            
            # Get the salary for the current month
            salary = Salary.query.filter(
                Salary.employee_id == employee.employee_id,
                Salary.month >= current_month_start,
                Salary.month <= current_month_end
            ).first()
            
            # Get the working days for the current month
            work_days = WorkDay.query.filter(
                WorkDay.employee_id == employee.employee_id,
                WorkDay.month >= current_month_start,
                WorkDay.month <= current_month_end
            ).first()
            
            # Get the vacation days for the current month
            vacation_days = db.session.query(db.func.sum(Vacation.number_of_days)).filter(
                Vacation.employee_id == employee.employee_id,
                Vacation.start_date >= current_month_start,
                Vacation.end_date <= current_month_end
            ).scalar() or 0
            
            # Get the bonuses for the current month
            bonuses = Bonus.query.filter(
                Bonus.employee_id == employee.employee_id,
                Bonus.month >= current_month_start,
                Bonus.month <= current_month_end
            ).all()
            
            # Prepare the data for Excel
            employee_info = {
                'name': employee.full_name,
                'email': employee.email,
                'salary': float(salary.base_salary) if salary and salary.base_salary else 0.0,
                'work_days': work_days.number_of_days if work_days else 0,
                'vacation_days': vacation_days,
                'bonuses': []
            }
            
            # Add the bonuses
            for bonus in bonuses:
                employee_info['bonuses'].append({
                    'amount': float(bonus.amount) if bonus.amount else 0.0,
                    'description': bonus.description or 'N/A'
                })
            
            employees_data.append(employee_info)
        
        return employees_data
    
    except Exception as e:
        print(f"Error collecting employee data: {e}")
        return []

def create_excel_file(employees_data, output_path):
    """
    Creează fișierul Excel cu datele angajaților
    """
    try:
        # Create the workbook and worksheet
        wb = Workbook()
        ws = wb.active
        ws.title = "Employee Summary"
        
        # Styles for header
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        header_alignment = Alignment(horizontal="center", vertical="center")
        
        # The headers of the columns
        headers = [
            "Employee Name", 
            "Email", 
            "Base Salary", 
            "Working Days", 
            "Vacation Days", 
            "Total Bonuses", 
            "Bonus Details"
        ]
        
        # Add the headers
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_alignment
        
        # Add the employee data
        for row, employee in enumerate(employees_data, 2):
            ws.cell(row=row, column=1, value=employee['name'])
            ws.cell(row=row, column=2, value=employee['email'])
            ws.cell(row=row, column=3, value=employee['salary'])
            ws.cell(row=row, column=4, value=employee['work_days'])
            ws.cell(row=row, column=5, value=employee['vacation_days'])
            
            # Calculate the total bonuses
            total_bonuses = sum(bonus['amount'] for bonus in employee['bonuses'])
            ws.cell(row=row, column=6, value=total_bonuses)
            
            # Add the details of the bonuses
            bonus_details = "; ".join([f"{bonus['description']}: {bonus['amount']}" for bonus in employee['bonuses']])
            ws.cell(row=row, column=7, value=bonus_details if bonus_details else "No bonuses")
        
        # Adjust the width of the columns
        column_widths = [20, 25, 15, 15, 15, 15, 40]
        for col, width in enumerate(column_widths, 1):
            ws.column_dimensions[ws.cell(row=1, column=col).column_letter].width = width
        
        # Save the file
        wb.save(output_path)
        return True
        
    except Exception as e:
        print(f"Error creating Excel file: {e}")
        return False

# ----------------------------- API ENDPOINTS --------------------------------

@app.route("/createAggregatedEmployeeData", methods=["POST"])
def create_aggregated_employee_data():
    """
    API endpoint pentru generarea raportului Excel cu datele angajaților
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        email_addresses = data.get('emails', [])
        output_folder = data.get('output_folder', 'app/generated_excel')
        
        if not email_addresses:
            return jsonify({'error': 'No email addresses provided'}), 400
        
        # make sure folder exists
        os.makedirs(output_folder, exist_ok=True)
        
        # generate file name with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"employee_summary_{timestamp}.xlsx"
        output_path = os.path.join(output_folder, filename)
        
        # collect data about employee
        employees_data = get_employee_data_for_excel(email_addresses)
        
        if not employees_data:
            return jsonify({'error': 'No employee data found for provided emails'}), 404
        
        # create excel file
        success = create_excel_file(employees_data, output_path)
        
        if success:
            return jsonify({
                'success': True,
                'filename': filename,
                'path': output_path,
                'message': f'{filename} created successfully'
            }), 200
        else:
            return jsonify({'error': 'Failed to create Excel file'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        # query the database
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session["user"] = user.username
            return redirect(url_for("index"))
        else:
            error = "Credentiale invalide"
            return render_template("login.html", error=error)

    # GET – doar afisam formularul (fara eroare)
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user", None)     # sterge cheia din sesiune
    return redirect(url_for("login"))

# ----------------------------- CLASSES ---------------------------------------

class Point:
    def __init__(self, x, y):
        self._x = x
        self._y = y

    def getX(self):
        return self._x

    def getY(self):
        return self._y
    
    def setY(self, y):
        self._y = y

class Fl_Output:
    def __init__(self, x, y, w, h, label=None):
        self.x = x
        self.y = y
        self.width = w
        self.height = h
        self.label = label
        self._value = ""

    def value(self, txt):
        self._value = txt

    def redraw(self):
        pass

    def getText(self):
        return self._value

class MyDisplayBox(Fl_Output):
    def __init__(self, pos: Point, w: int, h: int, label: str = None):
        super().__init__(pos.getX(), pos.getY(), w, h, label)

    def setText(self, txt: str):
        self.value(txt)
        self.redraw()

class MyReturnButton:
    def __init__(self, pos: Point, w: int, h: int, label: str = "&Return"):
        self.x = pos.getX()
        self.y = pos.getY()
        self.w = w
        self.h = h
        self.label = label
        self.tooltip = "Push Return button to exit"
        self.labelsize = 12

    def getRenderParams(self):
        return {
            "ret_x": self.x,
            "ret_y": self.y,
            "ret_w": self.w,
            "ret_h": self.h,
            "label": self.label
        }

# ----------------------------- EDIT BOX CLASS ----------------------------------

class MyEditBox:
    def __init__(self, pos: Point, w: int, h: int, label: str):
        self.x = pos.getX()
        self.y = pos.getY()
        self.w = w
        self.h = h
        self.label = label
        self.tooltip = "Input field for short text with newlines."
        self.wrap = True  # Equivalent behavior
        self.controller = None
        self.value = ""

    def setText(self, txt: str):
        self.value = txt

    def getText(self):
        return self.value

    def input_cb(self):
        # Placeholder for future callback logic, e.g., notify controller or update model
        pass

    def getRenderParams(self):
        return {
            "edit_x": self.x,
            "edit_y": self.y,
            "edit_w": self.w,
            "edit_h": self.h,
            "edit_label": self.label,
            "edit_value": self.value
        }
        
# ----------------------------- MODEL CLASS ------------------------------------

class Model:
    def __init__(self):
        self.lastChoice = 0
        self.lastInput = ""
        self.chView = None
        self.inpView = None
        self.factView = None
        self.sendPdfView = None

    def setLastChoice(self, ch):
        self.lastChoice = ch
        self.notify()

    def getLastChoice(self):
        return self.lastChoice

    def setChView(self, db: MyDisplayBox):
        self.chView = db

    def setInpView(self, db):
        self.inpView = db
    
    def setLastInput(self, txt):
        self.lastInput = txt

    def setFactView(self, db: MyDisplayBox):
        self.factView = db
    
    def setSendPdf(self, db: MyDisplayBox):
        self.sendPdfView = db

    def notify(self):
        if self.chView:
            self.chView.setText("Last choice is " + str(self.lastChoice))
        if self.inpView:
            self.inpView.setText(f"Last input is `{self.lastInput}`")

# ----------------------------- CONTROLLER CLASS -------------------------------

class Controller:
    def __init__(self):
        self.model = None

    def setModel(self, aModel: Model):
        self.model = aModel

    def chControl(self, aString: str): # apply the action from the GUI to the model
        try:
            ch = int(aString.strip().split()[-1])
            self.model.setLastChoice(ch)
        except Exception as e:
            print("Invalid input to Controller.chControl:", aString, e)
            
    def inpControl(self, aString: str): # apply the action from the GUI to the model
        self.model.setLastInput(aString)
        
        
        # Check if the 'export Excel' option (choice 1) is selected.
        if self.model.getLastChoice() == 1:
            self.handle_excel_export(aString)
        
        #Compute based on choice and update view accordingly
        if self.model.getLastChoice() == 2: # check if the option corresponds to the n-th fibonacci number option
            try:
                n = int(aString.strip())
                fib = self.fibonnaci(n)
                self.model.inpView.setText(str(fib))
            except Exception as e:
                self.model.inpView.setText("Invalid input")
                
        elif self.model.getLastChoice() == 3: # check if the option corresponds to factorial
            try:
                n = int(aString.strip())
                factorial_result = self.factorial(n)
                self.model.factView.setText(str(factorial_result))
            except Exception as e:
                self.model.factView.setText("Invalid input")
    
    def handle_excel_export(self, input_text, second_input_text=""):
        """
        Gestionează exportul Excel bazat pe input-urile din GUI
        """
        try:
            lines = input_text.strip().split('\n')
            if not lines or not lines[0].strip():
                if self.model.chView:
                    self.model.chView.setText("Error: No folder path provided")
                return
            
            # Prima linie este path-ul folderului
            output_folder = lines[0].strip()
            
            # Dacă există un al doilea input box, folosește-l pentru email-uri
            if second_input_text.strip():
                email_lines = second_input_text.strip().split('\n')
                email_addresses = [email.strip() for email in email_lines if email.strip()]
            else:
                # Altfel, email-urile sunt pe liniile următoare din primul input
                email_addresses = [email.strip() for email in lines[1:] if email.strip()]
            
            if not email_addresses:
                if self.model.chView:
                    self.model.chView.setText("Error: No email addresses provided")
                return
            
            # Asigură-te că folderul există
            os.makedirs(output_folder, exist_ok=True)
            
            # Generează numele fișierului cu timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"employee_summary_{timestamp}.xlsx"
            output_path = os.path.join(output_folder, filename)
            
            # Colectează datele angajaților
            employees_data = get_employee_data_for_excel(email_addresses)
            
            if not employees_data:
                if self.model.chView:
                    self.model.chView.setText("Error: No employee data found")
                return
            
            # Creează fișierul Excel
            success = create_excel_file(employees_data, output_path)
            
            if success:
                if self.model.chView:
                    self.model.chView.setText(f"{filename} created")
            else:
                if self.model.chView:
                    self.model.chView.setText("Error: Failed to create Excel file")
                    
        except Exception as e:
            if self.model.chView:
                self.model.chView.setText(f"Error: {str(e)}")
            print(f"Excel export error: {e}")
    
    def fibonnaci(self, n):
        #base condition
        if(n <= 1):
            return n
        
        #problem broken down into 2 function calls
        #and their results combined and returned
        last = self.fibonnaci(n - 1)
        slast = self.fibonnaci(n - 2)
        
        return last + slast

    def factorial(self, n):  # the function for factorial
        if n < 0:
            return "Error: negative number"
        P = 1
        for i in range(1, n + 1):
            P *= i
        return P

# ----------------------------- VIEW-CONTROLLER ASSOCIATION --------------------

class MyRadioButton:
    _id_counter = 0

    def __init__(self, pos: Point, w: int, h: int, slabel: str):
        self.x = pos.getX()
        self.y = pos.getY()
        self.w = w
        self.h = h
        self.label = slabel
        self.tooltip = "Radio button, only one button is set at a time."
        self.down_box = "FL_ROUND_DOWN_BOX"
        self.id = f"radio{MyRadioButton._id_counter}"
        MyRadioButton._id_counter += 1
        self.controller = None

    def getRenderParams(self):
        return {
            "id": self.id,
            "label": self.label
        }

    def setController(self, aCntrl):
        self.controller = aCntrl

    def radio_button_cb(self):
        if self.controller:
            self.controller.chControl(self.label)

class MyRadioGroup:
    def __init__(self, pos: Point, w: int, h: int, label: str, no: int):
        self.elts = []
        bpos = Point(pos.getX(), pos.getY())
        for i in range(no):
            bpos.setY(pos.getY() + i * 30)
            rb = MyRadioButton(bpos, w, h // no, f"My Choice {i + 1}")
            self.elts.append(rb)

    def getButtons(self):
        return self.elts
    
    def setController(self, aCntrl):
        for rb in self.elts:
            rb.setController(aCntrl)

# ----------------------------- CONNECTION LOGIC ----------------------------------------

class MyWindow:
    def __init__(self, pos: Point, w: int, h: int, title: str):
        if pos is None:
            self.x, self.y = 100, 200
        else:
            self.x, self.y = pos.getX(), pos.getY()
        self.w = w
        self.h = h
        self.title = title
        self.display_box = None
        self.return_button = None
        self.radio_buttons = []
        
        # Store references to all three display boxes
        self.firstdb = None
        self.seconddb = None
        self.thirddb = None
        self.fourthdb = None

    def addDisplayBox(self, display_box: MyDisplayBox):
        if self.firstdb is None:
            self.firstdb = display_box
        elif self.seconddb is None:
            self.seconddb = display_box
        elif self.thirddb is None:
            self.thirddb = display_box
        elif self.fourthdb is None:
            self.fourthdb = display_box

    def addReturnButton(self, return_button: MyReturnButton):
        self.return_button = return_button
        
    def addRadioButton(self, rb: MyRadioButton):
        self.radio_buttons.append(rb)
    
    def addRadioGroup(self, group):
        self.radio_buttons.extend(group.getButtons())

    def getRenderParams(self):
        params = {
            "x": self.x,
            "y": self.y,
            "w": self.w,
            "h": self.h,
            "title": self.title,
            "first_display_box_text": self.firstdb.getText() if self.firstdb else "",
            "second_display_box_text": self.seconddb.getText() if self.seconddb else "",
            "third_display_box_text": self.thirddb.getText() if self.thirddb else "",
            "fourth_display_box_text": self.thirddb.getText() if self.thirddb else "",
            "label": self.display_box.label if self.display_box else ""
        }
        if self.return_button:
            params.update(self.return_button.getRenderParams())
        if self.radio_buttons:
            params["radio_buttons"] = [rb.getRenderParams() for rb in self.radio_buttons]
        return params

# ----------------------------- ROUTING --------------------------

@app.route("/", methods=["GET", "POST"])
def index():
    
    # if user/admin not loggin, then send to /login
    if "user" not in session:
        return redirect(url_for("login"))
    
    
    posMainWindow = Point(100, 200)
    mainwindow = MyWindow(posMainWindow, 1150, 400, "Main Window")

    # Display Boxes
    posFirstDB = Point(100, 50)
    firstdb = MyDisplayBox(posFirstDB, 200, 50, "My display box")

    posSndDB = Point(360, 50)
    seconddb = MyDisplayBox(posSndDB, 200, 50, "Second display")

    posTrdDB = Point(620, 50)
    thirddb = MyDisplayBox(posTrdDB, 200, 50, "Third display")
    
    posFrthDB = Point(880, 50)
    fourthdb = MyDisplayBox(posFrthDB, 200, 50, "Fourth display")

    firstdb.setText("My first output text.")
    seconddb.setText("My second output text.")
    thirddb.setText("My third output text.")
    fourthdb.setText("My fourth output text.")

    mainwindow.addDisplayBox(firstdb)
    mainwindow.addDisplayBox(seconddb)
    mainwindow.addDisplayBox(thirddb)
    mainwindow.addDisplayBox(fourthdb)

    # Model and Controller
    model = Model()
    model.setChView(firstdb)  # Set firstdb for displaying Excel export messages
    model.setInpView(seconddb)
    model.setFactView(thirddb)  # set the factorial view to the third display box

    chCntrl = Controller()
    chCntrl.setModel(model)

    # Radio Group
    posRG = Point(160, 150)
    rg = MyRadioGroup(posRG, 150, 90, "MyChoice", 4)
    rg.setController(chCntrl)
    mainwindow.addRadioGroup(rg)

    # Return Button
    posRet = Point(400, 350)
    ret = MyReturnButton(posRet, 100, 25)
    mainwindow.addReturnButton(ret)

    # Edit Box input
    posEB = Point(400, 130)
    eb = MyEditBox(posEB, 150, 100, "&My Input")
    eb.setText("Initial edit text\nSecond line")

    # Edit Second Box input 
    posEB2 = Point(620, 130) # 400 px + 220 px = 620 px
    eb2 = MyEditBox(posEB2, 150, 100, "&My Input 2")
    eb2.setText("")

    if request.method == "POST":
        input_text = request.form.get("edit_box", "")
        second_text_input = request.form.get("edit_box2", "")
        selected_choice = request.form.get("radio_option", "") # processing the value of the selected radio button
        
        # Truncam fiecare linie la maxim 256 de caractere
        input_text = "\n".join([line[:256] for line in input_text.splitlines()])
        second_text_input = "\n".join([line[:256] for line in second_text_input.splitlines()])
        
        # Pentru export Excel, pasează ambele input-uri
        if int(selected_choice) == 1 if selected_choice else False:
            chCntrl.handle_excel_export(input_text, second_text_input)
        else:
            chCntrl.inpControl(input_text)
        
        # Process input text
        chCntrl.inpControl(input_text)
        
        # Set current_input for rendering
        current_input = input_text
        eb.setText(input_text)
        
        # Set current_second_input for rendering
        current_second_input = second_text_input
        eb2.setText(second_text_input)
    else:
        # For GET requests, use the initial text
        current_input = eb.getText()
        current_second_input = eb2.getText()
        selected_choice = ""
    
    # Prepare render parameters
    render_params = mainwindow.getRenderParams()
    render_params.update({
        "selected_choice": int(selected_choice) if selected_choice else 0,
        "current_input": current_input,
        "current_second_input": current_second_input,
        "first_text": firstdb.getText(),
        "second_text": seconddb.getText(),
        "third_text": thirddb.getText(),
        "fourth_text": fourthdb.getText()
    })
    
    return render_template_string(HTML_TEMPLATE, **render_params)
    
if __name__ == "__main__":
    app.run(debug=True)