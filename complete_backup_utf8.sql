--
-- PostgreSQL database dump
--

-- Dumped from database version 16.3
-- Dumped by pg_dump version 16.3

-- Started on 2024-11-14 19:24:12

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 236 (class 1259 OID 33487)
-- Name: admins; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.admins (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    password character varying(255) NOT NULL
);


ALTER TABLE public.admins OWNER TO postgres;

--
-- TOC entry 235 (class 1259 OID 33486)
-- Name: admins_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.admins_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.admins_id_seq OWNER TO postgres;

--
-- TOC entry 4971 (class 0 OID 0)
-- Dependencies: 235
-- Name: admins_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.admins_id_seq OWNED BY public.admins.id;


--
-- TOC entry 220 (class 1259 OID 25289)
-- Name: appointments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.appointments (
    id integer NOT NULL,
    doctor_id integer,
    patient_name character varying(100),
    appointment_date timestamp without time zone,
    status character varying(20) DEFAULT 'pending'::character varying,
    patient_id integer,
    time_slot time without time zone,
    specialty character varying(100),
    reason text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    doctor_memo text
);


ALTER TABLE public.appointments OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 25288)
-- Name: appointments_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.appointments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.appointments_id_seq OWNER TO postgres;

--
-- TOC entry 4972 (class 0 OID 0)
-- Dependencies: 219
-- Name: appointments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.appointments_id_seq OWNED BY public.appointments.id;


--
-- TOC entry 232 (class 1259 OID 33382)
-- Name: beds; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.beds (
    id integer NOT NULL,
    room_id integer,
    bed_number character varying(10) NOT NULL,
    status character varying(20) DEFAULT 'available'::character varying,
    patient_id integer
);


ALTER TABLE public.beds OWNER TO postgres;

--
-- TOC entry 231 (class 1259 OID 33381)
-- Name: beds_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.beds_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.beds_id_seq OWNER TO postgres;

--
-- TOC entry 4973 (class 0 OID 0)
-- Dependencies: 231
-- Name: beds_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.beds_id_seq OWNED BY public.beds.id;


--
-- TOC entry 234 (class 1259 OID 33395)
-- Name: bills; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.bills (
    id integer NOT NULL,
    patient_id integer,
    appointment_id integer,
    total_amount numeric(10,2) NOT NULL,
    status character varying(20) DEFAULT 'unpaid'::character varying,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.bills OWNER TO postgres;

--
-- TOC entry 233 (class 1259 OID 33394)
-- Name: bills_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.bills_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.bills_id_seq OWNER TO postgres;

--
-- TOC entry 4974 (class 0 OID 0)
-- Dependencies: 233
-- Name: bills_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.bills_id_seq OWNED BY public.bills.id;


--
-- TOC entry 222 (class 1259 OID 25322)
-- Name: chat_rooms; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.chat_rooms (
    id integer NOT NULL,
    doctor_id integer,
    patient_id integer,
    appointment_id integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.chat_rooms OWNER TO postgres;

--
-- TOC entry 221 (class 1259 OID 25321)
-- Name: chat_rooms_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.chat_rooms_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.chat_rooms_id_seq OWNER TO postgres;

--
-- TOC entry 4975 (class 0 OID 0)
-- Dependencies: 221
-- Name: chat_rooms_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.chat_rooms_id_seq OWNED BY public.chat_rooms.id;


--
-- TOC entry 228 (class 1259 OID 33357)
-- Name: doctor_applications; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.doctor_applications (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    email character varying(100) NOT NULL,
    specialization character varying(100) NOT NULL,
    experience integer NOT NULL,
    resume_path character varying(255) NOT NULL,
    similarity_score double precision,
    status character varying(20) DEFAULT 'pending'::character varying
);


ALTER TABLE public.doctor_applications OWNER TO postgres;

--
-- TOC entry 227 (class 1259 OID 33356)
-- Name: doctor_applications_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.doctor_applications_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.doctor_applications_id_seq OWNER TO postgres;

--
-- TOC entry 4976 (class 0 OID 0)
-- Dependencies: 227
-- Name: doctor_applications_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.doctor_applications_id_seq OWNED BY public.doctor_applications.id;


--
-- TOC entry 218 (class 1259 OID 25242)
-- Name: doctors; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.doctors (
    id integer NOT NULL,
    name character varying(100),
    specialty character varying(100),
    email character varying(100),
    password character varying(255)
);


ALTER TABLE public.doctors OWNER TO postgres;

--
-- TOC entry 217 (class 1259 OID 25241)
-- Name: doctors_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.doctors_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.doctors_id_seq OWNER TO postgres;

--
-- TOC entry 4977 (class 0 OID 0)
-- Dependencies: 217
-- Name: doctors_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.doctors_id_seq OWNED BY public.doctors.id;


--
-- TOC entry 224 (class 1259 OID 25347)
-- Name: messages; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.messages (
    id integer NOT NULL,
    chat_room_id integer,
    sender_type character varying(10),
    sender_id integer,
    message text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    is_read boolean DEFAULT false,
    CONSTRAINT messages_sender_type_check CHECK (((sender_type)::text = ANY ((ARRAY['doctor'::character varying, 'patient'::character varying])::text[])))
);


ALTER TABLE public.messages OWNER TO postgres;

--
-- TOC entry 223 (class 1259 OID 25346)
-- Name: messages_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.messages_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.messages_id_seq OWNER TO postgres;

--
-- TOC entry 4978 (class 0 OID 0)
-- Dependencies: 223
-- Name: messages_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.messages_id_seq OWNED BY public.messages.id;


--
-- TOC entry 226 (class 1259 OID 25364)
-- Name: notifications; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.notifications (
    id integer NOT NULL,
    user_id integer NOT NULL,
    user_type character varying(10) NOT NULL,
    message text NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    is_read boolean DEFAULT false
);


ALTER TABLE public.notifications OWNER TO postgres;

--
-- TOC entry 225 (class 1259 OID 25363)
-- Name: notifications_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.notifications_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.notifications_id_seq OWNER TO postgres;

--
-- TOC entry 4979 (class 0 OID 0)
-- Dependencies: 225
-- Name: notifications_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.notifications_id_seq OWNED BY public.notifications.id;


--
-- TOC entry 216 (class 1259 OID 25231)
-- Name: patients; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.patients (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    email character varying(100) NOT NULL,
    phone character varying(20) NOT NULL,
    password character varying(255) NOT NULL,
    gender character varying(20) NOT NULL,
    medical_record text,
    profile_pic bytea
);


ALTER TABLE public.patients OWNER TO postgres;

--
-- TOC entry 215 (class 1259 OID 25230)
-- Name: patients_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.patients_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.patients_id_seq OWNER TO postgres;

--
-- TOC entry 4980 (class 0 OID 0)
-- Dependencies: 215
-- Name: patients_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.patients_id_seq OWNED BY public.patients.id;


--
-- TOC entry 230 (class 1259 OID 33374)
-- Name: rooms; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.rooms (
    id integer NOT NULL,
    room_number character varying(10) NOT NULL,
    room_type character varying(50) NOT NULL,
    capacity integer NOT NULL,
    status character varying(20) DEFAULT 'available'::character varying
);


ALTER TABLE public.rooms OWNER TO postgres;

--
-- TOC entry 229 (class 1259 OID 33373)
-- Name: rooms_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.rooms_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.rooms_id_seq OWNER TO postgres;

--
-- TOC entry 4981 (class 0 OID 0)
-- Dependencies: 229
-- Name: rooms_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.rooms_id_seq OWNED BY public.rooms.id;


--
-- TOC entry 4760 (class 2604 OID 33490)
-- Name: admins id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.admins ALTER COLUMN id SET DEFAULT nextval('public.admins_id_seq'::regclass);


--
-- TOC entry 4740 (class 2604 OID 25292)
-- Name: appointments id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.appointments ALTER COLUMN id SET DEFAULT nextval('public.appointments_id_seq'::regclass);


--
-- TOC entry 4755 (class 2604 OID 33385)
-- Name: beds id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.beds ALTER COLUMN id SET DEFAULT nextval('public.beds_id_seq'::regclass);


--
-- TOC entry 4757 (class 2604 OID 33398)
-- Name: bills id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bills ALTER COLUMN id SET DEFAULT nextval('public.bills_id_seq'::regclass);


--
-- TOC entry 4743 (class 2604 OID 25325)
-- Name: chat_rooms id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_rooms ALTER COLUMN id SET DEFAULT nextval('public.chat_rooms_id_seq'::regclass);


--
-- TOC entry 4751 (class 2604 OID 33360)
-- Name: doctor_applications id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.doctor_applications ALTER COLUMN id SET DEFAULT nextval('public.doctor_applications_id_seq'::regclass);


--
-- TOC entry 4739 (class 2604 OID 25245)
-- Name: doctors id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.doctors ALTER COLUMN id SET DEFAULT nextval('public.doctors_id_seq'::regclass);


--
-- TOC entry 4745 (class 2604 OID 25350)
-- Name: messages id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.messages ALTER COLUMN id SET DEFAULT nextval('public.messages_id_seq'::regclass);


--
-- TOC entry 4748 (class 2604 OID 25367)
-- Name: notifications id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notifications ALTER COLUMN id SET DEFAULT nextval('public.notifications_id_seq'::regclass);


--
-- TOC entry 4738 (class 2604 OID 25234)
-- Name: patients id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.patients ALTER COLUMN id SET DEFAULT nextval('public.patients_id_seq'::regclass);


--
-- TOC entry 4753 (class 2604 OID 33377)
-- Name: rooms id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rooms ALTER COLUMN id SET DEFAULT nextval('public.rooms_id_seq'::regclass);


--
-- TOC entry 4965 (class 0 OID 33487)
-- Dependencies: 236
-- Data for Name: admins; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.admins (id, name, password) VALUES (1, 'Eshwanth Karti T R', 'Tr@310305');


--
-- TOC entry 4949 (class 0 OID 25289)
-- Dependencies: 220
-- Data for Name: appointments; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.appointments (id, doctor_id, patient_name, appointment_date, status, patient_id, time_slot, specialty, reason, created_at, doctor_memo) VALUES (62, 5, 'Eshwanth Karti T R', '2024-10-03 00:00:00', 'pending', 1, '10:00:00', 'Orthopedics', NULL, '2024-10-23 02:54:02.122807', NULL);
INSERT INTO public.appointments (id, doctor_id, patient_name, appointment_date, status, patient_id, time_slot, specialty, reason, created_at, doctor_memo) VALUES (61, 4, 'Eshwanth Karti T R', '2024-10-04 00:00:00', 'accepted', 1, '09:00:00', 'Cardiology', NULL, '2024-10-22 13:58:45.981782', 'I pyaar you');


--
-- TOC entry 4961 (class 0 OID 33382)
-- Dependencies: 232
-- Data for Name: beds; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.beds (id, room_id, bed_number, status, patient_id) VALUES (2, 2, '1', 'available', NULL);
INSERT INTO public.beds (id, room_id, bed_number, status, patient_id) VALUES (3, 2, '2', 'available', NULL);
INSERT INTO public.beds (id, room_id, bed_number, status, patient_id) VALUES (4, 3, '1', 'available', NULL);
INSERT INTO public.beds (id, room_id, bed_number, status, patient_id) VALUES (5, 4, '1', 'available', NULL);
INSERT INTO public.beds (id, room_id, bed_number, status, patient_id) VALUES (6, 4, '2', 'available', NULL);
INSERT INTO public.beds (id, room_id, bed_number, status, patient_id) VALUES (7, 5, '1', 'available', NULL);
INSERT INTO public.beds (id, room_id, bed_number, status, patient_id) VALUES (8, 5, '2', 'available', 1);
INSERT INTO public.beds (id, room_id, bed_number, status, patient_id) VALUES (9, 5, '3', 'available', 4);
INSERT INTO public.beds (id, room_id, bed_number, status, patient_id) VALUES (1, 1, '1', 'occupied', 1);


--
-- TOC entry 4963 (class 0 OID 33395)
-- Dependencies: 234
-- Data for Name: bills; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- TOC entry 4951 (class 0 OID 25322)
-- Dependencies: 222
-- Data for Name: chat_rooms; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.chat_rooms (id, doctor_id, patient_id, appointment_id, created_at) VALUES (3, 1, 1, NULL, '2024-10-12 17:35:55.199529');
INSERT INTO public.chat_rooms (id, doctor_id, patient_id, appointment_id, created_at) VALUES (6, 4, 4, NULL, '2024-10-15 19:24:47.585953');
INSERT INTO public.chat_rooms (id, doctor_id, patient_id, appointment_id, created_at) VALUES (8, 4, 1, NULL, '2024-10-21 18:20:51.231345');
INSERT INTO public.chat_rooms (id, doctor_id, patient_id, appointment_id, created_at) VALUES (9, 5, 1, NULL, '2024-10-21 18:28:27.55939');


--
-- TOC entry 4957 (class 0 OID 33357)
-- Dependencies: 228
-- Data for Name: doctor_applications; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.doctor_applications (id, name, email, specialization, experience, resume_path, similarity_score, status) VALUES (2, 'Eshwanth Karti T R', 'eshwanthkartitr@gmail.com', 'Heart', 566, 'uploads\2407.04620v2.pdf', 0.0680340901017189, 'accepted');
INSERT INTO public.doctor_applications (id, name, email, specialization, experience, resume_path, similarity_score, status) VALUES (3, 'LordEgg33', 'Lord@gmail.com', 'Heart', 800, 'uploads\BSP_1streview.pdf', 0.25512009859085083, 'accepted');


--
-- TOC entry 4947 (class 0 OID 25242)
-- Dependencies: 218
-- Data for Name: doctors; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.doctors (id, name, specialty, email, password) VALUES (4, 'Dr. Smith', 'Cardiology', 'dr.smith@example.com', 'hashed_password_3');
INSERT INTO public.doctors (id, name, specialty, email, password) VALUES (5, 'Dr. Johnson', 'Orthopedics', 'dr.johnson@example.com', 'hashed_password_4');
INSERT INTO public.doctors (id, name, specialty, email, password) VALUES (1, 'Eshwanth Karti T R', 'Cardiology', 'eshwanthkartitr@gmail.com', '400');
INSERT INTO public.doctors (id, name, specialty, email, password) VALUES (7, 'LordEgg33', 'Lord@gmail.com', 'Heart', '800');


--
-- TOC entry 4953 (class 0 OID 25347)
-- Dependencies: 224
-- Data for Name: messages; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.messages (id, chat_room_id, sender_type, sender_id, message, created_at, is_read) VALUES (3, 3, 'patient', 1, 'Hello, Doctor!', '2024-10-12 17:38:28.639894', false);
INSERT INTO public.messages (id, chat_room_id, sender_type, sender_id, message, created_at, is_read) VALUES (4, 3, 'doctor', 1, 'Hello, how can I help you?', '2024-10-12 17:38:28.639894', false);
INSERT INTO public.messages (id, chat_room_id, sender_type, sender_id, message, created_at, is_read) VALUES (13, 6, 'doctor', 4, 'Hi bro who are you', '2024-10-15 19:24:47.585953', false);
INSERT INTO public.messages (id, chat_room_id, sender_type, sender_id, message, created_at, is_read) VALUES (27, 9, 'patient', 1, 'Hi', '2024-10-21 18:41:05.254911', false);
INSERT INTO public.messages (id, chat_room_id, sender_type, sender_id, message, created_at, is_read) VALUES (28, 3, 'doctor', 1, 'Why are you looking for my guidance', '2024-10-21 20:11:30.047152', false);
INSERT INTO public.messages (id, chat_room_id, sender_type, sender_id, message, created_at, is_read) VALUES (29, 3, 'patient', 1, 'because i have a severe problem', '2024-10-21 20:11:50.303873', false);


--
-- TOC entry 4955 (class 0 OID 25364)
-- Dependencies: 226
-- Data for Name: notifications; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.notifications (id, user_id, user_type, message, created_at, is_read) VALUES (1, 1, 'patient', 'Your appointment with Dr. Smith is confirmed.', '2024-10-12 17:36:50.696065', false);
INSERT INTO public.notifications (id, user_id, user_type, message, created_at, is_read) VALUES (2, 2, 'patient', 'Your appointment with Dr. Johnson is confirmed.', '2024-10-12 17:36:50.696065', false);


--
-- TOC entry 4945 (class 0 OID 25231)
-- Dependencies: 216
-- Data for Name: patients; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.patients (id, name, email, phone, password, gender, medical_record, profile_pic) VALUES (1, 'Eshwanth Karti T R', 'eshwanthkartitr@gmail.com', '08438967169', 'scrypt:32768:8:1$7oFgpgYZD9h33SzT$b45bf2467ca200f128904b671e86174ebef2b5599410ae3e98c14f97cc57d01257a83e0fe27ce2c8273679e0584996d32c83174e83f0e00fea5c006d863440a7', 'Male', 'Hi i am getting ocd on drugs', NULL);
INSERT INTO public.patients (id, name, email, phone, password, gender, medical_record, profile_pic) VALUES (4, 'Eshwanth Karti Eshwanth', 'eshu@gmail.com', '08438967169', 'scrypt:32768:8:1$i3w9EwC1XfbxYhP6$b2df6aa41dd0f0d83a5c3c2b65390539163a0bc3308ac3096bcc70bef3c535ce2f4037176ea1310d833aa770a9f439da836eb44d1b859bec490b964b833f881b', 'Male', 'Hi i am good on drugs', NULL);
INSERT INTO public.patients (id, name, email, phone, password, gender, medical_record, profile_pic) VALUES (5, 'LordEgg33', 'eshuva@gmail.com', '09438967169', 'scrypt:32768:8:1$YSG2VwJIGMPkwMms$773baad94d57a2f97a8cb9b87611536785de44fb811d34eeb0fad7ffd3ad8bfcea4a06c33a2fa6055431f6babbe64018b249e8f1b3ffe0a8ac4fb3c430d979a7', 'Male', 'I want to become an employee', NULL);


--
-- TOC entry 4959 (class 0 OID 33374)
-- Dependencies: 230
-- Data for Name: rooms; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.rooms (id, room_number, room_type, capacity, status) VALUES (1, '101', 'Single', 1, 'available');
INSERT INTO public.rooms (id, room_number, room_type, capacity, status) VALUES (2, '102', 'Double', 2, 'available');
INSERT INTO public.rooms (id, room_number, room_type, capacity, status) VALUES (3, '201', 'Single', 1, 'available');
INSERT INTO public.rooms (id, room_number, room_type, capacity, status) VALUES (4, '202', 'Double', 2, 'available');
INSERT INTO public.rooms (id, room_number, room_type, capacity, status) VALUES (5, '301', 'Suite', 3, 'available');


--
-- TOC entry 4982 (class 0 OID 0)
-- Dependencies: 235
-- Name: admins_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.admins_id_seq', 1, true);


--
-- TOC entry 4983 (class 0 OID 0)
-- Dependencies: 219
-- Name: appointments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.appointments_id_seq', 62, true);


--
-- TOC entry 4984 (class 0 OID 0)
-- Dependencies: 231
-- Name: beds_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.beds_id_seq', 9, true);


--
-- TOC entry 4985 (class 0 OID 0)
-- Dependencies: 233
-- Name: bills_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.bills_id_seq', 1, false);


--
-- TOC entry 4986 (class 0 OID 0)
-- Dependencies: 221
-- Name: chat_rooms_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.chat_rooms_id_seq', 9, true);


--
-- TOC entry 4987 (class 0 OID 0)
-- Dependencies: 227
-- Name: doctor_applications_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.doctor_applications_id_seq', 3, true);


--
-- TOC entry 4988 (class 0 OID 0)
-- Dependencies: 217
-- Name: doctors_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.doctors_id_seq', 8, true);


--
-- TOC entry 4989 (class 0 OID 0)
-- Dependencies: 223
-- Name: messages_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.messages_id_seq', 29, true);


--
-- TOC entry 4990 (class 0 OID 0)
-- Dependencies: 225
-- Name: notifications_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.notifications_id_seq', 2, true);


--
-- TOC entry 4991 (class 0 OID 0)
-- Dependencies: 215
-- Name: patients_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.patients_id_seq', 5, true);


--
-- TOC entry 4992 (class 0 OID 0)
-- Dependencies: 229
-- Name: rooms_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.rooms_id_seq', 5, true);


--
-- TOC entry 4791 (class 2606 OID 33492)
-- Name: admins admins_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.admins
    ADD CONSTRAINT admins_pkey PRIMARY KEY (id);


--
-- TOC entry 4771 (class 2606 OID 25295)
-- Name: appointments appointments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.appointments
    ADD CONSTRAINT appointments_pkey PRIMARY KEY (id);


--
-- TOC entry 4787 (class 2606 OID 33388)
-- Name: beds beds_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.beds
    ADD CONSTRAINT beds_pkey PRIMARY KEY (id);


--
-- TOC entry 4789 (class 2606 OID 33402)
-- Name: bills bills_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bills
    ADD CONSTRAINT bills_pkey PRIMARY KEY (id);


--
-- TOC entry 4773 (class 2606 OID 25330)
-- Name: chat_rooms chat_rooms_doctor_id_patient_id_appointment_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_rooms
    ADD CONSTRAINT chat_rooms_doctor_id_patient_id_appointment_id_key UNIQUE (doctor_id, patient_id, appointment_id);


--
-- TOC entry 4775 (class 2606 OID 25328)
-- Name: chat_rooms chat_rooms_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_rooms
    ADD CONSTRAINT chat_rooms_pkey PRIMARY KEY (id);


--
-- TOC entry 4781 (class 2606 OID 33367)
-- Name: doctor_applications doctor_applications_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.doctor_applications
    ADD CONSTRAINT doctor_applications_email_key UNIQUE (email);


--
-- TOC entry 4783 (class 2606 OID 33365)
-- Name: doctor_applications doctor_applications_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.doctor_applications
    ADD CONSTRAINT doctor_applications_pkey PRIMARY KEY (id);


--
-- TOC entry 4767 (class 2606 OID 25251)
-- Name: doctors doctors_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.doctors
    ADD CONSTRAINT doctors_email_key UNIQUE (email);


--
-- TOC entry 4769 (class 2606 OID 25249)
-- Name: doctors doctors_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.doctors
    ADD CONSTRAINT doctors_pkey PRIMARY KEY (id);


--
-- TOC entry 4777 (class 2606 OID 25357)
-- Name: messages messages_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_pkey PRIMARY KEY (id);


--
-- TOC entry 4779 (class 2606 OID 25373)
-- Name: notifications notifications_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_pkey PRIMARY KEY (id);


--
-- TOC entry 4763 (class 2606 OID 25240)
-- Name: patients patients_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.patients
    ADD CONSTRAINT patients_email_key UNIQUE (email);


--
-- TOC entry 4765 (class 2606 OID 25238)
-- Name: patients patients_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.patients
    ADD CONSTRAINT patients_pkey PRIMARY KEY (id);


--
-- TOC entry 4785 (class 2606 OID 33380)
-- Name: rooms rooms_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rooms
    ADD CONSTRAINT rooms_pkey PRIMARY KEY (id);


--
-- TOC entry 4792 (class 2606 OID 25296)
-- Name: appointments appointments_doctor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.appointments
    ADD CONSTRAINT appointments_doctor_id_fkey FOREIGN KEY (doctor_id) REFERENCES public.doctors(id);


--
-- TOC entry 4793 (class 2606 OID 25313)
-- Name: appointments appointments_patient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.appointments
    ADD CONSTRAINT appointments_patient_id_fkey FOREIGN KEY (patient_id) REFERENCES public.patients(id);


--
-- TOC entry 4798 (class 2606 OID 33389)
-- Name: beds beds_room_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.beds
    ADD CONSTRAINT beds_room_id_fkey FOREIGN KEY (room_id) REFERENCES public.rooms(id);


--
-- TOC entry 4799 (class 2606 OID 33408)
-- Name: bills bills_appointment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bills
    ADD CONSTRAINT bills_appointment_id_fkey FOREIGN KEY (appointment_id) REFERENCES public.appointments(id);


--
-- TOC entry 4800 (class 2606 OID 33403)
-- Name: bills bills_patient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bills
    ADD CONSTRAINT bills_patient_id_fkey FOREIGN KEY (patient_id) REFERENCES public.patients(id);


--
-- TOC entry 4794 (class 2606 OID 25341)
-- Name: chat_rooms chat_rooms_appointment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_rooms
    ADD CONSTRAINT chat_rooms_appointment_id_fkey FOREIGN KEY (appointment_id) REFERENCES public.appointments(id);


--
-- TOC entry 4795 (class 2606 OID 25331)
-- Name: chat_rooms chat_rooms_doctor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_rooms
    ADD CONSTRAINT chat_rooms_doctor_id_fkey FOREIGN KEY (doctor_id) REFERENCES public.doctors(id);


--
-- TOC entry 4796 (class 2606 OID 25336)
-- Name: chat_rooms chat_rooms_patient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_rooms
    ADD CONSTRAINT chat_rooms_patient_id_fkey FOREIGN KEY (patient_id) REFERENCES public.patients(id);


--
-- TOC entry 4797 (class 2606 OID 25358)
-- Name: messages messages_chat_room_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_chat_room_id_fkey FOREIGN KEY (chat_room_id) REFERENCES public.chat_rooms(id);


-- Completed on 2024-11-14 19:24:16

--
-- PostgreSQL database dump complete
--

