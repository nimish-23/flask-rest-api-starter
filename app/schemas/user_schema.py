from marshmallow import Schema, fields, validate

class RegistrationSchema(Schema):
    username = fields.String(required=True, validate=validate.Length(min=3, max=15))
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=6))

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=6))

class UpdateUserSchema(Schema):
    """Schema for updating user profile - all fields optional"""
    username = fields.String(required=False, validate=validate.Length(min=3, max=15))
    email = fields.Email(required=False)
    password = fields.String(required=False, validate=validate.Length(min=6))
