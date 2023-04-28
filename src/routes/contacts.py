from typing import List

from fastapi import Depends, HTTPException, status, Path, APIRouter, Query
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session
from fastapi_limiter import FastAPILimiter

from src.database.db import get_db
from src.database.models import User
from src.schemas import ContactResponse, ContactModel
from src.repository import contacts as repos_contacts
from src.services.auth import auth_service

router = APIRouter(prefix='/contacts', tags=['contacts'])


@router.get('/all', response_model=List[ContactResponse], description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def get_contacts(db: Session = Depends(get_db),
                       current_user: User = Depends(auth_service.get_current_user)):
    contacts = await repos_contacts.get_contacts(current_user, db)
    if contacts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not Found')
    return contacts


@router.get('/bday', response_model=List[ContactResponse], description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def get_nearest_bdays(db: Session = Depends(get_db),
                            current_user: User = Depends(auth_service.get_current_user)):
    contacts = await repos_contacts.get_nearest_bdays(current_user, db)
    if contacts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not Found')
    return contacts


@router.get('/{contact_id}', response_model=ContactResponse, description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def get_contact(contact_id: int = Path(ge=1), db: Session = Depends(get_db),
                      current_user: User = Depends(auth_service.get_current_user)):
    contact = await repos_contacts.get_contact(current_user, contact_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not Found')
    return contact


@router.get('/{field_name}/{field_value}', response_model=List[ContactResponse],
            description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def get_contacts_by_field(field_name: str, field_value: str, db: Session = Depends(get_db),
                                current_user: User = Depends(auth_service.get_current_user)):
    contacts = await repos_contacts.get_contact_by_field(current_user, field_name, field_value, db)

    if not contacts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not Found')
    return contacts


@router.post('/', response_model=ContactResponse, status_code=status.HTTP_201_CREATED,
             description='No more than 10 requests per minute',
             dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def create_contact(body: ContactModel, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    contact = await repos_contacts.create(current_user, body, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Wrong Data')
    return contact


@router.put('/{contact_id}', response_model=ContactResponse, description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def update_contact(body: ContactModel,
                         contact_id: int = Path(ge=1),
                         db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    contact = await repos_contacts.update(current_user, contact_id, body, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not Found')
    return contact


@router.delete('/{contact_id}', status_code=status.HTTP_204_NO_CONTENT,
               description='No more than 10 requests per minute',
               dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def remove(contact_id, db: Session = Depends(get_db),
                 current_user: User = Depends(auth_service.get_current_user)):
    contact = await repos_contacts.remove(current_user, contact_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not Found')
    return contact
