-- =========================================================
-- KBC Pulse AI - MariaDB Database Schema & Seed Data Script
-- Hackathon Tectonic 2026 - Challenge KBC Banque & Assurance
-- =========================================================

CREATE DATABASE IF NOT EXISTS kbc_pulse_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE kbc_pulse_db;

-- ---------------------------------------------------------
-- 1. Table: clients
-- ---------------------------------------------------------
DROP TABLE IF EXISTS ai_predictions_nudges;
DROP TABLE IF EXISTS investments;
DROP TABLE IF EXISTS insurances;
DROP TABLE IF EXISTS loans;
DROP TABLE IF EXISTS upcoming_payments;
DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS financial_summaries;
DROP TABLE IF EXISTS clients;

CREATE TABLE clients (
    client_id VARCHAR(36) PRIMARY KEY,
    persona_type VARCHAR(100) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    age INT NOT NULL,
    civil_status VARCHAR(50) NOT NULL,
    profession VARCHAR(100) NOT NULL,
    monthly_net_income DECIMAL(10, 2) NOT NULL,
    investor_profile VARCHAR(50) NOT NULL,
    kbc_segment VARCHAR(100) NOT NULL,
    ai_consent_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------------------------------------------------------
-- 2. Table: financial_summaries
-- ---------------------------------------------------------
CREATE TABLE financial_summaries (
    summary_id INT AUTO_INCREMENT PRIMARY KEY,
    client_id VARCHAR(36) NOT NULL,
    total_available_capital DECIMAL(12, 2) NOT NULL,
    liquid_cash DECIMAL(12, 2) NOT NULL,
    savings_account DECIMAL(12, 2) NOT NULL,
    investments_value DECIMAL(12, 2) NOT NULL,
    total_monthly_deficits_or_debts DECIMAL(10, 2) NOT NULL,
    net_worth_trend_30d VARCHAR(20) NOT NULL,
    FOREIGN KEY (client_id) REFERENCES clients(client_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------------------------------------------------------
-- 3. Table: transactions
-- ---------------------------------------------------------
CREATE TABLE transactions (
    transaction_id VARCHAR(36) PRIMARY KEY,
    client_id VARCHAR(36) NOT NULL,
    tx_date DATE NOT NULL,
    merchant VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    tx_type ENUM('DEBIT', 'CREDIT') NOT NULL,
    flag_ai_trigger VARCHAR(100) DEFAULT NULL,
    FOREIGN KEY (client_id) REFERENCES clients(client_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------------------------------------------------------
-- 4. Table: upcoming_payments
-- ---------------------------------------------------------
CREATE TABLE upcoming_payments (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    client_id VARCHAR(36) NOT NULL,
    label VARCHAR(100) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    due_date DATE NOT NULL,
    status ENUM('PLANNED', 'PROCESSING', 'PAID', 'CANCELLED') DEFAULT 'PLANNED',
    FOREIGN KEY (client_id) REFERENCES clients(client_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------------------------------------------------------
-- 5. Table: loans
-- ---------------------------------------------------------
CREATE TABLE loans (
    loan_id INT AUTO_INCREMENT PRIMARY KEY,
    client_id VARCHAR(36) NOT NULL,
    loan_type VARCHAR(100) NOT NULL,
    initial_amount DECIMAL(12, 2) NOT NULL,
    remaining_balance DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    monthly_payment DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    status ENUM('ACTIVE', 'FULLY_PAID', 'PENDING_APPROVAL') NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    FOREIGN KEY (client_id) REFERENCES clients(client_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------------------------------------------------------
-- 6. Table: insurances
-- ---------------------------------------------------------
CREATE TABLE insurances (
    insurance_id INT AUTO_INCREMENT PRIMARY KEY,
    contract_code VARCHAR(50) NOT NULL UNIQUE,
    client_id VARCHAR(36) NOT NULL,
    insurance_type VARCHAR(100) NOT NULL,
    monthly_premium DECIMAL(10, 2) NOT NULL,
    status ENUM('ACTIVE', 'EXPIRED', 'CANCELLED') DEFAULT 'ACTIVE',
    start_date DATE NOT NULL,
    end_date DATE DEFAULT NULL,
    FOREIGN KEY (client_id) REFERENCES clients(client_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------------------------------------------------------
-- 7. Table: investments
-- ---------------------------------------------------------
CREATE TABLE investments (
    investment_id INT AUTO_INCREMENT PRIMARY KEY,
    client_id VARCHAR(36) NOT NULL,
    holding_name VARCHAR(100) NOT NULL,
    holding_type VARCHAR(50) NOT NULL,
    asset_value DECIMAL(12, 2) NOT NULL,
    return_ytd VARCHAR(20) NOT NULL,
    FOREIGN KEY (client_id) REFERENCES clients(client_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------------------------------------------------------
-- 8. Table: ai_predictions_nudges
-- ---------------------------------------------------------
CREATE TABLE ai_predictions_nudges (
    nudge_id VARCHAR(36) PRIMARY KEY,
    client_id VARCHAR(36) NOT NULL,
    priority ENUM('HIGH', 'MEDIUM', 'LOW') NOT NULL,
    category VARCHAR(50) NOT NULL,
    title VARCHAR(150) NOT NULL,
    description TEXT NOT NULL,
    explainability_reason TEXT NOT NULL,
    confidence_score DECIMAL(3, 2) NOT NULL,
    status ENUM('PENDING', 'ACCEPTED', 'DISMISSED') DEFAULT 'PENDING',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES clients(client_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =========================================================
-- SEED DATA INSERTION
-- =========================================================

-- 1. CLIENTS DATA
INSERT INTO clients (client_id, persona_type, first_name, last_name, age, civil_status, profession, monthly_net_income, investor_profile, kbc_segment, ai_consent_active) VALUES
('kbc_user_2894', 'Jeune Actif & Fort Potentiel', 'Marc', 'Dupont', 28, 'Célibataire', 'Ingénieur Logiciel Senior', 4200.00, 'Dynamique (MIFID II)', 'Young Professional Premium', TRUE),
('kbc_user_4012', 'Famille Établie & Rénovation Énergétique', 'Sophie & Thomas', 'Mertens', 42, 'Mariés (2 enfants)', 'Cadre Santé & Pharmacien', 7800.00, 'Modéré / Équilibré (MIFID II)', 'Family & Wealth Growth', TRUE),
('kbc_user_9103', 'Senior & Patrimoine', 'Luc', 'Van Damme', 61, 'Marié', 'Consultant Indépendant (Pré-Retraite)', 5600.00, 'Prudent / Conservateur (MIFID II)', 'Private Wealth & Senior Transition', TRUE);

-- 2. FINANCIAL SUMMARIES DATA
INSERT INTO financial_summaries (client_id, total_available_capital, liquid_cash, savings_account, investments_value, total_monthly_deficits_or_debts, net_worth_trend_30d) VALUES
('kbc_user_2894', 48500.00, 15000.00, 25000.00, 8500.00, 0.00, '+5.8%'),
('kbc_user_4012', 125000.00, 20000.00, 45000.00, 60000.00, 1250.00, '+2.1%'),
('kbc_user_9103', 380000.00, 30000.00, 150000.00, 200000.00, 0.00, '+1.4%');

-- 3. TRANSACTIONS HISTORY DATA
INSERT INTO transactions (transaction_id, client_id, tx_date, merchant, category, amount, tx_type, flag_ai_trigger) VALUES
('tx_101', 'kbc_user_2894', '2026-09-28', 'BMW Garage Brussels', 'Automotive', 18500.00, 'DEBIT', 'NEW_CAR_PURCHASE'),
('tx_102', 'kbc_user_2894', '2026-09-25', 'Notaire Janssens & Associés', 'Legal / Real Estate', 1200.00, 'DEBIT', 'REAL_ESTATE_INTENT'),
('tx_103', 'kbc_user_2894', '2026-09-24', 'Tech Corp Monthly Payroll', 'Salary', 4200.00, 'CREDIT', 'SALARY_INCOME'),
('tx_104', 'kbc_user_2894', '2026-09-15', 'Delhaize Supermarket', 'Groceries', 142.50, 'DEBIT', NULL),
('tx_105', 'kbc_user_2894', '2026-09-10', 'Apple Store Brussels', 'Electronics', 1299.00, 'DEBIT', NULL),
('tx_106', 'kbc_user_2894', '2026-09-02', 'TotalEnergies Station', 'Fuel', 75.00, 'DEBIT', NULL),
('tx_201', 'kbc_user_4012', '2026-09-20', 'EcoSolar Belgium', 'Home Improvement', 4500.00, 'DEBIT', 'GREEN_HOME_INVESTMENT'),
('tx_202', 'kbc_user_4012', '2026-09-22', 'VUB Université Bruxelles', 'Education', 980.00, 'DEBIT', 'TUITION_FEE'),
('tx_203', 'kbc_user_4012', '2026-09-25', 'Hôpital Erasme Paie', 'Salary', 4100.00, 'CREDIT', 'SALARY_INCOME'),
('tx_204', 'kbc_user_4012', '2026-09-25', 'Pharmacie Centrale Paie', 'Salary', 3700.00, 'CREDIT', 'SALARY_INCOME'),
('tx_205', 'kbc_user_4012', '2026-09-12', 'IKEA Anderlecht', 'Home & Furniture', 850.20, 'DEBIT', NULL),
('tx_301', 'kbc_user_9103', '2026-09-18', 'Virement Rachat Parts Société', 'Capital Gain / Business', 50000.00, 'CREDIT', 'EXCESS_LIQUIDITY_RECEIVED'),
('tx_302', 'kbc_user_9103', '2026-09-21', 'Golf Club de Waterloo', 'Leisure', 450.00, 'DEBIT', NULL),
('tx_303', 'kbc_user_9103', '2026-09-15', 'Van Damme Consulting', 'Business Income', 5600.00, 'CREDIT', 'MONTHLY_HONORARIA'),
('tx_304', 'kbc_user_9103', '2026-09-05', 'Galerie d Art Knokke', 'Art & Luxury', 3200.00, 'DEBIT', NULL);

-- 4. UPCOMING PAYMENTS DATA
INSERT INTO upcoming_payments (client_id, label, amount, due_date, status) VALUES
('kbc_user_2894', 'Loyer Résidence Flagey', 950.00, '2026-10-01', 'PLANNED'),
('kbc_user_2894', 'Assurance Habitation KBC', 38.00, '2026-10-05', 'PLANNED'),
('kbc_user_2894', 'Abonnement Gym Basic-Fit', 29.99, '2026-10-08', 'PLANNED'),
('kbc_user_4012', 'Prêt Hypothécaire KBC (Maison)', 1100.00, '2026-10-02', 'PLANNED'),
('kbc_user_4012', 'Assurance Auto (Volvo XC60)', 85.00, '2026-10-05', 'PLANNED'),
('kbc_user_4012', 'Facture Engie Électricité', 210.00, '2026-10-12', 'PLANNED'),
('kbc_user_9103', 'Assurance Hospitalisation KBC', 110.00, '2026-10-03', 'PLANNED'),
('kbc_user_9103', 'Prélèvements Fiscaux Anticipés', 1450.00, '2026-10-15', 'PLANNED');

-- 5. LOANS DATA
INSERT INTO loans (client_id, loan_type, initial_amount, remaining_balance, monthly_payment, status, start_date, end_date) VALUES
('kbc_user_2894', 'Prêt Étudiant KBC Master', 10000.00, 0.00, 0.00, 'FULLY_PAID', '2020-09-01', '2024-06-30'),
('kbc_user_4012', 'Prêt Hypothécaire KBC (Résidence Principale)', 280000.00, 138000.00, 1100.00, 'ACTIVE', '2014-01-01', '2034-12-31'),
('kbc_user_4012', 'Prêt Travaux Rénovation Cuisine', 25000.00, 0.00, 0.00, 'FULLY_PAID', '2020-02-01', '2025-01-15'),
('kbc_user_9103', 'Prêt Hypothécaire Villa Knokke', 220000.00, 0.00, 0.00, 'FULLY_PAID', '2001-10-01', '2021-09-30');

-- 6. INSURANCES DATA
INSERT INTO insurances (contract_code, client_id, insurance_type, monthly_premium, status, start_date, end_date) VALUES
('INS-7721', 'kbc_user_2894', 'Assurance Habitation Locataire KBC', 38.00, 'ACTIVE', '2022-09-01', NULL),
('INS-3310', 'kbc_user_4012', 'Assurance Habitation Propriétaire KBC', 65.00, 'ACTIVE', '2014-01-01', NULL),
('INS-3311', 'kbc_user_4012', 'Assurance Auto Omnium Volvo XC60', 85.00, 'ACTIVE', '2021-03-15', NULL),
('INS-9001', 'kbc_user_9103', 'Assurance Hospitalisation KBC Select', 110.00, 'ACTIVE', '2010-05-01', NULL),
('INS-9002', 'kbc_user_9103', 'Assurance Vie & Succession KBC Heritage', 250.00, 'ACTIVE', '2015-11-01', NULL);

-- 7. INVESTMENTS DATA
INSERT INTO investments (client_id, holding_name, holding_type, asset_value, return_ytd) VALUES
('kbc_user_2894', 'KBC Equity Fund World', 'Mutual Fund', 5500.00, '+12.4%'),
('kbc_user_2894', 'iShares S&P 500 ETF', 'ETF', 3000.00, '+14.1%'),
('kbc_user_4012', 'KBC Life Pension Plan', 'Pension Fund', 32000.00, '+6.8%'),
('kbc_user_4012', 'KBC Eco Fund Sustainable World', 'ESG Fund', 28000.00, '+8.2%'),
('kbc_user_9103', 'Obligations d État Belge 2028', 'Government Bonds', 120000.00, '+3.2%'),
('kbc_user_9103', 'KBC Capital Protected Portfolio', 'Structured Product', 80000.00, '+4.1%');

-- 8. AI PREDICTIONS & NUDGES DATA
INSERT INTO ai_predictions_nudges (nudge_id, client_id, priority, category, title, description, explainability_reason, confidence_score, status) VALUES
('nudge_01', 'kbc_user_2894', 'HIGH', 'Assurance Auto', 'Achat véhicule détecté — Assurance Auto KBC Proactive', 'Nous avons détecté un paiement de 18 500 € chez "BMW Garage Brussels". Assurez votre nouveau véhicule immédiatement avec 15% de réduction client KBC.', 'Paiement concessionnaire détecté le 28/09. Aucun contrat d assurance auto actif trouvé chez KBC.', 0.96, 'PENDING'),
('nudge_02', 'kbc_user_2894', 'HIGH', 'Prêt Hypothécaire', 'Préparation à votre futur projet immobilier', 'Vos revenus réguliers (4 200 €/mois) et votre capital disponible (48,5k €) vous permettent d emprunter jusqu à 320 000 €.', 'Dépense notaire détectée le 25/09 + Capacité d épargne élevée + 0 prêt en cours.', 0.89, 'PENDING'),
('nudge_03', 'kbc_user_4012', 'HIGH', 'Prêt Vert', 'Financement Rénovation Énergétique - Prêt Vert KBC', 'Financez le solde de vos panneaux solaires au taux préférentiel KBC Green.', 'Acompte EcoSolar détecté le 20/09 + Propriétaire maison individuelle.', 0.93, 'PENDING'),
('nudge_04', 'kbc_user_4012', 'MEDIUM', 'Épargne Études', 'Plan d épargne projet études supérieures', 'Paiement de frais universitaires VUB détecté. Anticipez le coût des études de vos enfants.', 'Paiement VUB Université le 22/09 + Enfants de 16-18 ans.', 0.85, 'PENDING'),
('nudge_05', 'kbc_user_9103', 'HIGH', 'Gestion de Patrimoine', 'Placement Épargne & Private Banking (50 000 €)', 'Influx de liquidités détecté le 18/09. Protégez votre capital contre l inflation avec une solution KBC à capital garanti.', 'Virement entrant de 50 000 € + Profil conservateur avec 0 dette.', 0.95, 'PENDING');

-- =========================================================
-- END OF SCRIPT
-- =========================================================
