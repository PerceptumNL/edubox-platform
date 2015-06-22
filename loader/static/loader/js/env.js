function update(obj, key, val){
	if( typeof(obj[key]) == "object" && typeof(val) == "object"){
		for( inner_key in obj[key]){
			update(obj[key], inner_key, val[inner_key]);
		}
	}else{
		obj[key] = val;
	}
}

(function(window, $, undefined){
	window.Environment = {
		init: function(config){
			update(Environment, "config", config)
		},
		cache: {},
		config: {
			container: undefined
		},
		render: function(html){
			$(Environment.config.container).html(html);
		}
	};
})(window, jQuery);

(function(window, $, undefined){
	window.RESTObject = function(base_url){
		this.get_absolute_path = function(relative_path){
			if( !relative_path || relative_path == "/"){
				relative_path = ""
			}
			return base_url.replace("--$path--", relative_path);
		};
		this.get = function(rel_path, cb_fn){
			if(cb_fn == undefined){ cb_fn = Env.render; }
			$.get(_this.get_absolute_path(path), cb);
		};
		this.post = function(rel_path, data, cb_fn){
			if(cb_fn == undefined){ cb_fn = Env.render; }
			$.post(_this.get_absolute_path(path), data, cb);
		};
	}
})(window, jQuery);

(function(Env, $, undefined){
	function App(id, title, icon, base_url){
		var _this = this;
		_this.prototype = new RESTObject(base_url)

		_this.get_id = function(){ return id; };
		_this.get_title = function(){ return title; };
		_this.get_icon = function(){ return icon; };

		_this.get = function(rel_path, cb_fn){
			if(cb_fn == undefined){ cb_fn = Env.render; }
			return _this.prototype.get(rel_path, cb_fn);
		};
		_this.load = function(){ _this.get(); };

		_this.post = function(rel_path, data, cb_fn){
			if(cb_fn == undefined){ cb_fn = Env.render; }
			return _this.prototype.post(rel_path, data, cb_fn);
		};
	}

	// Add Env::cache slot, if necesary
	Env.cache.apps = Env.cache.apps || undefined;
	// Add Env::config slots, if neccary
	var config = Env.config.apps = Env.config.apps || {}
	config.api = config.api || {};
	config.api.list = config.api.list || undefined;
	config.api.details = config.api.details || undefined;
	config.api.router = config.api.router || undefined;
	// Define Env::apps function to retrieve all App instances, if necessary
	Env.apps = Env.apps || function(cb_fn){
		if( Env.cache.apps ){
			cb_fn(Env.cache.apps);
		}else{
			$.get(config.api.list, function(data, statusText, jqXhr){
				Env.cache.apps = [];
				for(var i = 0; i < data.length; i++){
					d = data[i];
					Env.cache.apps.push(new App(
						d['id'],
						d['title'],
						d['icon'],
						config.api.router.replace("--$id--", d['id'])
					));
				}
				cb_fn(Env.cache.apps);
			});
		}
	};
	// Define Env::app function to retrieve one App instance, if neccesary
	Env.app = Env.app || function(app_id, cb_fn){
		if( Env.cache.apps ){
			var apps = Env.cache.apps;
			for(var i = 0; i < apps.length; i++){
				if( apps[i].get_id() == app_id ){
					cb_fn(apps[i]);
				}
			}
			var details_url = config.api.details.replace("--$id--", app_id);
			$.get(details_url, function(data, statusText, jqXhr){
				var app = new App(
					data['id'],
					data['title'],
					data['icon'],
					config.api.router.replace("--$id--", datum['id'])
				);
				apps.push(app);
				cb_fn(app);
			});
		}
	}
})(Environment, jQuery);

(function(Env, $, undefined){
	function Service(name, title, base_url){
		var _this = this;
		this.prototype = new RESTObject(base_url)

		this.get_name = function(){ return name; };
		this.get_title = function(){ return title; };
	}

	// Add Env::cache slot, if necesary
	Env.cache.services = Env.cache.services || undefined;
	// Add Env::config slots, if neccary
	var config = Env.config.services = Env.config.services || {};
	config.api = config.api || {};
	config.api.list = config.api.list || undefined;
	config.api.details = config.api.details || undefined;
	config.api.router = config.api.router || undefined;
	// Define Env::services function to retrieve Service instances, if necessary
	Env.services = Env.services || function(cb_fn){
		if( Env.cache.services ){
			cb_fn(Env.cache.services);
		}else{
			$.get(config.api.list, function(data, statusText, jqXhr){
				Env.cache.services = [];
				for(var i = 0; i < data.length; i++){
					d = data[i];
					Env.cache.services.push(new Service(
						d['name'],
						d['title'],
						config.api.router.replace("--$id--", d['id'])
					));
				}
				cb_fn(Env.cache.services);
			});
		}
	}
})(Environment, jQuery);
