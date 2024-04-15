from marshmallow import Schema, fields


class AdminSchema(Schema):
    id = fields.Int(required=False)
    email = fields.Str(required=True)
    password = fields.Str(required=True)

class AdminAddSchema(Schema):
    email = fields.Str(required=True)

class AdminResponseSchema(AdminAddSchema):
    id = fields.Int(required=True)