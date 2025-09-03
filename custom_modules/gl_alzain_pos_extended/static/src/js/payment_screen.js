import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { patch } from "@web/core/utils/patch";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { _t } from "@web/core/l10n/translation";
patch(PaymentScreen.prototype, {
    /**
     * @override
     */
    async validateOrder(isForceValidate) {
        if (this.currentOrder && !this.currentOrder.partner_id) {
            this.pos.selectPartner();
        } else {
            return super.validateOrder(...arguments);
        }
    },

    async addNewPaymentLine(paymentMethod) {
        if (paymentMethod.default_partner_id && !this.currentOrder.partner_id) {
            this.currentOrder.partner_id = paymentMethod.default_partner_id;
        }
        return super.addNewPaymentLine(...arguments);
    }
});


