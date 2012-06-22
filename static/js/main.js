app = {
	debug:true,
	log: function(obj){
		if(this.debug){
			console.log(obj);
		}
	},
	state: "start",
	models:{},
	cols:{},
	views:{}
};

var Order = Backbone.Model.extend({
	defaults: {
		type: "simple",
		type_label: "",
		//базовые параметры
		width: "", //ширина изделия
		height: "", //высота изделия
		quant: "", //тираж
		time: "", //время на выполнение заказа
		chroma: "", //цветность
		param_value: "", //атрибуты бумаги(имя, плотность)
		add_trim: "true",
		add_print_area: "true",
		//параметры постпечатки
		add_lamin: "false", //добавка ламинации
		lamin_name: "", //кодовое имя выбраной ламинации
		lamin_label: "", //имя выбраной ламинации
		add_big: "false", //добавка биговки
		big_count: "", //количество бигов
		big_align: "", //позиционирование биговки
		//параметры при пересчёте
		format: "A4", //формат печатного листа
		Real: "", //площадь печати реальной продукции
		All: "", //полная площадь затраченой бумаги
		Out: "", //процент отхода
		On_paper: "", //количество изделий на 1 лист
		rows: "", //количество изделий в строку
		cols: "", //количество изделий в столбик
		number_of_lists: "", //количество листов
		finally_production: "", //итоговое количество изделий
		wid_a3: "", //размер печатного листа
		hei_a3: "", //размер печатного листа
		slices: "", //количество резов
		//параметры при просчёте
		layout: "", //расскладка на лист
		print_cost: "", //цена печати
		slice_cost: "", //цена подрезки
		big_cost: "", //цена беговки
		lamin_cost: "", //цена ламинации
		order_cost: "" //цена заказа
	}
});


var Format = Backbone.Model.extend({//Модель форматов
	defaults:{
		name: "", //имя формата
		width: "",
		height: ""
	}
});

var Formats = Backbone.Collection.extend({//Набор форматов
	model: Format,
	url: '/paper-size/',
	id: 'formats-block',

	initialize: function(){
		this.fetch();
	},

	parse: function(resp, xhr){
		return resp.Formats
	}
});


var Paper = Backbone.Model.extend({//Модель бумаги
	defaults:{
		param_name: "", //имя плотности
		param_value: "" //значение плотности
	}
});

var Papers = Backbone.Collection.extend({// Набор бумаги
	model: Paper,
	url: '/paper-choose/',
	id: "papers-block",

	initialize: function(){
		this.fetch();

	},
	parse: function(resp, xhr){
		return resp.Paper
	}
});


var Lamin = Backbone.Model.extend({//Модель ламинации
	defaults:{
		lamin_name: "",
		lamin_label: ""
	}
});

var Lamins = Backbone.Collection.extend({//Набор ламинаций
	model: Lamin,
	url: '/lamin/',
	id: "lamins-block",

	initialize: function(){
		this.fetch()
	},
	parse: function(resp, xhr){
		return resp.Lamins
	}
});


var AppState = Backbone.Model.extend({
	defaults: {
		state: "start"
	}
});


var ListLamins = Backbone.View.extend({//Вывод ламинаций

	template: _.template($('#template-lamins-block').html()),

	initialize: function(){
		this.collection.bind('reset', this.render, this)
	},

	render: function(){
		$(this.el).html(this.template({
			models: this.collection.toJSON()
		}));
	}

});


var ListPapers = Backbone.View.extend({//Вывод бумаги

	template: _.template($('#template-papers-block').html()),

	initialize: function(){
		this.collection.bind('reset', this.render, this)
	},

	render: function(){
		$(this.el).html(this.template({
			models: this.collection.toJSON()
		}));
	}

});


var ListFormats = Backbone.View.extend({//Вывод форматов

	template: _.template($('#template-formats-block').html()),

	events:{
		"click .select-format": "select"
	},

	initialize: function(){
		this.collection.bind('reset', this.render, this)
	},

	select: function(e){
		e.preventDefault();
		var $btn = $(e.currentTarget);
		$('#width').val($btn.data("width"));
		$('#height').val($btn.data("height"));
	},

	render: function(){
		$(this.el).html(this.template({
			models: this.collection.toJSON()
		}));
	}

});



var Block = Backbone.View.extend({
	el: $("#block"), // DOM элемент widget'а


	template: _.template($('#start').html()),

	events: {
		"click #send": "load", // Обработчик клика на кнопке "Проверить"
		//"click #login-btn": "login", // Обработчик клика на кнопке "Проверить"
		"click #add_lamin": "load_lamin", //вывод ламинаций
		"click #add_big": "load_big" //вывод биговок
	},

	initialize: function () { // Подписка на событие модели
		this.model.bind('change', this.render, this);
		app.models.order.bind('change:param_value', this.swapPaper, this);
	},

	load: function (e) {
		e.preventDefault();
		var errors = false;
		$("#alert").add("#status").slideUp();
		$("#status").remove();
		$("#alert").html("");
		//$("#results").hide();
		$(this.el).find('#send').button('loading');
		$(this.el).find('.error').removeClass("error");
		$(this.el).find('.warning').removeClass("warning");
		$(this.el).find('.help-block').remove();
		var data = {};
		$.each(this.el.find("input:text, input:radio:checked, select"), function(){
			var $input = $(this);
			if (_.isNumber(parseFloat($input.val())) || !$input.hasClass("num")){
				data[$input.attr('name')] = $input.val();
			}
			else{
				$input.closest(".control-group").addClass("error");
				$input.after("<span class='help-block'>Please correct the error</span>");
				$('#send').button('reset');
				errors = true;
			}
		});
		$.each(this.el.find("input:checkbox"), function() {
			var $input = $(this);
			data[$input.attr('name')] = $input.is(":checked") ? true : false;
		});
		if (errors)
			return false;

		app.log(data);
		app.models.order.set(data);//пишем начлаьные данные в модель заказа
		app.models.order.trigger("retype");//выясняем тип заказа
	},

	/*login: function(e){
		//e.preventDefault();

		var sendData = {
			action: "login",
			username: $(this.el).find("#username").val(),
			password:  $(this.el).find("#password").val(),
			'csrfmiddlewaretoken': djangoToken
		};

		$.ajax({
			url: "/",
			type: "POST",
			data: sendData,
			complete: function(data){
				app.log(data);
				var content = $(data).find("div[role='main'] > *");
				app.log(content);
				//location.reload();
				//$("div[role='main']").html(content);
				$("#login").modal("hide");
			}
		})


	},*/

	load_lamin: function(){
		$(this.el).find("#lamins").toggle();

	},

	load_big: function(){
		$(this.el).find("#bigs").toggle();

	},


	swapPaper: function(){

		var $a4 = $(this.el).find("#paper80"),
			$a3 = $(this.el).find("#paper100"),
			$paper = $(this.el).find("#papers-block"),
			format = app.models.order.get("format");

		if ($paper.val() == "80" && (format=="A3" || format=="A3p")){
			$paper.closest(".control-group").addClass("warning");
			$paper.after("<span class='help-block'>Эта бумага не доступна для А3, просчёт выполнен на 100</span>");
			app.models.order.set({param_value: 100}, {silent: true});
			return false
		}

		if ($paper.val() == "100" && (format=="A4" || format=="A4p")){
			$paper.closest(".control-group").addClass("warning");
			$paper.after("<span class='help-block'>Эта бумага не доступна для А4, просчёт выполнен на 80</span>");
			app.models.order.set({param_value: 80}, {silent: true});
			return false
		}
	},

	render: function () {
		var state = this.model.get("state");
		$(this.el).html(this.template(this.model.toJSON()));
		this.lamins 	= new ListLamins({el: this.$("#" + app.cols.lamins.id), collection: app.cols.lamins});
		this.papers 	= new ListPapers({el: this.$("#" + app.cols.papers.id), collection: app.cols.papers});
		this.formats 	= new ListFormats({el: this.$("#" + app.cols.formats.id), collection: app.cols.formats});

		return this;
	}

});


var Result = Backbone.View.extend({
	el: $("#result"),


	template: _.template($('#print').html()),


	initialize: function(){
		this.model.bind('change', 	this.render, this);
		this.model.bind('calc', 	this.calc, this);
		this.model.bind('retype', 	this.retype, this);
		this.model.bind('layout', 	this.renderLayout, this);
		this.model.bind('change:type', this.labelType, this);
	},


	retype: function(){
		var width 			= parseInt(app.models.order.get("width")),
			height 			= parseInt(app.models.order.get("height")),
			add_print_area	= app.models.order.get("add_print_area"),
			add_trim  		= app.models.order.get("add_trim"),
			quant  			= app.models.order.get("quant"),
			time   			= parseInt(app.models.order.get("time"));
		var a3={}; a3.width = 305; a3.height = 430;
		var	a1={}; a1.width = 420; a1.height = 594;

		if (!add_trim){
			width+=4;
			height+=4;
		}

		if (!add_print_area){
			width+=8;
			height+=8;
		}

		// TODO: SUMMARY PRINTING CHECK

		if ((width <= a3.width) && (height <= a3.height)){// Если изделие меньше А3
				$.when(app.views.result.resize()).then(function(){ //Делаем пересчёт на выбранный формат
					quant = app.models.order.get("number_of_lists");
					if (quant <=500) {
						app.models.order.set({type: "digit"});// Уходим на цифровую печать
					}
					else{
						if (time < 5){
							app.models.order.set({type: "digit"});// Уходим на цифровую печать
						}
						else{
							app.models.order.set({type: "offset"}); // Уходим на оффсет
						}
					}
					app.models.order.trigger("calc");
				});

		}
		else{//Изделие больше А3
			if ((width > a3.width) && (height > a3.height) &&(quant <= 100)){
				app.models.order.set({type: "wide"}); //Уходим на широкоформтаку
			}
			else{
				app.models.order.set({type: "offset"}); //Уходим на оффсет
			}
			app.models.order.trigger("calc");
		}

	},

	labelType: function(){
		var type = this.model.get("type");

		switch(type){
			case "digit":
				this.model.set({type_label: "Цифровая"});
				break;

			case "offset":
				this.model.set({type_label: "Оффсетная"});
				break;

			case "wide":
				this.model.set({type_label: "Широкоформатная"});
				break;

			default:
				this.model.set({type_label: "malfunction"});
		}
	},

	resize: function(){
		var senddata = {
			width:  		this.model.get("width"),
			height: 		this.model.get("height"),
			quant:  		this.model.get("quant"),
			add_trim: 		this.model.get("add_trim"),
			add_print_area: this.model.get("add_print_area")
		};

		var that = this;
		return $.ajax({
				url: "/recounter/",
				data: senddata,
				success: function(data){
					that.model.set(data);
					app.log(data);
				},
				error: function(error){
					app.log(error);
					$("#alert").after("<div id='status' class='alert alert-error'><strong>Error "+ error.status + " :</strong> "+ error.statusText + "</div>");
					$('#send').button('reset');
				}
			}
		)
	},

	calc: function(){
		var type = this.model.get("type");
		var that = this;
		var senddata = {
			"width": 			this.model.get("width"),
			"height": 			this.model.get("height"),
			"param_value": 		this.model.get("param_value"),
			"number_of_lists": 	this.model.get("number_of_lists"),
			"quant": 			this.model.get("quant"),
			"slices": 			this.model.get("slices"),
			"chroma": 			this.model.get("chroma"),
			"format": 			this.model.get("format"),
			"add_lamin": 		this.model.get("add_lamin"),
			"add_trim": 		this.model.get("add_trim"),
			"add_print_area": 	this.model.get("add_print_area"),
			"add_big": 			this.model.get("add_big")
		};

		if (senddata.add_lamin) _.extend(senddata,{"lamin_name": this.model.get("lamin_name")});
		if (senddata.add_big) 	_.extend(senddata,{"big_count": this.model.get("big_count"), "big_align": this.model.get("big_align")});

		$.ajax({
			url: "/" + type + "/",
			data: senddata,
			success: function(data){
				//app.log(data);
				that.model.set({order_cost:""});
				that.model.set(data);
				$('#send').button('reset');
			},
			error: function(error){
				app.log(error);
				$("#alert").after("<div id='status' class='alert alert-error'><strong>Error "+ error.status + " :</strong> "+ error.statusText + "</div>");
				$('#send').button('reset');
			}
		});
	},

	renderLayout: function(){
		var lay={};
		lay.rows   = parseInt(app.models.order.get("rows"));
		lay.cols   = parseInt(app.models.order.get("cols"));
		lay.wid_a3 = parseInt(app.models.order.get("wid_a3"));
		lay.hei_a3 = parseInt(app.models.order.get("hei_a3"));
		lay.print  = parseInt(app.models.order.get("trim")); //запечатка
		lay.trim   = parseInt(app.models.order.get("dop")); //подрезка
		lay.pos    = app.models.order.get("pos");
		lay.big		= app.models.order.get("add_big");

		if (lay.pos){
			lay.width  = parseInt(app.models.order.get("width"));
			lay.height = parseInt(app.models.order.get("height"));
		}
		else
		{
			lay.height = parseInt(app.models.order.get("width"));
			lay.width  = parseInt(app.models.order.get("height"));
		}

		if (lay.big){
			lay.big_count = app.models.order.get("big_count");
			lay.big_align = app.models.order.get("big_align");
		}

		$("#layout").html("");
		var paper = Raphael("layout",lay.wid_a3+25, lay.hei_a3+20);
		// Creates canvas
		paper.rect(0,0,lay.wid_a3, lay.hei_a3);
		for (var i = 0; i < lay.cols;i+=1){
			for (var j = 0; j < lay.rows;j+=1){
				lay.rowC = i*(lay.width +lay.trim)+lay.print;//отрисовка порезки
				lay.colC = j*(lay.height+lay.trim)+lay.print;
				lay.rowB = i*(lay.width +lay.trim)+lay.print+lay.trim;//отрисовка изделия
				lay.colB = j*(lay.height+lay.trim)+lay.print+lay.trim;

				paper.rect(lay.rowB,lay.colB, lay.width , lay.height)
					 .attr({"gradient": "90-#0055cc-#0088cc","stroke-width": 0, "stroke": "#fff"});
				paper.rect(lay.rowC,lay.colC, lay.width+2*lay.trim, lay.height+2*lay.trim)
					 .attr({"stroke-width": 1, "stroke": "#999"});
				if (lay.big){
					if (lay.big_align == "horizontal"){
						if (lay.big_count == 2) {
							paper.rect(lay.rowB, lay.colB+lay.height/3, lay.width, 1).attr({fill:"#ea412c", "stroke-width": 0});
							paper.rect(lay.rowB, lay.colB+lay.height/3*2, lay.width, 1).attr({fill:"#ea412c", "stroke-width": 0});
						}
						else paper.rect(lay.rowB, lay.colB+lay.height/2, lay.width, 1).attr({fill:"#ea412c", "stroke-width": 0});
					}
					else{
						if (lay.big_count == 2) {
							paper.rect(lay.rowB+lay.width/3, lay.colB, 1, lay.height).attr({fill:"#ea412c", "stroke-width": 0});
							paper.rect(lay.rowB+lay.width/3*2, lay.colB, 1, lay.height).attr({fill:"#ea412c", "stroke-width": 0});
						}
						else paper.rect(lay.rowB+lay.width/2, lay.colB, 1, lay.height).attr({fill:"#ea412c", "stroke-width": 0});
					}
				}

			}
		}
		paper.text(lay.wid_a3/2, lay.hei_a3+10,lay.wid_a3);
		paper.text(lay.wid_a3+15,lay.hei_a3/2, lay.hei_a3);
		lay.out={layout: paper.toJSON()};
		app.models.order.set(lay.out);
		return this;
	},


	render: function(){
		app.log(this.model.toJSON());
		$(this.el).html(this.template(this.model.toJSON()));
		this.model.trigger("layout");
		$(this.el).slideDown();
		return this
	}
});

var ShowOrder = Backbone.View.extend({
	el: $("#order"),

	template:_.template($("#template-order").html()),

	initialize: function(){
		this.model.bind("change:order_cost", this.render, this)
		this.model.bind("change:type_label", this.render, this)
	},

	events: {
		"click #send-order": "send"
	},

	send: function(e){
		e.preventDefault();

		var order = this.model.toJSON(),
			append = { email: $("#email").val()},
			$el = $(this.el);

		$("#status").remove();
		_.extend(order,append);

		$.ajax({
			url: "/add-order/",
			data: order,
			success: function(data){
				$el.before("<div id='status' class='block alert-success'><strong>Ваш заказ отправлен на обработку.</strong> Скоро с вами свяжеться менеджер.</div>");
				$el.slideUp();
				app.log(order);
			},
			error: function(error){
				app.log(error);
				$el.after("<div id='status' class='block alert-error'><strong>Error "+ error.status + " :</strong> "+ error.statusText + "</div>");
				//$("#results").slideUp();
				$('#send').button('reset');
			}
		});
	},

	render: function(){
		$(this.el).html(this.template(
			this.model.toJSON()
		));
		that = this;
		var uploader = new qq.FileUploader({
			action: uploadUrl,
			element: $('#fileUpload')[0],
			multiple: true,
			onComplete: function(id, fileName, responseJSON) {
				if(responseJSON.success) {
					app.log("success!");
				} else {
					app.log("upload failed!");
				}
				that.model.set({ file: fileName});
			},
			onAllComplete: function(uploads) {
				// uploads is an array of maps
				// the maps look like this: {file: FileObject, response: JSONServerResponse}
				//that.model.set
				app.log("Success");
			},
			params: {
				'csrf_token': djangoToken,
				'csrf_name': 'csrfmiddlewaretoken',
				'csrf_xname': 'X-CSRFToken'
			}
		});
		$(this.el).slideDown();
		return this
	}

});

/*
var Controller = Backbone.Router.extend({
	routes: {
		"": "start", // Пустой hash-тэг
		"!/": "start", // Начальная страница
		"!/success": "success", // Блок удачи
		"!/paper-choose": "paperСhoose",// блок выбора бумаги
		"!/error": "error" // Блок ошибки
	},

	start: function () {
		app.models.State.set({ state: "start" });
	},

	success: function () {
		app.models.State.set({ state: "success" });
	},

	paperСhoose: function(){
		app.models.State.set({ state: "paper-choose" });
	},

	error: function () {
		app.models.State.set({ state: "error" });
	}
});
*/

jQuery(document).ready(function($){

	app.models.State = new AppState();
	app.models.order = new Order();


	app.cols.papers = new Papers();
	app.cols.formats = new Formats();
	app.cols.lamins = new Lamins();

	//app.controller = new Controller(); // Создаём контроллер


	app.views.page = new Block({model: app.models.State}); // создадим объект
	app.views.result = new Result({model: app.models.order});
	app.views.order = new ShowOrder({model: app.models.order});


	app.models.State.trigger("change"); // Вызовем событие change у модели
	//app.models.order.bind("change:width",function(){});
	/*app.models.State.bind("change:state", function () { // подписка на смену состояния для контроллера
		var state = this.get("state");
		if (state == "start")
			app.controller.navigate("!/", false); // false потому, что нам не надо
		// вызывать обработчик у Router
		else
			app.controller.navigate("!/" + state, false);
	});
	*/
	//Backbone.history.start();  // Запускаем HTML5 History push

});

