/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { PosOrderline } from "@point_of_sale/app/models/pos_order_line";
import { rpc } from "@web/core/network/rpc";
import { Orderline } from "@point_of_sale/app/generic_components/orderline/orderline";

patch(Orderline, {
    props: {
        ...Orderline.props,
        line: {
            ...Orderline.props.line,
            shape: {
                ...Orderline.props.line.shape,
                is_component: { type: Boolean, optional: false },
            },
        },
    },
});
patch(PosOrder.prototype, {

    get_orderlines() {
        if (this.lines && this.lines.length > 0) {
            for (const line of this.lines) {
                let rf_line_id = line.refunded_orderline_id;
                if (line.refunded_orderline_id) {
                    rf_line_id = line.refunded_orderline_id.id;
                }
                if (rf_line_id && typeof rf_line_id !== 'number') {
                    const match = rf_line_id.match(/pos\.order\.line\((\d+)\s*,*\s*\)/);
                    rf_line_id = match && match[1] ? parseInt(match[1], 10) : null;
                }
                const line_id = rf_line_id || line.id;
                let lines = this.lines;
                const result = rpc("/web/dataset/call_kw/pos.order.line/get_component_status", {
                    model: "pos.order.line",
                    method: "get_component_status",
                    args: [[line_id]],
                    kwargs: {},
                }).then(function(res) {
                    line.is_component = res;
                });
            }
        }
        return this.lines;
    }
});

patch(PosOrderline.prototype, {
    setup() {
            super.setup(...arguments);

        this.is_component = false;

        if (this.order && this.refunded_orderline_id !== undefined) {
            let rf_line_id = this.refunded_orderline_id;
            if (typeof rf_line_id !== 'number') {
                const match = rf_line_id.match(/pos\.order\.line\((\d+)\s*,*\s*\)/);
                rf_line_id = match && match[1] ? parseInt(match[1], 10) : null;
            }
            const line_id = rf_line_id || this.id;

            rpc("/web/dataset/call_kw/pos.order.line/get_component_status", {
                model: "pos.order.line",
                method: "get_component_status",
                args: [[line_id]],
                kwargs: {},
            }).then((result) => {
                this.is_component = result;
            });
        }
    },

    getDisplayData() {
        const data = super.getDisplayData();
        data.is_component = this.is_component;
        return data;
    },
});