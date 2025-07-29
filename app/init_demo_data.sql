/* =========================================================
   RESET – curata toate tabelele (optional, pentru re‑rule)
   ========================================================= */
TRUNCATE TABLE archived_files  RESTART IDENTITY CASCADE;
TRUNCATE TABLE work_days       RESTART IDENTITY CASCADE;
TRUNCATE TABLE vacations       RESTART IDENTITY CASCADE;
TRUNCATE TABLE bonuses         RESTART IDENTITY CASCADE;
TRUNCATE TABLE salaries        RESTART IDENTITY CASCADE;
TRUNCATE TABLE employees       RESTART IDENTITY CASCADE;
TRUNCATE TABLE users           RESTART IDENTITY CASCADE;

/* =========================================================
   USERS – conturi aplicatie (manager + 4 angajati)
   ========================================================= */
INSERT INTO users (username, "password", email, role, organization_name, created_at) VALUES
  ('manager01',  'adminpass',            'manager@acme.com',    'MANAGER',  'ACME Corp',  NOW()),
  ('john.doe',   'emp123',              'john.doe@acme.com',   'EMPLOYEE', 'ACME Corp',  NOW()),
  ('jane.smith', 'emp123',              'jane.smith@acme.com', 'EMPLOYEE', 'ACME Corp',  NOW()),
  ('maria.pop',  'emp123',              'maria.pop@acme.com',  'EMPLOYEE', 'ACME Corp',  NOW()),
  ('alex.iones', 'emp123',              'alex.iones@acme.com', 'EMPLOYEE', 'ACME Corp',  NOW());

/* =========================================================
   EMPLOYEES – date personale + legatura spre users
   ========================================================= */
INSERT INTO employees (user_id, first_name, last_name, cnp, username, "password", email,
                       address, city, country)
SELECT user_id, first_name, last_name, cnp, username, 'emp123', email,
       address, city, country
FROM
(
  VALUES
  /* manager – nu va primi fisa de salariu, dar il pastram */
  (1, 'Ana',      'Marin',   '2860505123456', 'manager01', 'manager@acme.com',
   'Str. Libertatii 10', 'Bucuresti', 'RO'),
  -- angajatii
  (2, 'John',     'Doe',     '1900301123457', 'john.doe',  'john.doe@acme.com',
   'Str. Lalelelor 5',   'Cluj-Napoca', 'RO'),
  (3, 'Jane',     'Smith',   '2910623123458', 'jane.smith','jane.smith@acme.com',
   'Bd. Unirii 15',      'Iasi',        'RO'),
  (4, 'Maria',    'Pop',     '2930915123459', 'maria.pop', 'maria.pop@acme.com',
   'Calea Victoriei 88', 'București',  'RO'),
  (5, 'Alex',     'Ionescu', '1941201123460', 'alex.iones','alex.iones@acme.com',
   'Str. Pacii 42',      'Timisoara',  'RO')
) AS e(user_id, first_name, last_name, cnp, username, email,
       address, city, country);

/* =========================================================
   SALARIES – salariul de baza pe luna (iulie 2025)
   ========================================================= */
INSERT INTO salaries (employee_id, base_salary, "month") VALUES
  -- john.doe
  (2, 8500,  DATE '2025-07-01'),
  -- jane.smith
  (3, 9200,  DATE '2025-07-01'),
  -- maria.pop
  (4, 7800,  DATE '2025-07-01'),
  -- alex.iones
  (5, 8000,  DATE '2025-07-01');

/* =========================================================
   BONUSES – prime / sporuri (facultativ)
   ========================================================= */
INSERT INTO bonuses (employee_id, amount, description, "month") VALUES
  (2,  850, 'Performanta Q2',   DATE '2025-07-01'),
  (3, 1200, 'Leadership',      DATE '2025-07-01'),
  (5,  500, 'Spor weekend',    DATE '2025-07-01');

/* =========================================================
   VACATIONS – concedii efectuate in iulie 2025
   ========================================================= */
INSERT INTO vacations (employee_id, start_date,   end_date,     number_of_days, reason) VALUES
  (3, DATE '2025-07-08', DATE '2025-07-12', 5, 'Concediu odihna'),
  (4, DATE '2025-07-22', DATE '2025-07-26', 5, 'Concediu odihna');

/* =========================================================
   WORK_DAYS – zile efectiv lucrate in iulie 2025
   (in RO iulie 2025 are 23 zile lucratoare calendaristice)
   ========================================================= */
INSERT INTO work_days (employee_id, "month", number_of_days) VALUES
  (2, DATE '2025-07-01', 23),           -- fara concediu
  (3, DATE '2025-07-01', 18),           -- 5 zile libere
  (4, DATE '2025-07-01', 18),           -- 5 zile libere
  (5, DATE '2025-07-01', 23);           -- fara concediu

/* =========================================================
   ARCHIVED_FILES – fisiere expediate (initial gol)
   Se vor popula de logica aplicatiei cand se trimite Excel/PDF
   ========================================================= */
/* Exemplu (stergere dupa test):
INSERT INTO archived_files (employee_id, file_name, file_type, path, sent_date)
VALUES (2, 'john_doe_salary_2025‑07.pdf', 'PDF', '/archive/2025/07/', CURRENT_DATE);
*/

COMMIT;