from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict


# ---------- Auth ----------
class SignupRequest(BaseModel):
    name: str
    roll_no: str
    email: EmailStr
    password: str
    gender: str
    year: int
    branch: str
    contact: str = ""


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    roll_no: str
    email: str
    role: str
    gender: str
    year: int
    branch: str
    contact: str
    group_id: str | None = None


# ---------- Groups ----------
class GroupCreateResponse(BaseModel):
    id: str
    code: str
    leader_id: str
    status: str


class GroupJoinRequest(BaseModel):
    code: str


class GroupMemberOut(BaseModel):
    id: str
    name: str
    roll_no: str
    payment_status: str = "pending"


class GroupOut(BaseModel):
    id: str
    code: str
    leader_id: str
    status: str
    members: list[GroupMemberOut]


# ---------- Hostel / Floor / Cluster / Room ----------
class RoomOut(BaseModel):
    id: str
    room_label: str
    room_number: int
    capacity: int
    occupied_count: int


class ClusterOut(BaseModel):
    id: str
    cluster_number: int
    rooms: list[RoomOut]
    state: str  # "empty" | "partial" | "full"


class FloorOut(BaseModel):
    id: str
    floor_number: int
    clusters: list[ClusterOut]


class HostelOut(BaseModel):
    id: str
    name: str
    gender: str
    year: int
    floors: list[FloorOut]


# ---------- Preferences ----------
class PreferenceItem(BaseModel):
    cluster_id: str
    rank: int


class PreferenceSubmitRequest(BaseModel):
    preferences: list[PreferenceItem]  # 3 to 5 items


# ---------- Booking ----------
class BookingOut(BaseModel):
    id: str
    group_id: str
    cluster_id: str
    room_ids: list[str]
    status: str
    created_at: datetime
    confirmed_at: datetime | None = None


# ---------- Payment (simulated gateway) ----------
class PayFeeResponse(BaseModel):
    message: str
    transaction_ref: str
    amount: int
    allocation: dict | None = None  # allocation/expansion result triggered by this payment, if any


class PaymentStatusOut(BaseModel):
    user_id: str
    name: str
    status: str


# ---------- Admin ----------
class AdminReassignRequest(BaseModel):
    group_id: str
    new_cluster_id: str
