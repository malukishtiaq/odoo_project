import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { patch } from "@web/core/utils/patch";
import { onMounted } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { NumberPopup } from "@point_of_sale/app/utils/input_popups/number_popup";
import { makeAwaitable } from "@point_of_sale/app/store/make_awaitable_dialog";

patch(ProductScreen.prototype, {
    getNumpadButtons() {
        var res = super.getNumpadButtons()
        if (this.pos.get_cashier()._role === "cashier") {
            res.forEach((btn) => {
                if (btn.value == "price") {
                    btn.class = 'd-none'
                }
            });
        }
        return res
    },

    async checkPIN() {
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
            return true;
        }
    },

    async onNumpadClick(buttonValue) {
        if (buttonValue === "discount" && this.pos.get_cashier()._role === "cashier") {
            let pin = await this.checkPIN();
            if (pin) {
                super.onNumpadClick(...arguments);
            } else {
                this.numberBuffer.reset();
            }
        } else {
            super.onNumpadClick(...arguments);
        }
    }
});
