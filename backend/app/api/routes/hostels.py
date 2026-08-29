from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.models import Hostel, Floor, Cluster, Room
from app.schemas.schemas import HostelOut, FloorOut, ClusterOut, RoomOut
from app.api.deps import get_current_user

router = APIRouter(prefix="/api/hostels", tags=["hostels"])


def _cluster_state_label(rooms: list[Room]) -> str:
    total = sum(r.occupied_count for r in rooms)
    if total == 0:
        return "empty"
    if total >= 4:
        return "full"
    return "partial"


@router.get("", response_model=list[HostelOut])
async def list_hostels(db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    result = await db.execute(
        select(Hostel).options(
            selectinload(Hostel.floors).selectinload(Floor.clusters).selectinload(Cluster.rooms)
        )
    )
    hostels = result.scalars().unique().all()

    output = []
    for h in hostels:
        floors_out = []
        for f in sorted(h.floors, key=lambda x: x.floor_number):
            clusters_out = []
            for c in sorted(f.clusters, key=lambda x: x.cluster_number):
                rooms_sorted = sorted(c.rooms, key=lambda r: r.room_number)
                clusters_out.append(
                    ClusterOut(
                        id=c.id,
                        cluster_number=c.cluster_number,
                        rooms=[
                            RoomOut(
                                id=r.id,
                                room_label=r.room_label,
                                room_number=r.room_number,
                                capacity=r.capacity,
                                occupied_count=r.occupied_count,
                            )
                            for r in rooms_sorted
                        ],
                        state=_cluster_state_label(rooms_sorted),
                    )
                )
            floors_out.append(FloorOut(id=f.id, floor_number=f.floor_number, clusters=clusters_out))
        output.append(HostelOut(id=h.id, name=h.name, gender=h.gender.value, year=h.year, floors=floors_out))

    return output
