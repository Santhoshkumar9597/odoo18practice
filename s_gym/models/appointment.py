from odoo import api, fields, models, _


class AppointmentFitness(models.Model):
    _name = "appointment.fitness"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = " book an appointment for your fitness"
    _order = 'sequence, id desc'

    sequence = fields.Integer(string="Sequence", default=10)
    trainer_id = fields.Many2one('gym.fitness', string="Trainer", required=True)
    my_field = fields.Char(string="My Field", tracking=True)
    name = fields.Char(string="Name", tracking=True)
    age = fields.Integer(string="Age", tracking=True)
    gender = fields.Selection([('male', 'Male'), ('female', 'Female'), ('other', 'Other')], string="Gender")
    appointment_time = fields.Datetime(string="Appointment Time", tracking=1)
    booking_date = fields.Date(string="Booking Date", default='fields.Datetime.now')
    ref = fields.Char(string="Reference", help="The reference of the appointment to which trainer you want")
    active = fields.Boolean("Active", default=True)
    session = fields.Html(string="Session")
    priority = fields.Selection([('o', 'Normal'), ('1', 'Low'), ('2', 'Medium'), ('3', 'High')], string="Priority")
    state = fields.Selection([('confirm', 'Confirmed'), ('cancel', 'Cancelled')], string="Status", required=True,
                             default='confirm')
    supplement_ids = fields.One2many('appointment.supplement', 'supplement_id', string="Supplements")
    install = fields.Boolean(string="Install")
    image = fields.Image(string="Image")
    tag_ids = fields.Many2many("gymers.tag", string="Tags", tracking=45)
    progress = fields.Integer(string="Progress", compute="_compute_progress")
    cancel_reason = fields.Text(string="Cancellation Reason")

    def action_notification(self):
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Notification',
                'message': 'Button clicked successfully',
                'sticky': False,
                'type': 'success',
            }
        }

    @api.depends('state')
    def _compute_progress(self):
        for record in self:
            if record.state == 'confirm':
                record.progress = 100
            else:
                record.progress = 0

    @api.onchange('trainer_id')
    def onchange_trainer_id(self):
        if self.trainer_id:
            self.ref = self.trainer_id.ref

    def action_train(self):
        return {'type': 'ir.actions.act_url', 'target': 'new', 'url': 'https://www.ufc.com', }

    def action_gym_fitness(self):
        return True

    def action_confirm_appointment(self):
        for record in self:
            record.state = 'confirm'
            print("Button clicked")
        return {'effect': {'fadeout': 'slow', 'message': 'message', 'type': 'rainbow_man', }}

    def action_cancel_appointment(self):
        for record in self:
            record.state = 'cancel'

    def action_installed(self):
        for record in self:
            record.install = True


class AppointmentSupplement(models.Model):
    _name = 'appointment.supplement'
    _description = "Appointment Supplement Lines"
    sl_no = fields.Integer(string="Serial No")
    product_id = fields.Many2one('product.product')
    price_unit = fields.Float(string="Price Unit")
    quantity = fields.Integer(string="Quantity")
    supplement_id = fields.Many2one('appointment.fitness', string="appointment")

    @api.model_create_multi
    def create(self, vals_list):
        records = super(AppointmentSupplement, self).create(vals_list)
        if records and records[0].supplement_id:
            records._resequence_for_appointment(records[0].supplement_id)
        return records

    def unlink(self):
        supplement_ids = self.mapped('supplement_id')
        res = super(AppointmentSupplement, self).unlink()
        for appointment in supplement_ids:
            self._resequence_for_appointment(appointment)
        return res

    def _resequence_for_appointment(self, appointment):
        supplements = self.search([('supplement_id', '=', appointment.id)], order="id asc")
        for index, record in enumerate(supplements, start=1):
            record.sl_no = index


class AppointmentSupplementInherit(models.Model):
    _inherit = 'appointment.supplement'
    description = fields.Char(string="Description")

    total_price = fields.Float(string="Total Price", compute="_compute_total_price", store=True)

    @api.depends('price_unit', 'quantity')
    def _compute_total_price(self):
        for record in self:
            record.total_price = record.price_unit * record.quantity
