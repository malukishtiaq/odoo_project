/** @odoo-module **/
import { _t } from "@web/core/l10n/translation";

import { patch } from "@web/core/utils/patch";
import { TicketScreen } from "@point_of_sale/app/screens/ticket_screen/ticket_screen";
import { useService } from "@web/core/utils/hooks";
import { NumberPopup } from "@point_of_sale/app/utils/input_popups/number_popup";
import { makeAwaitable } from "@point_of_sale/app/store/make_awaitable_dialog";

patch(TicketScreen.prototype, {
    _onClickOrder({ detail: clickedOrder }) {
        if (!clickedOrder || clickedOrder.locked) {
            if (this.env.pos.selectedSyncedOrderId === clickedOrder?.backendId) {
                this.env.pos.selectedSyncedOrderId = null;
            } else {
                this.env.pos.selectedSyncedOrderId = clickedOrder?.backendId;
            }

            if (!this.env.pos.getSelectedOrderline()) {
                const orderlines = clickedOrder.get_orderlines();
                const firstLine = orderlines[0];
                if (firstLine) {
                    this.env.pos.selectedOrderlineIds[clickedOrder.backendId] = firstLine.id;
                }

                for (const line of orderlines) {
                    if (line.is_component) {
                        const toRefundDetail = this._getToRefundDetail(line);
                        toRefundDetail.qty = line.quantity;
                    }
                }
            }

            this.numberBuffer.reset();
        } else {
            this._setOrder(clickedOrder);
        }

        this.render();
    },
});
