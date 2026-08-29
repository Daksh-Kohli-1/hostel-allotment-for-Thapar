"""
Seeds the database with:
  1. All 6 hostels (3 boys, 3 girls), each with 8 floors, 29 clusters/floor,
     58 rooms/floor, numbered the way Thapar actually numbers them
     (Floor 1 = 101-158, Floor 2 = 201-258, ... Floor 8 = 801-858).
  2. A handful of demo users, groups, payments and bookings so the app has
     something to look at immediately after `docker compose up`.

Room numbering / clustering rule
---------------------------------
Each floor has 58 rooms, paired into 29 two-room clusters (a cluster =
2 rooms sharing a washroom, 2 seats per room = 4 seats per cluster).
Per the brief, connected rooms within a cluster share the same number
parity - odd rooms pair with odd, even rooms pair with even (e.g. Room 101
is connected to Room 103, not 102). On a 58-room floor there are 29 odd
room numbers and 29 even room numbers - an odd count on each side - so 14
odd-odd clusters + 14 even-even clusters use up 56 rooms, and the two
numbers left over (one odd, one even) are paired into a final 29th
cluster. That keeps the total at exactly 29 clusters / 58 rooms per floor
while staying as close as possible to the "same parity connects" rule.
"""
from datetime import datetime, timezone, timedelta

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.models.models import (
    User, Hostel, Floor, Cluster, Room, Group, Preference, Booking, Payment,
    RoleEnum, GenderEnum, GroupStatus, BookingStatus, PaymentStatus,
)

FLOORS_PER_HOSTEL = 8
ROOMS_PER_FLOOR = 58
CLUSTERS_PER_FLOOR = 29
HOSTEL_FEE = 60000

BOYS_HOSTELS = ["Agira Hall", "Neeram Hall", "Anantan Hall"]
GIRLS_HOSTELS = ["Hostel PG", "Pavani Hall", "Dhriti Hall"]


def generate_room_number_pairs(floor_number: int) -> list[tuple[int, int]]:
    """Return the 29 (room_a_number, room_b_number) pairs for one floor."""
    base = floor_number * 100
    odds = list(range(base + 1, base + 58, 2))   # 29 numbers: base+1 .. base+57
    evens = list(range(base + 2, base + 59, 2))  # 29 numbers: base+2 .. base+58

    pairs: list[tuple[int, int]] = []
    for i in range(0, 28, 2):          # 14 odd-odd clusters
        pairs.append((odds[i], odds[i + 1]))
    for i in range(0, 28, 2):          # 14 even-even clusters
        pairs.append((evens[i], evens[i + 1]))
    pairs.append((odds[28], evens[28]))  # 29th cluster: the two leftovers
    return pairs


async def _build_hostel(db, name: str, gender: GenderEnum) -> Hostel:
    hostel = Hostel(name=name, gender=gender, year=0)  # year=0 -> open to all years
    db.add(hostel)
    await db.flush()

    for floor_num in range(1, FLOORS_PER_HOSTEL + 1):
        floor = Floor(hostel_id=hostel.id, floor_number=floor_num)
        db.add(floor)
        await db.flush()

        room_pairs = generate_room_number_pairs(floor_num)
        for cluster_num, (num_a, num_b) in enumerate(room_pairs, start=1):
            cluster = Cluster(floor_id=floor.id, cluster_number=cluster_num)
            db.add(cluster)
            await db.flush()

            db.add(Room(cluster_id=cluster.id, room_label="A", room_number=num_a, capacity=2, occupied_count=0))
            db.add(Room(cluster_id=cluster.id, room_label="B", room_number=num_b, capacity=2, occupied_count=0))

    await db.flush()
    return hostel


async def _get_cluster(db, hostel: Hostel, floor_number: int, cluster_number: int) -> Cluster:
    result = await db.execute(
        select(Cluster)
        .join(Floor, Cluster.floor_id == Floor.id)
        .where(Floor.hostel_id == hostel.id, Floor.floor_number == floor_number, Cluster.cluster_number == cluster_number)
    )
    return result.scalar_one()


async def _get_rooms(db, cluster: Cluster) -> dict[str, Room]:
    result = await db.execute(select(Room).where(Room.cluster_id == cluster.id))
    return {r.room_label: r for r in result.scalars().all()}


def _make_student(name, roll_no, email, gender, year, branch, contact) -> User:
    return User(
        name=name,
        roll_no=roll_no,
        email=email,
        password_hash=hash_password("Pass@123"),
        role=RoleEnum.student,
        gender=gender,
        year=year,
        branch=branch,
        contact=contact,
    )


async def seed_initial_data():
    async with AsyncSessionLocal() as db:
        existing = await db.execute(select(Hostel.id).limit(1))
        if existing.scalar_one_or_none():
            return  # already seeded

        # ---------- Hostels (3 boys + 3 girls, 8 floors / 29 clusters each) ----------
        hostels: dict[str, Hostel] = {}
        for name in BOYS_HOSTELS:
            hostels[name] = await _build_hostel(db, name, GenderEnum.male)
        for name in GIRLS_HOSTELS:
            hostels[name] = await _build_hostel(db, name, GenderEnum.female)
        await db.commit()

        # ---------- Admin ----------
        admin = User(
            name="System Admin",
            roll_no="ADMIN001",
            email="admin@thapar.edu",
            password_hash=hash_password("Admin@123"),
            role=RoleEnum.admin,
            gender=GenderEnum.other,
            year=0,
            branch="Administration",
            contact="0000000000",
        )
        db.add(admin)

        # ---------- Demo students ----------
        # 1) Solo student who has ALREADY PAID and been allotted a room -
        #    demonstrates single students booking without a group.
        solo_boy = _make_student("Karan Mehta", "102303001", "karan.mehta@thapar.edu", GenderEnum.male, 2, "Computer Science", "9999900001")
        # 2) A 3-member group where only 2 members have paid so far -
        #    demonstrates that allotment does not wait for the whole group.
        leader_3 = _make_student("Ishaan Kapoor", "102303002", "ishaan.kapoor@thapar.edu", GenderEnum.male, 1, "Electronics", "9999900002")
        member_3a = _make_student("Rohan Sharma", "102303003", "rohan.sharma@thapar.edu", GenderEnum.male, 1, "Electronics", "9999900003")
        member_3b_unpaid = _make_student("Aditya Verma", "102303004", "aditya.verma@thapar.edu", GenderEnum.male, 1, "Mechanical", "9999900004")
        # 3) A full 4-member group, all paid, cluster fully booked & confirmed.
        leader_4 = _make_student("Yash Gupta", "102303005", "yash.gupta@thapar.edu", GenderEnum.male, 3, "Computer Science", "9999900005")
        member_4a = _make_student("Dev Malhotra", "102303006", "dev.malhotra@thapar.edu", GenderEnum.male, 3, "Computer Science", "9999900006")
        member_4b = _make_student("Arjun Nair", "102303007", "arjun.nair@thapar.edu", GenderEnum.male, 3, "Civil", "9999900007")
        member_4c = _make_student("Vivaan Joshi", "102303008", "vivaan.joshi@thapar.edu", GenderEnum.male, 3, "Civil", "9999900008")
        # 4) Solo female student, paid & allotted, in a girls hostel.
        solo_girl = _make_student("Ananya Singh", "102303009", "ananya.singh@thapar.edu", GenderEnum.female, 2, "Computer Science", "9999900009")
        # 5) A brand-new student who has just signed up: no group, no payment, no booking yet.
        fresh_student = _make_student("Priya Reddy", "102303010", "priya.reddy@thapar.edu", GenderEnum.female, 1, "Electronics", "9999900010")

        db.add_all([
            solo_boy, leader_3, member_3a, member_3b_unpaid,
            leader_4, member_4a, member_4b, member_4c,
            solo_girl, fresh_student,
        ])
        await db.flush()

        now = datetime.now(timezone.utc)

        # ---- Scenario 1: solo boy, paid, allotted a single seat ----
        agira = hostels["Agira Hall"]
        cluster_solo = await _get_cluster(db, agira, 1, 2)
        rooms_solo = await _get_rooms(db, cluster_solo)
        rooms_solo["A"].occupied_count = 1

        group_solo = Group(code="SOLOK1", leader_id=solo_boy.id, status=GroupStatus.confirmed, booking_ready_at=now)
        db.add(group_solo)
        await db.flush()
        solo_boy.group_id = group_solo.id

        db.add(Preference(group_id=group_solo.id, cluster_id=cluster_solo.id, rank=1))
        db.add(Payment(user_id=solo_boy.id, group_id=group_solo.id, transaction_ref="SIMPAY-DEMO0001", amount=HOSTEL_FEE, status=PaymentStatus.paid))
        db.add(Booking(
            group_id=group_solo.id, cluster_id=cluster_solo.id, room_ids=rooms_solo["A"].id,
            status=BookingStatus.confirmed, confirmed_at=now,
        ))

        # ---- Scenario 2: 3-member group, only 2 paid, allotted for 2 seats already ----
        cluster_partial = await _get_cluster(db, agira, 2, 5)
        rooms_partial = await _get_rooms(db, cluster_partial)
        rooms_partial["A"].occupied_count = 2  # the 2 members who already paid

        group_partial = Group(code="TRIO001", leader_id=leader_3.id, size_limit=4, status=GroupStatus.confirmed, booking_ready_at=now)
        db.add(group_partial)
        await db.flush()
        leader_3.group_id = group_partial.id
        member_3a.group_id = group_partial.id
        member_3b_unpaid.group_id = group_partial.id  # in the group, hasn't paid yet

        db.add(Preference(group_id=group_partial.id, cluster_id=cluster_partial.id, rank=1))
        db.add(Payment(user_id=leader_3.id, group_id=group_partial.id, transaction_ref="SIMPAY-DEMO0002", amount=HOSTEL_FEE, status=PaymentStatus.paid))
        db.add(Payment(user_id=member_3a.id, group_id=group_partial.id, transaction_ref="SIMPAY-DEMO0003", amount=HOSTEL_FEE, status=PaymentStatus.paid))
        db.add(Payment(user_id=member_3b_unpaid.id, group_id=group_partial.id, amount=HOSTEL_FEE, status=PaymentStatus.pending))
        db.add(Booking(
            group_id=group_partial.id, cluster_id=cluster_partial.id, room_ids=rooms_partial["A"].id,
            status=BookingStatus.confirmed, confirmed_at=now,
        ))

        # ---- Scenario 3: full 4-member group, all paid, cluster full ----
        cluster_full = await _get_cluster(db, agira, 3, 10)
        rooms_full = await _get_rooms(db, cluster_full)
        rooms_full["A"].occupied_count = 2
        rooms_full["B"].occupied_count = 2

        group_full = Group(code="QUAD001", leader_id=leader_4.id, size_limit=4, status=GroupStatus.confirmed, booking_ready_at=now)
        db.add(group_full)
        await db.flush()
        for u in (leader_4, member_4a, member_4b, member_4c):
            u.group_id = group_full.id

        db.add(Preference(group_id=group_full.id, cluster_id=cluster_full.id, rank=1))
        for i, u in enumerate((leader_4, member_4a, member_4b, member_4c), start=4):
            db.add(Payment(user_id=u.id, group_id=group_full.id, transaction_ref=f"SIMPAY-DEMO000{i}", amount=HOSTEL_FEE, status=PaymentStatus.paid))
        db.add(Booking(
            group_id=group_full.id, cluster_id=cluster_full.id,
            room_ids=f"{rooms_full['A'].id},{rooms_full['B'].id}",
            status=BookingStatus.confirmed, confirmed_at=now,
        ))

        # ---- Scenario 4: solo girl, paid, allotted a single seat ----
        pavani = hostels["Pavani Hall"]
        cluster_girl = await _get_cluster(db, pavani, 1, 1)
        rooms_girl = await _get_rooms(db, cluster_girl)
        rooms_girl["A"].occupied_count = 1

        group_girl = Group(code="SOLOA1", leader_id=solo_girl.id, status=GroupStatus.confirmed, booking_ready_at=now)
        db.add(group_girl)
        await db.flush()
        solo_girl.group_id = group_girl.id

        db.add(Preference(group_id=group_girl.id, cluster_id=cluster_girl.id, rank=1))
        db.add(Payment(user_id=solo_girl.id, group_id=group_girl.id, transaction_ref="SIMPAY-DEMO0008", amount=HOSTEL_FEE, status=PaymentStatus.paid))
        db.add(Booking(
            group_id=group_girl.id, cluster_id=cluster_girl.id, room_ids=rooms_girl["A"].id,
            status=BookingStatus.confirmed, confirmed_at=now,
        ))

        # fresh_student is intentionally left with no group/payment/booking.

        await db.commit()
