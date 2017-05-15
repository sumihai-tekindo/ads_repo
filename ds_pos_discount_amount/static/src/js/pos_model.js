odoo.define('ds_pos_discount_amount.models', function (require) {
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

    var posmod = require('point_of_sale.models');
    var exports = {};
    var Order = posmod.Order
    var Orderline = posmod.Orderline

    //extending PosModel
    posmod.PosModel.prototype.scan_product= function(parsed_code){
        var selectedOrder = this.get_order();
        var product = this.db.get_product_by_barcode(parsed_code.base_code);

        if(!product){
            return false;
        }

        if(parsed_code.type === 'price'){
            selectedOrder.add_product(product, {price:parsed_code.value,company_substitute_id:$('select.company_id').val()});
        }else if(parsed_code.type === 'weight'){
            selectedOrder.add_product(product, {quantity:parsed_code.value, merge:false,company_substitute_id:$('select.company_id').val()});
        }else if(parsed_code.type === 'discount'){
            selectedOrder.add_product(product, {discount:parsed_code.value, merge:false,company_substitute_id:$('select.company_id').val()});
        }else if(parsed_code.type === 'discount_amt'){
            selectedOrder.add_product(product, {discount_amt:parsed_code.value, merge:false,company_substitute_id:$('select.company_id').val()});
        }else{
            selectedOrder.add_product(product,{company_substitute_id:$('select.company_id').val()});
        }
        return true;
    };

    var Orderline_id = 1;
    //extending Orderline
    Orderline.prototype.initialize= function(attr,options){
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
        this.discount_amt = 0;
        this.discount_amt_Str = '0';
        this.type = 'unit';
        this.selected = false;
        this.id       = Orderline_id++; 
        this.company_substitute_id = false; 
        };

    Orderline.prototype.init_from_JSON= function(json) {
        this.product = this.pos.db.get_product_by_id(json.product_id);
        if (!this.product) {
            console.error('ERROR: attempting to recover product ID', json.product_id,
                'not available in the point of sale. Correct the product or clean the browser cache.');
        }
        this.price = json.price_unit;
        this.set_discount(json.discount);
        this.set_discount_amt(json.discount_amt);
        this.set_quantity(json.qty);
        this.id    = json.id;
        this.company_substitute_id = this.set_substitute_company();
        Orderline_id = Math.max(this.id+1,Orderline_id);
        };
        
    Orderline.prototype.clone= function(){
        var Orderline = new Orderline({},{
            pos: this.pos,
            order: this.order,
            product: this.product,
            price: this.price,
        });
        Orderline.order = null;
        Orderline.quantity = this.quantity;
        Orderline.quantityStr = this.quantityStr;
        Orderline.discount = this.discount;
        Orderline.discount_amt = this.discount_amt;
        Orderline.type = this.type;
        Orderline.selected = false;
        return Orderline;
        };
    Orderline.prototype.set_discount_amt= function(discount){
        var disc = parseFloat(discount);
        this.discount_amt = disc;
        this.discount_amt_Str = '' + disc;
        this.trigger('change',this);
        };

    Orderline.prototype.get_discount_amt= function(){
        return this.discount_amt;
        };
    Orderline.prototype.get_discount_amt_str= function(){
        return this.discount_amt_Str;
        };

    Orderline.prototype.can_be_merged_with= function(Orderline){
        // console.log("-------------THIS----------");
        // console.log(this);
        // console.log("-------------orderline----------");
        // console.log(Orderline);
        if( this.get_product().id !== Orderline.get_product().id){    //only Orderline of the same product can be merged
            return false;
        }else if(!this.get_unit() || !this.get_unit().groupable){
            return false;
        }else if(this.get_product_type() !== Orderline.get_product_type()){
            return false;
        }else if(this.get_discount() > 0){             // we don't merge discounted Orderlines
            return false;
        }else if(this.get_discount_amt() > 0){             // we don't merge discounted Orderlines
            return false;
        }else if(this.price !== Orderline.price){
            return false;
        }else if(this.company_substitute_id !== Orderline.company_substitute_id){
            return false;
        }else{ 
            return true;
            }
        };
    Orderline.prototype.export_as_JSON= function() {
        return {
            company_substitute_id:this.get_substitute_company(),
            qty: this.get_quantity(),
            price_unit: this.get_unit_price(),
            discount: this.get_discount(),
            discount_amt: this.get_discount_amt(),
            product_id: this.get_product().id,
            tax_ids: [[6, false, _.map(this.get_applicable_taxes(), function(tax){ return tax.id; })]],
            id: this.id,
            };
        };
    Orderline.prototype.export_for_printing= function(){
        return {
            quantity:           this.get_quantity(),
            unit_name:          this.get_unit().name,
            price:              this.get_unit_display_price(),
            discount:           this.get_discount(),
            discount_amt:       this.get_discount_amt(),
            product_name:       this.get_product().display_name,
            price_display :     this.get_display_price(),
            price_with_tax :    this.get_price_with_tax(),
            price_without_tax:  this.get_price_without_tax(),
            tax:                this.get_tax(),
            product_description:      this.get_product().description,
            product_description_sale: this.get_product().description_sale,
            };
        };
    Orderline.prototype.get_base_price= function(){
            var rounding = this.pos.currency.rounding;
            return round_pr((this.get_unit_price() * this.get_quantity() * (1 - this.get_discount()/100)), rounding);
        };

    Orderline.prototype.compute_all= function(taxes, price_unit, quantity, currency_rounding,disc_amt=0.0) {
        var self = this;
        var list_taxes = [];
        var currency_rounding_bak = currency_rounding;
        if (this.pos.company.tax_calculation_rounding_method == "round_globally"){
           currency_rounding = currency_rounding * 0.00001;
        }


        var total_excluded = round_pr((price_unit * quantity)-disc_amt, currency_rounding);

        var total_included = total_excluded;
        var base = total_excluded;
        _(taxes).each(function(tax) {
            tax = self._map_tax_fiscal_position(tax);
            if (tax.amount_type === 'group'){
                var ret = self.compute_all(tax.children_tax_ids, price_unit, quantity, currency_rounding,disc_amt);
                total_excluded = ret.total_excluded;
                base = ret.total_excluded;
                total_included = ret.total_included;
                list_taxes = list_taxes.concat(ret.taxes);
            }
            else {
                var tax_amount = self._compute_all(tax, base, quantity);
                tax_amount = round_pr(tax_amount, currency_rounding);

                if (tax_amount){
                    if (tax.price_include) {
                        total_excluded -= tax_amount;
                        base -= tax_amount;
                    }
                    else {
                        total_included += tax_amount;
                    }
                    if (tax.include_base_amount) {
                        base += tax_amount;
                    }
                    var data = {
                        id: tax.id,
                        amount: tax_amount,
                        name: tax.name,
                    };
                    list_taxes.push(data);
                }
            }
        });
        return {
            taxes: list_taxes,
            total_excluded: round_pr(total_excluded, currency_rounding_bak),
            total_included: round_pr(total_included, currency_rounding_bak)
        };
    };
    
    Orderline.prototype.get_all_prices= function(){
        var price_unit = (this.get_unit_price() * (1.0 - (this.get_discount() / 100.0)));
        var taxtotal = 0;

        var product =  this.get_product();
        var taxes_ids = product.taxes_id;
        var taxes =  this.pos.taxes;
        var taxdetail = {};
        var product_taxes = [];

        _(taxes_ids).each(function(el){
            product_taxes.push(_.detect(taxes, function(t){
                return t.id === el;
            }));
        });

        var all_taxes = this.compute_all(product_taxes, price_unit, this.get_quantity(), this.pos.currency.rounding, this.get_discount_amt());
        _(all_taxes.taxes).each(function(tax) {
            taxtotal += tax.amount;
            taxdetail[tax.id] = tax.amount;
        });

        return {
            "priceWithTax": all_taxes.total_included,
            "priceWithoutTax": all_taxes.total_excluded,
            "tax": taxtotal,
            "taxDetails": taxdetail,
        };
    };

    
    //extending Order
    Order.prototype.add_product = function(product, options){

            if(this._printed){
                this.destroy();
                return this.pos.get_order().add_product(product, options);
            }
            this.assert_editable();
            options = options || {};

            var attr = JSON.parse(JSON.stringify(product));
            attr.pos = this.pos;
            attr.order = this;
            var line = new posmod.Orderline({}, {pos: this.pos, order: this, product: product, company_substitute_id : $("select.company_id").val()});
            if(options.quantity !== undefined){
                line.set_quantity(options.quantity);
            }
            if(options.price !== undefined){
                line.set_unit_price(options.price);
            }
            if(options.discount !== undefined){
                line.set_discount(options.discount);
            }
            if(options.discount_amt !== undefined){
                line.set_discount_amt(options.discount_amt);
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
            var last_Orderline = this.get_last_orderline()
            
            if( last_Orderline && last_Orderline.can_be_merged_with(line) && options.merge !== false){
                last_Orderline.merge(line);
            }else{
                this.orderlines.add(line);
            }
            this.select_orderline(this.get_last_orderline());
        };
    Order.prototype.get_total_discount= function() {
            return round_pr(this.orderlines.reduce((function(sum, Orderline) {
                return sum + (((Orderline.get_unit_price() * (Orderline.get_discount()/100)) * Orderline.get_quantity())-Orderline.get_discount_amt());
            }), 0), this.pos.currency.rounding);
        };
        
    Order.prototype.get_total_without_tax= function() {
            return round_pr(this.orderlines.reduce((function(sum, orderLine) {
                return sum + orderLine.get_price_without_tax();
            }), 0), this.pos.currency.rounding);
        };

});