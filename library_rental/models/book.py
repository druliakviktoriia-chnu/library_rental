from odoo import fields, models


class LibraryBook(models.Model):
    _name = 'library.book'
    _description = 'Library Book'

    name = fields.Char(string='Title', required=True)
    author = fields.Char(required=True)
    isbn = fields.Char(string='ISBN')
    publish_year = fields.Integer()
