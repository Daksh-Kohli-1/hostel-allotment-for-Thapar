import enum
import uuid
from datetime import datetime
from sqlalchemy import String, Integer, Boolean, ForeignKey, Enum, DateTime, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


class RoleEnum(str, enum.Enum):
    student = "student"
    admin = "admin"


class GenderEnum(str, enum.Enum):
    male = "male"
    female = "female"
    other = "other"


class GroupStatus(str, enum.Enum):
    forming = "forming"           # still adding members
    prefs_submitted = "prefs_submitted"
    reserved = "reserved"         # awaiting payment
    confirmed = "confirmed"
    expired = "expired"


class BookingStatus(str, enum.Enum):
    reserved = "reserved"
    confirmed = "confirmed"
    released = "released"
    admin_override = "admin_override"


class PaymentStatus(str, enum.Enum):
    pending = "pending"
    paid = "paid"
    failed = "failed"


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    name: Mapped[str] = mapped_column(String(120))
    roll_no: Mapped[str] = mapped_column(String(30), unique=True)
    email: Mapped[str] = mapped_column(String(150), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[RoleEnum] = mapped_column(Enum(RoleEnum), default=RoleEnum.student)
    gender: Mapped[GenderEnum] = mapped_column(Enum(GenderEnum), default=GenderEnum.other)
    year: Mapped[int] = mapped_column(Integer, default=1)
    branch: Mapped[str] = mapped_column(String(80), default="")
    contact: Mapped[str] = mapped_column(String(20), default="")
    group_id: Mapped[str | None] = mapped_column(ForeignKey("groups.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    group: Mapped["Group"] = relationship("Group", back_populates="members", foreign_keys=[group_id])


class Group(Base):
    __tablename__ = "groups"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    code: Mapped[str] = mapped_column(String(10), unique=True)
    leader_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"))
    size_limit: Mapped[int] = mapped_column(Integer, default=4)
    status: Mapped[GroupStatus] = mapped_column(Enum(GroupStatus), default=GroupStatus.forming)
    booking_ready_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)  # FCFS timestamp
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    members: Mapped[list["User"]] = relationship("User", back_populates="group", foreign_keys=[User.group_id])
    preferences: Mapped[list["Preference"]] = relationship("Preference", back_populates="group", cascade="all, delete-orphan")
    booking: Mapped["Booking"] = relationship("Booking", back_populates="group", uselist=False)


class Hostel(Base):
    __tablename__ = "hostels"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    name: Mapped[str] = mapped_column(String(120))
    gender: Mapped[GenderEnum] = mapped_column(Enum(GenderEnum))
    year: Mapped[int] = mapped_column(Integer)

    floors: Mapped[list["Floor"]] = relationship("Floor", back_populates="hostel", cascade="all, delete-orphan")


class Floor(Base):
    __tablename__ = "floors"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    hostel_id: Mapped[str] = mapped_column(String, ForeignKey("hostels.id"))
    floor_number: Mapped[int] = mapped_column(Integer)

    hostel: Mapped["Hostel"] = relationship("Hostel", back_populates="floors")
    clusters: Mapped[list["Cluster"]] = relationship("Cluster", back_populates="floor", cascade="all, delete-orphan")

    __table_args__ = (UniqueConstraint("hostel_id", "floor_number", name="uq_hostel_floor"),)


class Cluster(Base):
    __tablename__ = "clusters"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    floor_id: Mapped[str] = mapped_column(String, ForeignKey("floors.id"))
    cluster_number: Mapped[int] = mapped_column(Integer)

    floor: Mapped["Floor"] = relationship("Floor", back_populates="clusters")
    rooms: Mapped[list["Room"]] = relationship("Room", back_populates="cluster", cascade="all, delete-orphan")

    __table_args__ = (UniqueConstraint("floor_id", "cluster_number", name="uq_floor_cluster"),)


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    cluster_id: Mapped[str] = mapped_column(String, ForeignKey("clusters.id"))
    room_label: Mapped[str] = mapped_column(String(2))  # "A" or "B" (position within the cluster)
    room_number: Mapped[int] = mapped_column(Integer, default=0)  # real-world room number, e.g. 101, 158
    capacity: Mapped[int] = mapped_column(Integer, default=2)
    occupied_count: Mapped[int] = mapped_column(Integer, default=0)

    cluster: Mapped["Cluster"] = relationship("Cluster", back_populates="rooms")

    __table_args__ = (UniqueConstraint("cluster_id", "room_label", name="uq_cluster_room_label"),)


class Preference(Base):
    __tablename__ = "preferences"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    group_id: Mapped[str] = mapped_column(String, ForeignKey("groups.id"))
    cluster_id: Mapped[str] = mapped_column(String, ForeignKey("clusters.id"))
    rank: Mapped[int] = mapped_column(Integer)  # 1 = most preferred

    group: Mapped["Group"] = relationship("Group", back_populates="preferences")
    cluster: Mapped["Cluster"] = relationship("Cluster")


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    group_id: Mapped[str] = mapped_column(String, ForeignKey("groups.id"), unique=True)
    cluster_id: Mapped[str] = mapped_column(String, ForeignKey("clusters.id"))
    room_ids: Mapped[str] = mapped_column(String)  # comma-separated room ids allotted
    status: Mapped[BookingStatus] = mapped_column(Enum(BookingStatus), default=BookingStatus.reserved)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    group: Mapped["Group"] = relationship("Group", back_populates="booking")
    cluster: Mapped["Cluster"] = relationship("Cluster")


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"))
    group_id: Mapped[str] = mapped_column(String, ForeignKey("groups.id"))
    # Simulated payment gateway reference (swap for a real Razorpay order/payment id later).
    transaction_ref: Mapped[str] = mapped_column(String(100), nullable=True)
    amount: Mapped[int] = mapped_column(Integer)
    status: Mapped[PaymentStatus] = mapped_column(Enum(PaymentStatus), default=PaymentStatus.pending)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship("User")
