odoo.define('ds_pos_multi_company_screen', function (require) {
"use strict";
	var PSC = require("point_of_sale.screens")
	var core = require('web.core');
	var QWeb = core.qweb;
	var DomCache = PSC.DomCache;
	
	var ProdScWidget =PSC.ProductScreenWidget.include({
		click_product: function(product) {
	        // console.log("Product Clicked");
	        // console.log(product);
	       if(product.to_weight && this.pos.config.iface_electronic_scale){
	           this.gui.show_screen('scale',{product: product});
	       }else{
	           this.pos.get_order().add_product(product,{company_substitute_id:$('select.company_id').val()});
	       }
	    },

	});

});