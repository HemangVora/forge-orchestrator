from datetime import datetime

from sqlalchemy.orm import Session

from app.models.worker import Worker
from app.schemas.worker import WorkerRegisterRequest, WorkerRegisterResponse


class WorkerService:
    def __init__(self, db: Session):
        self.db = db

    def register(self, payload: WorkerRegisterRequest) -> WorkerRegisterResponse:
        worker = self.db.query(Worker).filter(Worker.hostname == payload.hostname).first()
        now = datetime.utcnow()

        if worker is None:
            worker = Worker(
                hostname=payload.hostname,
                capabilities=payload.capabilities,
                status="online",
                last_heartbeat=now,
            )
            self.db.add(worker)
        else:
            worker.capabilities = payload.capabilities
            worker.status = "online"
            worker.last_heartbeat = now

        self.db.commit()
        self.db.refresh(worker)

        return WorkerRegisterResponse(
            worker_id=str(worker.id),
            hostname=worker.hostname,
            status=worker.status,
        )

    def heartbeat(self, hostname: str) -> WorkerRegisterResponse | None:
        worker = self.db.query(Worker).filter(Worker.hostname == hostname).first()
        if worker is None:
            return None

        worker.last_heartbeat = datetime.utcnow()
        worker.status = "online"
        self.db.commit()
        self.db.refresh(worker)

        return WorkerRegisterResponse(
            worker_id=str(worker.id),
            hostname=worker.hostname,
            status=worker.status,
        )
