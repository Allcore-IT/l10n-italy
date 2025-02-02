# Author(s): Silvio Gregorini (silviogregorini@openforce.it)
# Copyright 2019 Openforce Srls Unipersonale (www.openforce.it)
# Copyright 2023 Simone Rubino - Aion Tech
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AssetDepreciationModeLine(models.Model):
    _name = "asset.depreciation.mode.line"
    _description = "Asset Depreciation Mode Line"
    _order = "from_year_nr asc, to_year_nr asc"

    application = fields.Selection(
        [("coefficient", "Coefficient"), ("percentage", "Percentage")],
        default="coefficient",
        required=True,
        string="Application by",
    )

    coefficient = fields.Float()

    company_id = fields.Many2one(
        "res.company", readonly=True, related="mode_id.company_id", string="Company"
    )

    from_year_nr = fields.Integer(
        required=True,
        string="From Year",
        help="Minimum number of fiscal years passed "
        "from asset purchase date "
        "to apply this line.",
    )

    mode_id = fields.Many2one(
        "asset.depreciation.mode",
        ondelete="cascade",
        required=True,
        readonly=True,
        string="Mode",
    )

    percentage = fields.Float()

    to_year_nr = fields.Integer(
        string="To Year",
        help="Maximum number of fiscal years passed "
        "from asset purchase date "
        "to apply this line.",
    )

    @api.onchange("application")
    def onchange_application(self):
        if self.application:
            if self.application == "coefficient":
                self.percentage = 0
            elif self.application == "percentage":
                self.coefficient = 0
            else:
                self.coefficient = 0
                self.percentage = 0

    def get_depreciation_amount_multiplier(self):
        multiplier = 1
        passed_fiscal_years = self._context.get("passed_fiscal_years")
        if passed_fiscal_years is None:
            # Cannot compare to any line
            return multiplier

        lines = self.filtered(
            lambda line: line.from_year_nr <= passed_fiscal_years
            and (not line.to_year_nr or line.to_year_nr >= passed_fiscal_years)
        )
        if not lines:
            return multiplier

        for line in lines:
            if line.application == "coefficient":
                multiplier *= line.coefficient
            elif line.application == "percentage":
                multiplier *= line.percentage / 100

        return multiplier
