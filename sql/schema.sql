--
-- PostgreSQL database dump
--

\restrict M1qfi6ivJI7ZKnQOcSHgitba2golE3bSh93NMF4JIKDhLaq8YyLtO7UYSUfy2EL

-- Dumped from database version 18.6
-- Dumped by pg_dump version 18.6

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
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
-- Name: accounts; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.accounts (
    account_id integer NOT NULL,
    customer_id integer NOT NULL,
    account_type text NOT NULL,
    currency character(3) NOT NULL
);


--
-- Name: customers; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.customers (
    customer_id integer NOT NULL,
    customer_name text NOT NULL,
    city text NOT NULL,
    registration_date date NOT NULL
);


--
-- Name: transactions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.transactions (
    transaction_id integer NOT NULL,
    account_id integer NOT NULL,
    transaction_type text NOT NULL,
    amount numeric(12,2) NOT NULL,
    currency character(3) NOT NULL,
    status text NOT NULL,
    transaction_date timestamp without time zone NOT NULL,
    CONSTRAINT transactions_amount_check CHECK ((amount > (0)::numeric)),
    CONSTRAINT transactions_currency_check CHECK ((currency = 'KZT'::bpchar)),
    CONSTRAINT transactions_status_check CHECK ((status = ANY (ARRAY['completed'::text, 'failed'::text]))),
    CONSTRAINT transactions_transaction_type_check CHECK ((transaction_type = ANY (ARRAY['payment'::text, 'deposit'::text])))
);


--
-- Name: daily_transactions; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.daily_transactions AS
 SELECT (transaction_date)::date AS transaction_day,
    currency,
    count(*) AS total_operations,
    count(*) FILTER (WHERE (status = 'failed'::text)) AS failed_operations,
    COALESCE(sum(amount) FILTER (WHERE ((status = 'completed'::text) AND (transaction_type = 'payment'::text))), (0)::numeric) AS payment_amount,
    COALESCE(sum(amount) FILTER (WHERE ((status = 'completed'::text) AND (transaction_type = 'deposit'::text))), (0)::numeric) AS deposit_amount
   FROM public.transactions
  GROUP BY ((transaction_date)::date), currency;


--
-- Name: accounts accounts_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.accounts
    ADD CONSTRAINT accounts_pkey PRIMARY KEY (account_id);


--
-- Name: customers customers_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.customers
    ADD CONSTRAINT customers_pkey PRIMARY KEY (customer_id);


--
-- Name: transactions transactions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT transactions_pkey PRIMARY KEY (transaction_id);


--
-- Name: accounts accounts_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.accounts
    ADD CONSTRAINT accounts_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customers(customer_id);


--
-- Name: transactions transactions_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT transactions_account_id_fkey FOREIGN KEY (account_id) REFERENCES public.accounts(account_id);


--
-- PostgreSQL database dump complete
--

\unrestrict M1qfi6ivJI7ZKnQOcSHgitba2golE3bSh93NMF4JIKDhLaq8YyLtO7UYSUfy2EL

