from odoo import api, fields, models
class GymersTag(models.Model):
    _name = "gymers.tag"
    _description = "Gymers Tag"

    name = fields.Char(string="Tag", required=True)
    active = fields.Boolean(string="Active", default=True)
    color = fields.Integer(string="Color", default=0, required=True)
    sequence = fields.Integer(string="Sequence")

    _sql_constraints = [('unique_tag_name','unique(name)','Tag name already exists'),
                        ('check_sequence','check(sequence>0)','sequence must be greater then 0')]
