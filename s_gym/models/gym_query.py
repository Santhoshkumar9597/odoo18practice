from odoo import models, fields, api
from odoo.exceptions import UserError

class GymQuery(models.Model):
    _name = 'gym.query'
    _description = 'Gym SQL Query Executor'

    name = fields.Char(string="Query Name", required=True)
    query = fields.Text(string="SQL Query", required=True)
    output_type = fields.Selection([
        ('formatted', 'Formatted'),
        ('raw', 'Raw'),
    ], string="Output Type", default='formatted')
    result = fields.Text(string="Result", readonly=True)

    def _format_select_result(self, data):
        if not data:
            return "No results found."
        headers = data[0].keys()
        rows = [list(row.values()) for row in data]
        table = [headers] + rows
        col_widths = [max(len(str(cell)) for cell in col) for col in zip(*table)]
        formatted_rows = []
        for row in table:
            formatted_rows.append(" | ".join(str(cell).ljust(w) for cell, w in zip(row, col_widths)))
        return "\n".join(formatted_rows)

    def action_execute_query(self):
        for record in self:
            if not record.query.strip():
                raise UserError("Query cannot be empty!")
            try:
                self.env.cr.execute(record.query)
                if record.query.strip().lower().startswith("select"):
                    data = self.env.cr.dictfetchall()
                    if record.output_type == 'formatted':
                        record.result = self._format_select_result(data)
                    else:
                        record.result = str(data)
                else:
                    self.env.cr.commit()
                    record.result = "Query executed successfully."
            except Exception as e:
                record.result = f"Error executing query: {e}"
