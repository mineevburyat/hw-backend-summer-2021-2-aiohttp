import typing
from hashlib import sha256
from typing import Optional

from app.base.base_accessor import BaseAccessor
from app.admin.models import Admin
from aiohttp_session import get_session

if typing.TYPE_CHECKING:
    from app.web.app import Application


class AdminAccessor(BaseAccessor):
    def __init__(self, app):
        self.app: Optional['Application'] = None

    async def connect(self, app: 'Application'):
        # TODO: создать админа по данным в config.yml здесь
        
        #!! DONE
        self.app = app
        try:
            self.app.database.admins
            self.app.database.questions
            self.app.database.themes
        except KeyError:
            self.app.database.admins = []
            self.app.database.questions = []
            self.app.database.themes = []

        admin = await self.create_admin(self.app.config.admin.email, self.app.config.admin.password)
        self.app.database.admins.append(admin)

        # print('connect to database')
        

    async def disconnect(self, _: 'Application'):
        self.app = None
        # print('disconnect from database')


    # async def create_session(self):
    #     session = await get_session(self.request)
    #     session['token'] = self.request.app.config.session.key

    
    # async def clear_session(self):
    #     session = await get_session(self.request)
    #     session['token'] = None


    async def get_by_email(self, email: str) -> Optional[Admin]:
        for admin in self.app.database.admins:
            if admin.email == email:
                return admin
        return None
        

    async def create_admin(self, email: str, password: str) -> Admin:
        hashed_password = sha256(password.encode('utf-8')).hexdigest()
        id = self.app.database.next_admin_id
        admin = Admin(id=id, email=email, password=hashed_password)
        self.app.database.admins.append(admin)

        return admin



       
