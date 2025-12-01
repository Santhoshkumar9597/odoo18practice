from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import date
from dateutil.relativedelta import relativedelta

class GymFitness(models.Model):
    _name = "gym.fitness"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Gym Fitness"
    _order = 'sequence, id desc'

    name_bold = fields.Html(string="Name Bold", compute='_compute_name_bold', store=False)
    sequence = fields.Integer(string="Sequence", default=10)
    name = fields.Char(string="Name", tracking=True, required=True)
    ref = fields.Char(string="Reference", readonly=True, copy=False, default='New')
    date_of_birth = fields.Date(string="Date of Birth",tracking=1)
    gender = fields.Selection([('male', 'Male'),('female', 'Female'),('other', 'Other')], string="Gender",tracking=5)
    marital_status = fields.Selection([('single', 'Single'),('married', 'Married'),('divorced', 'Divorced'),], string="Marital Status")
    phone=fields.Char(string="Phone")
    email=fields.Char(string="Email")
    website=fields.Char(string="Website")
    partner_name = fields.Char(string="Partner Name")
    active = fields.Boolean(default=True)
    state = fields.Selection([('free', 'In Free'),('coaching', 'In Coaching'),('leave', 'In Leave')], string="Status", default='free', tracking=True)
    age = fields.Integer(string="Age",compute="_compute_age",inverse="_inverse_compute_age",search="_search_age",store=True)
    is_birthday = fields.Boolean(string="Is Birthday",compute="_compute_is_birthday",store=False)
    appointment_count = fields.Integer( string="Appointment Count", compute="_compute_appointment_count", store=True )

    @api.depends('name')

    def _compute_name_bold(self):
        for rec in self:
            rec.name_bold = f"<b>{rec.name}</b>" if rec.name else ""

    @api.depends('date_of_birth')
    def _compute_appointment_count(self):
        appointment_data = self.env['appointment.fitness'].read_group( [('trainer_id', 'in', self.ids)],['trainer_id'],['trainer_id'])
        counts = {data['trainer_id'][0]: data['trainer_id_count'] for data in appointment_data}
        for trainer in self:
            trainer.appointment_count = counts.get(trainer.id, 0)

    def action_view_appointments(self):
        self.ensure_one()
        return {
            'name': f"Appointments for {self.name}",'type': 'ir.actions.act_window',
            'res_model': 'appointment.fitness','view_mode': 'tree,form',
            'domain': [('trainer_id', '=', self.id)],'context': {'default_trainer_id': self.id}
        }

    def _compute_age(self):
        for rec in self:
            today = fields.Date.today()
            if rec.date_of_birth:
                rec.age = today.year - rec.date_of_birth.year
            else:
                rec.age = 0
    def _compute_is_birthday(self):
        today = date.today()
        for rec in self:
            if rec.date_of_birth:
                rec.is_birthday = (
                        rec.date_of_birth.day == today.day and
                        rec.date_of_birth.month == today.month
                )
            else:
                rec.is_birthday = False
    def _inverse_compute_age(self):
        today = fields.Date.today()
        for rec in self:
            rec.date_of_birth = today - relativedelta(years=rec.age) if rec.age else False
    def _search_age(self, operator, value):
        today = fields.Date.today()
        target_date = today - relativedelta(years=value)
        if operator in ('=', '=='):
            domain = [('date_of_birth', '>=', target_date.replace(year=target_date.year - 1)),
                      ('date_of_birth', '<=', target_date)]
        elif operator in ('>', '>='):
            domain = [('date_of_birth', '<=', target_date)]
        elif operator in ('<', '<='):
            domain = [('date_of_birth', '>=', target_date)]
        else:
            domain = []
        return domain
    @api.constrains('date_of_birth')
    def _check_date_of_birth(self):
        for rec in self:
            if rec.date_of_birth and rec.date_of_birth > fields.Date.today():
                raise ValidationError(_("Date of Birth must be in the past"))
    def name_get(self):
        return [(rec.id, f"[{rec.ref}] {rec.name}") for rec in self]
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('ref', 'New') == 'New':
                vals['ref'] = self.env['ir.sequence'].next_by_code('gym.fitness.ref') or 'New'
        return super().create(vals_list)
    def action_in_free(self):
        self.write({'state': 'free'})
    def action_in_coaching(self):
        self.write({'state': 'coaching'})
    def action_in_leave(self):
        self.write({'state': 'leave'})
