CREATE DATABASE whatsapp_bot;

-- CREATE THIS TABLE BEFORE ANY OTHER TABLE ELSE FOREIGN KEY REFERENCE ERROR WILL BE THROWN
CREATE TABLE IF NOT EXISTS response_collection (session_id uuid NOT NULL DEFAULT uuid_generate_v4(), whatsapp_id varchar, from_account varchar, account_name varchar, start_time datetime, update_time datetime, end_time datetime, age int, pincode int, occupation varchar, type_of_loan varchar, salary varchar, loan_amount varchar, duration varchar, final_decision varchar, PRIMARY KEY(session_id));

-- CREATE THIS TABLE BEFORE THE PROMPTS TABLE ELSE FOREIGN KEY REFERENCE ERROR WILL BE THROWN
CREATE TABLE IF NOT EXISTS active_sessions (whatsapp_id varchar NOT NULL, start_time datetime, update_time datetime, last_question_id varchar, session_id uuid, session_type varchar, PRIMARY KEY(whatsapp_id), CONSTRAINT fk_active_sessions FOREIGN KEY(session_id) REFERENCES response_collection(session_id));

CREATE TABLE IF NOT EXISTS resume_prompted (whatsapp_id varchar, CONSTRAINT fk_resume_prompted FOREIGN KEY(whatsapp_id) REFERENCES active_sessions(whatsapp_id));

CREATE TABLE IF NOT EXISTS verify_prompted (whatsapp_id varchar, CONSTRAINT fk_resume_prompted FOREIGN KEY(whatsapp_id) REFERENCES active_sessions(whatsapp_id));