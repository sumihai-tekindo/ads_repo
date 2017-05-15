odoo.define('ds_pos_discount_amount', function (require) {
"use strict";
	var PSC = require("point_of_sale.screens")
	var core = require('web.core');
	var QWeb = core.qweb;
	var DomCache = PSC.DomCache;
	
	
	var ProdScreenW = PSC.ScreenWidget.include({
		barcode_discount_amt_action: function(code){
	        var last_orderline = this.pos.get_order().get_last_orderline();

	        if(last_orderline){
	            last_orderline.set_discount_amt(code.value);
	        }
	    },
		show : function(){
	        var self = this;

	        this.hidden = false;
	        if(this.$el){
	            this.$el.removeClass('oe_hidden');
	        }

	        this.pos.barcode_reader.set_action_callback({
	            'cashier'		: _.bind(self.barcode_cashier_action, self),
	            'product'		: _.bind(self.barcode_product_action, self),
	            'weight'		: _.bind(self.barcode_product_action, self),
	            'price'			: _.bind(self.barcode_product_action, self),
	            'client' 		: _.bind(self.barcode_client_action, self),
	            'discount'		: _.bind(self.barcode_discount_action, self),
	            'discount_amt'	: _.bind(self.barcode_discount_amt_action, self),
	            'error'   		: _.bind(self.barcode_error_action, self),
	        });
	    },
	});

	var ProdOrderW = PSC.OrderWidget.include({
		set_value: function(val) {
	    	var order = this.pos.get_order();
	    	if (order.get_selected_orderline()) {
	            var mode = this.numpad_state.get('mode');
	            if( mode === 'quantity'){
	                order.get_selected_orderline().set_quantity(val);
	            }else if( mode === 'discount'){
	                order.get_selected_orderline().set_discount(val);
	            }else if( mode === 'discount_amt'){
	                order.get_selected_orderline().set_discount_amt(val);
	            }else if( mode === 'price'){
	                order.get_selected_orderline().set_unit_price(val);
	            }
	    	}
	    },
	});
});