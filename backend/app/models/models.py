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
    father_name: Mapped[str] = mapped_column(String(120), default="")
    mother_name: Mapped[str] = mapped_column(String(120), default="")
    emergency_contact_name: Mapped[str] = mapped_column(String(120), default="")
    emergency_contact_phone: Mapped[str] = mapped_column(String(30), default="")
    aadhaar_no: Mapped[str] = mapped_column(String(30), default="")
    address: Mapped[str] = mapped_column(String(255), default="")
    dob: Mapped[str] = mapped_column(String(30), default="")
    vehicle_type: Mapped[str] = mapped_column(String(50), default="")
    vehicle_model: Mapped[str] = mapped_column(String(50), default="")
    vehicle_reg_no: Mapped[str] = mapped_column(String(50), default="")
    program: Mapped[str] = mapped_column(String(80), default="B.Tech")
    department: Mapped[str] = mapped_column(String(80), default="Computer Engineering")
    section: Mapped[str] = mapped_column(String(20), default="COE-2")
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
    user: Mapped["User"] = relationship("User")


class ServiceRequest(Base):
    __tablename__ = "service_requests"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"))
    category: Mapped[str] = mapped_column(String(50))  # Maintenance, Cleaning, Gate pass, etc.
    subject: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(String(1000))
    priority: Mapped[str] = mapped_column(String(20), default="Medium")  # Low, Medium, High, Emergency
    status: Mapped[str] = mapped_column(String(30), default="Submitted")  # Submitted, In progress, Approved, Completed, Rejected
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship("User")


class MessFeedback(Base):
    __tablename__ = "mess_feedbacks"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"))
    rating: Mapped[int] = mapped_column(Integer)  # 1 to 5
    comment: Mapped[str] = mapped_column(String(500), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class PollVote(Base):
    __tablename__ = "poll_votes"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"))
    poll_id: Mapped[str] = mapped_column(String(50), default="weekly_menu_poll")
    option_index: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (UniqueConstraint("user_id", "poll_id", name="uq_user_poll_vote"),)


class VisitorRequest(Base):
    __tablename__ = "visitor_requests"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"))
    visitor_name: Mapped[str] = mapped_column(String(120))
    phone: Mapped[str] = mapped_column(String(20))
    relationship: Mapped[str] = mapped_column(String(50))
    visit_date: Mapped[str] = mapped_column(String(30))
    expected_arrival: Mapped[str] = mapped_column(String(30))
    expected_departure: Mapped[str] = mapped_column(String(30))
    status: Mapped[str] = mapped_column(String(30), default="Pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class LeaveRequest(Base):
    __tablename__ = "leave_requests"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"))
    request_type: Mapped[str] = mapped_column(String(30), default="Leave")  # Leave, Day Out, Late Entry
    destination: Mapped[str] = mapped_column(String(200))
    reason: Mapped[str] = mapped_column(String(500))
    start_date: Mapped[str] = mapped_column(String(30))
    end_date: Mapped[str] = mapped_column(String(30))
    expected_return: Mapped[str] = mapped_column(String(30))
    emergency_contact: Mapped[str] = mapped_column(String(30))
    status: Mapped[str] = mapped_column(String(30), default="Approved")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AmenityBooking(Base):
    __tablename__ = "amenity_bookings"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"))
    amenity_name: Mapped[str] = mapped_column(String(100))  # Study Room, Gym, Laundry, etc.
    booking_date: Mapped[str] = mapped_column(String(30))
    time_slot: Mapped[str] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(30), default="Confirmed")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(120))
    message: Mapped[str] = mapped_column(String(500))
    category: Mapped[str] = mapped_column(String(30), default="General")  # Payment, Notice, Maintenance, Leave, System
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
