from hashlib import sha256
import json
from http.client import HTTPException
from aiohttp_apispec import request_schema, response_schema, querystring_schema
from aiohttp.web_exceptions import HTTPNotFound, HTTPUnauthorized, HTTPForbidden, HTTPBadRequest
# random
from aiohttp_session import get_session, new_session
from marshmallow import ValidationError
from app.admin.schemes import AdminResponseSchema, AdminSchema
from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.utils import check_basic_auth, json_response


class AdminLoginView(View):
    @request_schema(AdminSchema)
    @response_schema(AdminResponseSchema, 200)
    async def post(self):
        data = await self.request.json()
        try:
            email = data['email']
            password = data['password']
        except KeyError:
            raise HTTPBadRequest
        
        hashed_password = sha256(password.encode()).hexdigest()
                
        admin = await self.request.app.store.admins.get_by_email(email=email)
        if not admin:
            raise HTTPForbidden
        
        session = await get_session(self.request)
        session['token'] = self.request.app.config.session.key

        if email == admin.email and hashed_password == admin.password:
            session['admin'] = {}
            session['admin'].setdefault('id', admin.id)
            session['admin'].setdefault('email', admin.email)

            raw_admin = AdminResponseSchema().dump(admin)           
            return json_response(data=raw_admin)
        else:
            raise HTTPForbidden
            


class AdminCurrentView(AuthRequiredMixin, View):
    @querystring_schema(AdminSchema)
    @response_schema(AdminResponseSchema, 200)
    async def get(self):
        admin_email = self.request.app.database.admins[0].email
        admin = await self.request.app.store.admins.get_by_email(admin_email)
        if admin:
            return json_response(data=AdminResponseSchema().dump(admin))
        else:
            raise HTTPNotFound


class IndexView(View):
    async def get(self):
        return json_response(data='Bye, hello')
