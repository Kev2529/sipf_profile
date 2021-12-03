# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from ast import literal_eval

from odoo import api, fields, models
from pytz import timezone, UTC, utc
from datetime import timedelta

from odoo.tools import format_time


class HrEmployeeBase(models.AbstractModel):
    _inherit = "hr.employee.base"

    in_charge_of = fields.Char("En charge de")
    