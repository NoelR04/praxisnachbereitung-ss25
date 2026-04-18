-- TODO: Inventar-Schema für Tag 3
--
-- Legt hier euer Datenmodell für die Inventar-App an.
-- Vorschlag für die Reihenfolge:
--   1. Stammdaten-Tabellen (department, person, device_type, location)
--   2. device
--   3. assignment
--
-- Ergänzt anschließend kleine Seed-Daten, damit ihr eure Flows testen könnt.


create table if not exists department (
  department_id  serial primary key,
  name           text not null unique
);

create table if not exists device_type (
  device_type_id serial primary key,
  name           text not null unique
);

create table if not exists location (
  location_id    serial primary key,
  name           text not null unique
);

create table if not exists person (
  person_id      serial primary key,
  vorname        text not null,
  nachname       text not null,
  email          text not null unique,
  department_id  int not null references department(department_id) on delete restrict
);

create table if not exists device (
  device_id      serial primary key,
  serial_number  text not null unique,
  device_name    text not null,
  device_type_id int not null references device_type(device_type_id) on delete restrict,
  location_id    int not null references location(location_id) on delete restrict,
  created_at     timestamp not null default now()
);


create table if not exists assignment (
  assignment_id  serial primary key,
  device_id      int not null references device(device_id) on delete restrict,
  person_id      int not null references person(person_id) on delete restrict,
  issued_at      timestamp not null default now(),
  returned_at    timestamp,
  check (returned_at is null or returned_at >= issued_at)
);

-- nur eine aktive Ausleihe pro Gerät
create unique index if not exists uq_assignment_active_device
  on assignment (device_id)
  where returned_at is null;


insert into department (name) values
  ('IT'),
  ('Verwaltung'),
  ('Logistik')
on conflict (name) do nothing;

insert into device_type (name) values
  ('Laptop'),
  ('Monitor'),
  ('Handscanner')
on conflict (name) do nothing;

insert into location (name) values
  ('Gebäude E'),
  ('Gebäude F'),
  ('Gebäude H')
on conflict (name) do nothing;

insert into person (vorname, nachname, email, department_id) values
  ('Anna', 'Schmidt', 'anna.schmidt@example.com', 1),
  ('Ben', 'Müller', 'ben.mueller@example.com', 2),
  ('Clara', 'Weber', 'clara.weber@example.com', 3)
on conflict (email) do nothing;

insert into device (serial_number, device_name, device_type_id, location_id) values
  ('LAP-1001', 'Lenovo ThinkPad T14', 1, 1),
  ('MON-2001', 'Dell P2422H', 2, 2),
  ('SCAN-3001', 'Zebra DS2278', 3, 3)
on conflict (serial_number) do nothing;

insert into assignment (device_id, person_id, issued_at, returned_at)
select d.device_id, p.person_id, a.issued_at, a.returned_at
from (values
  ('LAP-1001', 'anna.schmidt@example.com', now() - interval '3 days', null),
  ('MON-2001', 'ben.mueller@example.com', now() - interval '10 days', now() - interval '2 days')
) as a(serial_number, email, issued_at, returned_at)
join device d on d.serial_number = a.serial_number
join person p on p.email = a.email
on conflict do nothing;