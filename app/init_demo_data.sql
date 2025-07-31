/* =========================================================
   RESET – curata toate tabelele (pentru re-rule)
   ========================================================= */
TRUNCATE TABLE archived_files  RESTART IDENTITY CASCADE;
TRUNCATE TABLE work_days       RESTART IDENTITY CASCADE;
TRUNCATE TABLE vacations       RESTART IDENTITY CASCADE;
TRUNCATE TABLE bonuses         RESTART IDENTITY CASCADE;
TRUNCATE TABLE salaries        RESTART IDENTITY CASCADE;
TRUNCATE TABLE employees       RESTART IDENTITY CASCADE;

/* =========================================================
   EMPLOYEES
   ========================================================= */
INSERT INTO employees (
   employee_id, manager_id, role,
   first_name, last_name, cnp,
   username, password, email,
   address, city, country,
   created_at
) VALUES
-- manager 1
(1, NULL,     'manager',
   'Ana',      'Marin',   '2860505123456',
   'johndoe10200', 'adminpass', 'johndoe10200@yahoo.com',
   'Str. Libertatii 10', 'Bucuresti', 'RO',
   NOW()),
-- angajati ai managerului 1
(2, 1,        'employee',
   'John',     'Doe',     '1900301123457',
   'john.doe',    'emp123', 'johndoe10304@proton.me',
   'Str. Lalelelor 5', 'Cluj-Napoca', 'RO',
   NOW()),
(3, 1,        'employee',
   'Jane',     'Smith',   '2910623123458',
   'jane.smith',  'emp123', 'johndoe10201@yahoo.com',
   'Bd. Unirii 15', 'Iasi',      'RO',
   NOW())
;
/* =========================================================
   SALARIES – baza de salariu pentru iulie 2025
   ========================================================= */
INSERT INTO salaries (employee_id, base_salary, "month") VALUES
   (1,  1000, DATE '2025-07-01'),
   (2,  8500, DATE '2025-07-01'),
   (3,  9200, DATE '2025-07-01');

/* =========================================================
   BONUSES – prime / sporuri iulie 2025
   ========================================================= */
INSERT INTO bonuses (employee_id, amount, description, "month") VALUES
   (1,  500,  'Spor weekend',   DATE '2025-07-01'),
   (2,  850,  'Performanta Q2', DATE '2025-07-01'),
   (3, 1200,  'Leadership',     DATE '2025-07-01');

/* =========================================================
   VACATIONS – concedii iulie 2025
   ========================================================= */
INSERT INTO vacations (employee_id, start_date, end_date, number_of_days, reason) VALUES
   (1, DATE '2025-06-08', DATE '2025-06-12', 5, 'Concediu odihna'),
   (2, DATE '2025-07-08', DATE '2025-07-12', 5, 'Concediu odihna'),
   (3, DATE '2025-07-22', DATE '2025-07-26', 5, 'Concediu odihna');

/* =========================================================
   WORK_DAYS – zile lucrate iulie 2025
   (in RO iulie 2025 are 23 zile lucratoare)
   ========================================================= */
INSERT INTO work_days (employee_id, "month", number_of_days) VALUES
   (1, DATE '2025-07-01', 23),  -- fara concediu
   (2, DATE '2025-07-01', 23),  -- fara concediu
   (3, DATE '2025-07-01', 18);  -- 5 zile concediu

/* =========================================================
   ARCHIVED_FILES – inca niciun fisier
   ========================================================= */
/* Exemple de insertii generate din aplicatie:
INSERT INTO archived_files (employee_id, file_name, file_type, path, sent_date)
 VALUES (3, 'john_doe_salary_2025-07.pdf', 'PDF', '/archive/2025/07/', CURRENT_DATE);
*/

COMMIT;
