/** @odoo-module **/
import { _t } from "@web/core/l10n/translation";

import { patch } from "@web/core/utils/patch";
import { TicketScreen } from "@point_of_sale/app/screens/ticket_screen/ticket_screen";
import { useService } from "@web/core/utils/hooks";
import { NumberPopup } from "@point_of_sale/app/utils/input_popups/number_popup";
import { makeAwaitable } from "@point_of_sale/app/store/make_awaitable_dialog";

patch(TicketScreen.prototype, {
    setup() {
        super.setup();
        this.numberBuffer = useService("number_buffer");
        this.dialog = useService("dialog");
        this.notification = useService("notification");
    },

    async onDoRefund() {
        const order = this.getSelectedOrder();
        if (order && this.getHasItemsToRefund() && this.pos.get_cashier()._role === "cashier") {
            let inputPin = await makeAwaitable(this.dialog, NumberPopup, {
                formatDisplayedValue: (x) => x.replace(/./g, "•"),
                title: _t("Password?"),
            });
            if (!inputPin || this.pos.config.discount_refund_pin !== parseInt(inputPin)) {
                this.notification.add(_t("PIN not found"), {
                    type: "warning",
                    title: _t(`Wrong PIN`),
                });
                return false;
            } else {
                await super.onDoRefund(...arguments);
            }
        } else {
            await super.onDoRefund(...arguments);
        }
    },
});
