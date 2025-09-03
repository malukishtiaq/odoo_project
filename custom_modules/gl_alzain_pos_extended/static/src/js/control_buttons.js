/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { ControlButtons } from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";
import { makeAwaitable } from "@point_of_sale/app/store/make_awaitable_dialog";
import { SelectionPopup } from "@point_of_sale/app/utils/input_popups/selection_popup";
import { _t } from "@web/core/l10n/translation";

patch(ControlButtons.prototype, {

    async onClickOrderEmployee() {
        const selectionList = this.pos.models["hr.employee"].map((order_employee_id) => ({
            id: order_employee_id.id,
            label: order_employee_id.name,
            isSelected:
                this.currentOrder.order_employee_id &&
                order_employee_id.id === this.currentOrder.order_employee_id.id,
            item: order_employee_id,
        }));

        const payload = await makeAwaitable(this.dialog, SelectionPopup, {
            title: _t("Select the Employee"),
            list: selectionList,
        });

        if (payload) {
            this.currentOrder.setOrderEmployee(payload);
        }
    },
});
