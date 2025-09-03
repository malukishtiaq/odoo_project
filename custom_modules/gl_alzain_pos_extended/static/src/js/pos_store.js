import { PosStore } from "@point_of_sale/app/store/pos_store";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { makeActionAwaitable } from "@point_of_sale/app/store/make_awaitable_dialog";

patch(PosStore.prototype, {

    async editPartner(partner) {
        const record = await makeActionAwaitable(
            this.action,
            "point_of_sale.res_partner_action_edit_pos",
            {
                props: { resId: partner?.id },
                additionalContext: {
                    ...this.editPartnerContext(),
                    default_is_created_from_pos: true,
                },
            }
        );
        const newPartner = await this.data.read("res.partner", record.config.resIds);
        debugger;
        return newPartner[0];
    },

});