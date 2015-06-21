function update(obj, key, val){
	if( typeof(obj[key]) == "object" && typeof(val) == "object"){
		for( inner_key in obj[key]){
			update(obj[key], inner_key, val[inner_key]);
		}
	}else{
		obj[key] = val;
	}
}

Environment = {
	init: function(config){
		update(Environment, "config", config)
	},
	config: {
		container: undefined
	},
	render: function(html){
		$(Environment.config.container).html(html);
	}
};

App = {
	init: function(config){
		update(this, "config", config)
	},
	config: {
		api: {
			list: undefined,
			details: undefined,
			router: undefined
		}
	},
	cache: {
		list: undefined
	},
	list: function(cb_fn){
		if(this.cache.list){
			cb_fn(this.cache.list)
		}else{
			var _this = this
			$.get(this.config.api.list, function(data, statusText, jqXhr){
				_this.cache.list = data;
				cb_fn(data);
			});
		}
	},
	load: function(url){
		$.get(url, Environment.render);
	},
	get: function(app_id){
		var endpoint = App.config.api.router.replace("--$id--", app_id);
		var app = {
			set: false,
			config: {
				endpoint: endpoint
			},
			get_absolute_path: function(path){
				if(path == undefined || path == "/"){
					path = ""
				}
				return app.config.endpoint.replace("--$path--", path);
			},
			get: function(path, cb){
				$.get(app.get_absolute_path(path), cb);
			},
			post: function(path, data, cb){
				$.post(app.get_absolute_path(path), data, cb);
			},
			load: function(path){
				app.get(path, Environment.render);
			}
		}
		return app
	}
};

Service = {
	init: function(config){
		update(Service, "config", config)
	},
	config: {
		api: {
			list: undefined,
			details: undefined,
			router: undefined
		}
	},
	cache: {
		list: undefined
	},
	list: function(cb_fn){
		if(Service.cache.list){
			cb_fn(Service.cache.list)
		} else {
			$.get(this.config.api.list, function(data, statusText, jqXhr){
				Service.cache.list = data;
				cb_fn(data);
			});
		}
	},
	get: function(service_id){
		var endpoint = Service.config.api.router.replace("--$id--", service_id);
		var service = {
			set: false,
			config: {
				endpoint: endpoint
			},
			get_absolute_path: function(path){
				if(path == undefined || path == "/"){
					path = ""
				}
				return service.config.endpoint.replace("--$path--", path);
			},
			get: function(path, cb){
				$.get(service.get_absolute_path(path), cb);
			},
			post: function(path, data, cb){
				$.post(service.get_absolute_path(path), data, cb);
			}
		}
		return service
	}
};
