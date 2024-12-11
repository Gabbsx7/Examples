create table
  public.examples (
    id uuid not null default extensions.uuid_generate_v4 (),
    "nfeNumber" text not null,
    "nfeSerialNumber" text not null,
    "accessKey" text not null,
    "issuedOn" text not null,
    "createdOn" text null,
    "totalInvoiceAmount" text not null,
    action text not null,
    xml_url text null,
    pdf_url text null,
    created_at timestamp with time zone null default now(),
    updated_at timestamp with time zone null default now(),
    type text null,
    "operationType" text null,
    description text null,
    nsu text null,
    "parentAccessKey" text null,
    "company_federalTaxNumber" text not null,
    company_id text not null,
    issuer_name text null,
    "issuer_federalTaxNumber" text null,
    buyer_name text null,
    "buyer_federalTaxNumber" text null,
    transportation_name text null,
    "transportation_federalTaxNumber" text null,
    "NfeId" text null,
    userwe_id uuid null,
    "Tipo" text null,
    dayofweek text null,
    constraint invoices_pkey primary key (id),
    constraint invoices_access_key_key unique ("accessKey"),
    constraint invoices_userwe_id_fkey foreign key (userwe_id) references "User" (id)
  ) tablespace pg_default;

create index if not exists idx_invoices_issue_date on public.invoices using btree ("issuedOn") tablespace pg_default;

create trigger trigger_verificar before insert on invoices for each row
execute function verificar_e_inserir ();

create trigger update_dayofweek_trigger before insert
or
update on invoices for each row
execute function update_dayofweek_sigla ();
