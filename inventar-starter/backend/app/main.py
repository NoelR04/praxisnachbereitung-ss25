from fastapi import FastAPI, Request, Query, HTTPException, status, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
import os
from datetime import datetime
import psycopg
from psycopg.errors import UniqueViolation, ForeignKeyViolation
from .db import get_conn
from .models import DeviceCreate, AssignmentCreate, AssignmentReturn
import paho.mqtt.client as mqtt

app = FastAPI(title="Inventar Starter", version="0.1.0")
templates = Jinja2Templates(
    directory=os.path.join(os.path.dirname(__file__), "templates")
)

MQTT_HOST = os.getenv("MQTT_HOST", "mqtt")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))


def mqtt_client() -> mqtt.Client:
    c = mqtt.Client()
    c.connect(MQTT_HOST, MQTT_PORT, keepalive=30)
    return c


def publish_mqtt_event(topic: str, payload: str) -> None:
    try:
        c = mqtt_client()
        c.publish(topic, payload, qos=0, retain=False)
        c.disconnect()
    except Exception:
        pass


@app.get("/health")
async def health():
    db_state = "ok"
    mqtt_state = "ok"

    try:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("select 1")
            cur.fetchone()
    except Exception as ex:
        db_state = f"error:{type(ex).__name__}"

    try:
        c = mqtt_client()
        c.disconnect()
    except Exception as ex:
        mqtt_state = f"degraded:{type(ex).__name__}"

    return {
        "status": "ok" if db_state == "ok" else "degraded",
        "db": db_state,
        "mqtt": mqtt_state,
    }


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "title": "Inventar Starter"},
    )


@app.get("/inventory", response_class=HTMLResponse)
async def inventory_page(request: Request):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            select
                d.device_id,
                d.serial_number,
                d.note,
                dt.name as device_type,
                l.name as location,
                case
                    when exists (
                        select 1
                        from assignment a
                        where a.device_id = d.device_id
                          and a.returned_at is null
                    ) then 'ausgeliehen'
                    else 'frei'
                end as status
            from device d
            join device_type dt on dt.device_type_id = d.device_type_id
            join location l on l.location_id = d.location_id
            order by d.device_id
        """)
        devices = cur.fetchall()

        cur.execute("""
            select device_type_id, name
            from device_type
            order by name
        """)
        device_types = cur.fetchall()

        cur.execute("""
            select location_id, name
            from location
            order by name
        """)
        locations = cur.fetchall()

        cur.execute("""
            select person_id, vorname, nachname
            from person
            order by nachname, vorname
        """)
        persons = cur.fetchall()

        cur.execute("""
            select
                d.device_id,
                d.serial_number
            from device d
            where not exists (
                select 1
                from assignment a
                where a.device_id = d.device_id
                  and a.returned_at is null
            )
            order by d.serial_number
        """)
        available_devices = cur.fetchall()

        cur.execute("""
            select
                a.assignment_id,
                d.serial_number,
                p.vorname,
                p.nachname,
                a.issued_at
            from assignment a
            join device d on d.device_id = a.device_id
            join person p on p.person_id = a.person_id
            where a.returned_at is null
            order by a.issued_at desc
        """)
        active_assignments = cur.fetchall()

    return templates.TemplateResponse(
        "inventory.html",
        {
            "request": request,
            "title": "Inventar",
            "devices": devices,
            "device_types": device_types,
            "locations": locations,
            "persons": persons,
            "available_devices": available_devices,
            "active_assignments": active_assignments,
        },
    )


@app.post("/inventory/devices")
async def create_device_from_form(
    serial_number: str = Form(...),
    device_type_id: int = Form(...),
    location_id: int = Form(...),
    note: str | None = Form(None),
):
    try:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("""
                insert into device (serial_number, device_type_id, location_id, note)
                values (%s, %s, %s, %s)
            """, (serial_number, device_type_id, location_id, note))
    except UniqueViolation:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="serial_number existiert bereits",
        )
    except ForeignKeyViolation:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="device_type_id oder location_id ist ungültig",
        )

    return RedirectResponse(url="/inventory", status_code=303)


@app.post("/inventory/assignments")
async def create_assignment_from_form(
    device_id: int = Form(...),
    person_id: int = Form(...),
):
    try:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("""
                insert into assignment (device_id, person_id)
                values (%s, %s)
                returning assignment_id
            """, (device_id, person_id))
            assignment = cur.fetchone()

        publish_mqtt_event(
            "inventory/assignments/issued",
            f'{{"assignment_id": {assignment["assignment_id"]}, "device_id": {device_id}, "person_id": {person_id}}}',
        )
    except UniqueViolation:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="device hat bereits eine aktive Ausleihe",
        )
    except ForeignKeyViolation:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="device_id oder person_id ist ungültig",
        )

    return RedirectResponse(url="/inventory", status_code=303)


@app.post("/inventory/assignments/{assignment_id}/return")
async def return_assignment_from_form(assignment_id: int):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            select assignment_id, device_id, person_id, issued_at, returned_at
            from assignment
            where assignment_id = %s
        """, (assignment_id,))
        assignment = cur.fetchone()

        if not assignment:
            raise HTTPException(status_code=404, detail="assignment nicht gefunden")

        if assignment["returned_at"] is not None:
            raise HTTPException(
                status_code=409,
                detail="assignment wurde bereits zurückgegeben",
            )

        returned_at = datetime.now()

        if returned_at < assignment["issued_at"]:
            raise HTTPException(
                status_code=422,
                detail="returned_at darf nicht vor issued_at liegen",
            )

        cur.execute("""
            update assignment
            set returned_at = %s
            where assignment_id = %s
            returning assignment_id, device_id, person_id
        """, (returned_at, assignment_id))
        updated = cur.fetchone()

    publish_mqtt_event(
        "inventory/assignments/returned",
        f'{{"assignment_id": {updated["assignment_id"]}, "device_id": {updated["device_id"]}, "person_id": {updated["person_id"]}}}',
    )

    return RedirectResponse(url="/inventory", status_code=303)


@app.post("/mqtt/publish")
async def mqtt_publish(topic: str = Query(...), payload: str = Query(...)):
    c = mqtt_client()
    c.publish(topic, payload, qos=0, retain=False)
    c.disconnect()
    return {"ok": True, "topic": topic, "payload": payload}


@app.get("/devices")
async def get_devices():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            select
                device_id,
                serial_number,
                device_type_id,
                location_id,
                note,
                created_at::text as created_at
            from device
            order by device_id
        """)
        return cur.fetchall()


@app.post("/devices", status_code=status.HTTP_201_CREATED)
async def create_device(payload: DeviceCreate):
    try:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("""
                insert into device (serial_number, device_type_id, location_id, note)
                values (%s, %s, %s, %s)
                returning
                    device_id,
                    serial_number,
                    device_type_id,
                    location_id,
                    note,
                    created_at::text as created_at
            """, (
                payload.serial_number,
                payload.device_type_id,
                payload.location_id,
                payload.note,
            ))
            return cur.fetchone()
    except UniqueViolation:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="serial_number existiert bereits",
        )
    except ForeignKeyViolation:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="device_type_id oder location_id ist ungültig",
        )


@app.get("/assignments/active")
async def get_active_assignments():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            select
                assignment_id,
                device_id,
                person_id,
                issued_at::text as issued_at,
                returned_at::text as returned_at
            from assignment
            where returned_at is null
            order by issued_at desc
        """)
        return cur.fetchall()


@app.post("/assignments", status_code=status.HTTP_201_CREATED)
async def create_assignment(payload: AssignmentCreate):
    issued_at = payload.issued_at or datetime.now().isoformat()

    try:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("""
                insert into assignment (device_id, person_id, issued_at)
                values (%s, %s, %s)
                returning
                    assignment_id,
                    device_id,
                    person_id,
                    issued_at::text as issued_at,
                    returned_at::text as returned_at
            """, (
                payload.device_id,
                payload.person_id,
                issued_at,
            ))
            assignment = cur.fetchone()

        publish_mqtt_event(
            "inventory/assignments/issued",
            f'{{"assignment_id": {assignment["assignment_id"]}, "device_id": {assignment["device_id"]}, "person_id": {assignment["person_id"]}}}',
        )

        return assignment
    except UniqueViolation:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="device hat bereits eine aktive Ausleihe",
        )
    except ForeignKeyViolation:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="device_id oder person_id ist ungültig",
        )
    except psycopg.Error as ex:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Fehler beim Erstellen der Ausleihe: {type(ex).__name__}",
        )


@app.post("/assignments/{assignment_id}/return")
async def return_assignment_api(assignment_id: int, payload: AssignmentReturn):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            select
                assignment_id,
                device_id,
                person_id,
                issued_at,
                returned_at
            from assignment
            where assignment_id = %s
        """, (assignment_id,))
        assignment = cur.fetchone()

        if not assignment:
            raise HTTPException(status_code=404, detail="assignment nicht gefunden")

        if assignment["returned_at"] is not None:
            raise HTTPException(
                status_code=409,
                detail="assignment wurde bereits zurückgegeben",
            )

        returned_at_str = payload.returned_at or datetime.now().isoformat()

        try:
            returned_at_dt = datetime.fromisoformat(returned_at_str)
        except ValueError:
            raise HTTPException(
                status_code=422,
                detail="returned_at ist kein gültiges ISO-Datum",
            )

        if returned_at_dt < assignment["issued_at"]:
            raise HTTPException(
                status_code=422,
                detail="returned_at darf nicht vor issued_at liegen",
            )

        cur.execute("""
            update assignment
            set returned_at = %s
            where assignment_id = %s
            returning
                assignment_id,
                device_id,
                person_id,
                issued_at::text as issued_at,
                returned_at::text as returned_at
        """, (returned_at_dt, assignment_id))
        updated = cur.fetchone()

    publish_mqtt_event(
        "inventory/assignments/returned",
        f'{{"assignment_id": {updated["assignment_id"]}, "device_id": {updated["device_id"]}, "person_id": {updated["person_id"]}}}',
    )

    return updated