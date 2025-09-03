import { PosStore } from "@point_of_sale/app/store/pos_store";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { makeActionAwaitable } from "@point_of_sale/app/store/make_awaitable_dialog";

patch(PosStore.prototype, {

    getReceiptHeaderData(order) {
        return {
            ...super.getReceiptHeaderData(...arguments),
            config: this.config
        };
    },

});