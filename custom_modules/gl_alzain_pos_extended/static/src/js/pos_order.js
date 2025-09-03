/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { rpc } from "@web/core/network/rpc";

patch(PosOrder.prototype, {
    setup(vals) {
        super.setup(vals);
        this.order_employee_id = vals.order_employee_id || false;
        this.all_order_employee_id = this.models["hr.employee"].getAll()
        if (this.order_employee_id) {
            this.all_order_employee_id.forEach((emp) => {
                if (emp.id == this.order_employee_id) {
                    this.order_employee_id = emp
                }
            });
        }
    },

    getOrderEmployee() {
        return this.order_employee_id;
    },

    setOrderEmployee(emp) {
        this.order_employee_id = emp;
    },
});
