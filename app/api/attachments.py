import os
import shutil
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status, Response
from fastapi.responses import FileResponse
from typing import List
from sqlalchemy import select as sqlalchemy_select
from sqlmodel import Session
from app.models.attachment import Attachment
from app.models.ticket import Ticket
from app.api.users import get_current_user
from app.core.db import get_session

UPLOAD_ROOT = "attachments"  # katalog na pliki

router = APIRouter(prefix="/tickets", tags=["attachments"])

@router.post("/{ticket_id}/attachments", status_code=201)
async def upload_attachments(
    ticket_id: int,
    files: List[UploadFile] = File(...),
    user=Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Sprawdź czy ticket istnieje i czy user ma prawo do niego
    ticket = session.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Not found")
    if user.role == "client" and ticket.created_by != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    saved_attachments = []
    ticket_folder = os.path.join(UPLOAD_ROOT, str(ticket_id))
    os.makedirs(ticket_folder, exist_ok=True)

    for upload in files:
        filename = upload.filename
        file_path = os.path.join(ticket_folder, filename)
        # Zabezpieczenie przed nadpisaniem
        if os.path.exists(file_path):
            raise HTTPException(status_code=409, detail=f"File {filename} already exists")

        with open(file_path, "wb") as out_file:
            shutil.copyfileobj(upload.file, out_file)

        att = Attachment(
            ticket_id=ticket_id,
            filename=filename,
            content_type=upload.content_type,
            path=file_path
        )
        session.add(att)
        saved_attachments.append(filename)
    session.commit()
    return {"msg": "Pliki zapisane", "files": saved_attachments}

@router.get("/{ticket_id}/attachments")
def list_attachments(
    ticket_id: int,
    user=Depends(get_current_user),
    session: Session = Depends(get_session)
):
    ticket = session.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Not found")
    if user.role == "client" and ticket.created_by != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    attachments = session.exec(sqlalchemy_select(Attachment).where(Attachment.ticket_id == ticket_id)).all()
    return [
        {
            "id": att.id,
            "filename": att.filename,
            "content_type": att.content_type,
            "uploaded_at": att.uploaded_at
        }
        for att in attachments
    ]

@router.get("/attachments/{attachment_id}")
def download_attachment(
    attachment_id: int,
    user=Depends(get_current_user),
    session: Session = Depends(get_session)
):
    att = session.get(Attachment, attachment_id)
    if not att:
        raise HTTPException(status_code=404, detail="Not found")
    ticket = session.get(Ticket, att.ticket_id)
    if user.role == "client" and ticket.created_by != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return FileResponse(
        att.path,
        media_type=att.content_type,
        filename=att.filename
    )

@router.delete("/attachments/{attachment_id}")
def delete_attachment(
    attachment_id: int,
    user=Depends(get_current_user),
    session: Session = Depends(get_session)
):
    att = session.get(Attachment, attachment_id)
    if not att:
        raise HTTPException(status_code=404, detail="Not found")
    ticket = session.get(Ticket, att.ticket_id)
    if user.role == "client" and ticket.created_by != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    try:
        if os.path.exists(att.path):
            os.remove(att.path)
    except Exception:
        pass
    session.delete(att)
    session.commit()
    return {"msg": "Załącznik usunięty"}
