odoo.define('ds_pos_multi_company.models', function (require) {
"use strict";
    
    var BarcodeParser = require('barcodes.BarcodeParser');
    var PosDB = require('point_of_sale.DB');
    var devices = require('point_of_sale.devices');
    var core = require('web.core');
    var Model = require('web.DataModel');
    var formats = require('web.formats');
    var session = require('web.session');
    var time = require('web.time');
    var utils = require('web.utils');

    var QWeb = core.qweb;
    var _t = core._t;
    var Mutex = utils.Mutex;
    var round_di = utils.round_decimals;
    var round_pr = utils.round_precision;
    var Backbone = window.Backbone;

	var posmod = require('point_of_sale.models')

	var models = posmod.PosModel
    var Order = posmod.Order
    var Orderline = posmod.Orderline;

    var exports = {};
    var orderline_id = posmod.orderline_id


    // console.log(posmod);
    posmod.PosModel.prototype.scan_product= function(parsed_code){
        var selectedOrder = this.get_order();
        var product = this.db.get_product_by_barcode(parsed_code.base_code);
        // console.log("xxxxxxxxxxxxxx");
        
        
        if(!product){
            return false;
        }
        if(parsed_code.type === 'price'){
            selectedOrder.add_product(product, {price:parsed_code.value,company_substitute_id:$('select.company_id').val()});
        }else if(parsed_code.type === 'weight'){
            selectedOrder.add_product(product, {quantity:parsed_code.value, merge:false,company_substitute_id:$('select.company_id').val()});
        }else if(parsed_code.type === 'discount'){
            selectedOrder.add_product(product, {discount:parsed_code.value, merge:false,company_substitute_id:$('select.company_id').val()});
        }else{
            selectedOrder.add_product(product,{company_substitute_id:$('select.company_id').val()});
        }

        return true;
    };



    //extending models
	models.extend({
		initialize: function(session, attributes) {
    	var  self = this;
    	this._super(session, attributes);
    	this.company_ids = [];
    	this.warehouse_ids = [];
    	this.analytic_account_ids = [];
        this.sales_ids=[]
    	}	
	});
	
    models.prototype.models.push(
    	{
        model:  'res.company',
        fields: ['currency_id', 'email', 'website', 'company_registry', 'vat', 'name', 'phone', 'partner_id' , 'country_id', 'tax_calculation_rounding_method'],
        domain: function(self){ return [['id','in',self.config.company_ids]]; },
        loaded: function(self,company_ids){ 
            self.company_ids = company_ids; 
        	},
    	});
    
    models.prototype.models.push(
    	{
        model:  'account.analytic.account',
        fields: ['name','company_id','partner_id','tag_ids'],
        domain: function(self){ return [['id','in',self.config.account_analytic_ids]]; },
        loaded: function(self,account_analytic_ids){ 
            self.analytic_account_ids = account_analytic_ids; 
        	},
    	});

    models.prototype.models.push(
        {
        model:  'res.users',
        fields: ['name',],
        domain: function(self){ return [['id','in',self.config.sales_ids]]; },
        loaded: function(self,sales_ids){ 
            self.sales_ids = sales_ids; 
            },
        });

    for (var i = 0; i < models.prototype.models.length; i++) {
        try{
            if(models.prototype.models[i].model === 'product.product'){
                models.prototype.models[i]=
                                {
                                    model:  'product.product',
                                    fields: ['display_name', 'list_price','price','pos_categ_id', 'taxes_id', 'ean13', 'default_code', 
                                             'to_weight', 'uom_id', 'uos_id', 'uos_coeff', 'mes_type', 'description_sale', 'description',
                                             'product_tmpl_id','warehouse_available_ids','company_id','substitute_ids','susbtitute_qty','qty_available'],
                                    context : function(self){ 
                                        
                                        return { pricelist: self.pricelist.id, display_default_code: false, company_id:self.company.id,}; 
                                    },
                                    domain: function(self){ 

                                        return [['sale_ok','=',true],['available_in_pos','=',true],['company_id','=',self.company.id]]},
                                    loaded: function(self, products){
                                        self.db.add_products(products);
                                    },
                                };
            }
        }
        catch(err){
            console.log(err);
        }
        
    }


    Orderline.extend({
        initialize: function(attr,options){
            this.pos   = options.pos;
            this.order = options.order;
            if (options.json) {
                this.init_from_JSON(options.json);
                return;
            }
            this.product = options.product;
            this.price   = options.product.price;
            this.set_quantity(1);
            this.discount = 0;
            this.discountStr = '0';
            this.type = 'unit';
            this.selected = false;
            this.id       = orderline_id++; 
            this.company_substitute_id = false; 

        }
    });

    Orderline.prototype.can_be_merged_with= function(orderline){
        
        if( this.get_product().id !== orderline.get_product().id){    //only orderline of the same product can be merged
            return false;
        }else if(!this.get_unit() || !this.get_unit().groupable){
            return false;
        }else if(this.get_product_type() !== orderline.get_product_type()){
            return false;
        }else if(this.get_discount() > 0){             // we don't merge discounted orderlines
            return false;
        }else if(this.price !== orderline.price){
            return false;
        }else if(this.company_substitute_id !== orderline.company_substitute_id){
            return false;
        }else{ 
            return true;
        }
    };

    Orderline.prototype.get_substitute_company=function(){
        return this.company_substitute_id;
    };
    Orderline.prototype.set_substitute_company=function(company_id){
        this.company_substitute_id=company_id;
    };

    Orderline.prototype.init_from_JSON= function(json) {
        this.product = this.pos.db.get_product_by_id(json.product_id);
        if (!this.product) {
            console.error('ERROR: attempting to recover product ID', json.product_id,
                'not available in the point of sale. Correct the product or clean the browser cache.');
        }
        this.price = json.price_unit;
        this.set_discount(json.discount);
        this.set_quantity(json.qty);
        this.id    = json.id;
        this.company_substitute_id = this.set_substitute_company();
        orderline_id = Math.max(this.id+1,orderline_id);
    };

    Orderline.prototype.export_as_JSON= function() {
        return {
            company_substitute_id:this.get_substitute_company(),
            qty: this.get_quantity(),
            price_unit: this.get_unit_price(),
            discount: this.get_discount(),
            product_id: this.get_product().id,
            tax_ids: [[6, false, _.map(this.get_applicable_taxes(), function(tax){ return tax.id; })]],
            id: this.id,
        };
    };


    //extending Order
    Order.extend({
        initialize: function(session, attributes) {
            var  self = this;
            this.online_shop_trans_code= '';
            this.analytic_account_id= '';
        },
    });

    Order.prototype.export_as_JSON = function() {
        var orderLines, paymentLines;
        orderLines = [];
        this.orderlines.each(_.bind( function(item) {
            return orderLines.push([0, 0, item.export_as_JSON()]);
        }, this));
        paymentLines = [];
        this.paymentlines.each(_.bind( function(item) {
            return paymentLines.push([0, 0, item.export_as_JSON()]);
        }, this));

        return {
            name: this.get_name(),
            amount_paid: this.get_total_paid(),
            amount_total: this.get_total_with_tax(),
            amount_tax: this.get_total_tax(),
            amount_return: this.get_change(),
            lines: orderLines,
            statement_ids: paymentLines,
            pos_session_id: this.pos_session_id,
            partner_id: this.get_client() ? this.get_client().id : false,
            pos_admin: this.pos.cashier ? this.pos.cashier.id : this.pos.user.id,
            user_id: $('select.salesman').val() ? $('select.salesman').val() : this.pos.user.id,
            uid: this.uid,
            sequence_number: this.sequence_number,
            creation_date: this.validation_date || this.creation_date, // todo: rename creation_date in master
            fiscal_position_id: this.fiscal_position ? this.fiscal_position.id : false,
            online_shop_trans_code: $('input.transcode').val(),
            analytic_account_id: $('select.analytic_id').val(),
            

        };
    };



    Order.prototype.add_product = function(product, options){
        if(this._printed){
            this.destroy();
            return this.pos.get_order().add_product(product, options);
        }
        this.assert_editable();
        options = options || {};
        // console.log(options);
        var attr = JSON.parse(JSON.stringify(product));
        attr.pos = this.pos;
        attr.order = this;

        var line = new posmod.Orderline({}, {pos: this.pos, order: this, product: product, company_substitute_id : $("select.company_id").val()});
        if(options.quantity !== undefined){
            line.prototype.set_quantity(options.quantity);
        }
        if(options.price !== undefined){
            line.prototype.set_unit_price(options.price);
        }
        if(options.discount !== undefined){
            line.prototype.set_discount(options.discount);
        }

        if(options.extras !== undefined){
            for (var prop in options.extras) { 
                line[prop] = options.extras[prop];
            }
        }
        if (options.company_substitute_id !== undefined){
            line.set_substitute_company(options.company_substitute_id);
        }
        console.log(line);
        var last_orderline = this.get_last_orderline();
        
        if( last_orderline && last_orderline.can_be_merged_with(line) && options.merge !== false){
            last_orderline.merge(line);
        }else{
            this.orderlines.add(line);
        }
        this.select_orderline(this.get_last_orderline());
    };



    
});