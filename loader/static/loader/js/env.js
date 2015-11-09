/*******************************
 * VM Environment for web apps *
 * --------------------------- */

/* Recursive update of obj with key-value pair. */
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
	var local_rgx = /^\/\b[-a-zA-Z0-9@:%_\+.~#?&//=]*$/g;
	var remote_rgx = /^(http(s)?:\/\/.)?(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)$/g;
	window.Environment = {
		init: function(config){
			update(Environment, "config", config)
		},
		cache: {},
		config: {
			container: undefined,
		},
		render: function(url_or_content){
			$(Environment.config.container).empty();
			if(local_rgx.test(url_or_content)){
				$(Environment.config.container).append(
						$("<iframe>").attr('src', url_or_content));
			} else if(remote_rgx.test(url_or_content)){
				console.log("What to do with remote rendering?")
				$(Environment.config.container).append(
						$("<iframe>").attr('src', url_or_content));
			} else {
				$(Environment.config.container).html(url_or_content);
			}
		}
	};
})(window, jQuery);

(function(window, $, undefined){
	window.RESTObject = function(base_url){
		var _this = this;
		_this.get_absolute_path = function(relative_path){
			if( !relative_path || relative_path == "/"){
				relative_path = ""
			}
			return base_url.replace("--$path--", relative_path);
		};
		_this.get = function(rel_path, cb_fn){
			if(cb_fn == undefined){ cb_fn = window.Environment.render; }
			if(cb_fn == window.Environment.render){
				window.Environment.render(_this.get_absolute_path(rel_path));
			}else{
				$.get(_this.get_absolute_path(rel_path), cb_fn);
			}
		};
		_this.post = function(rel_path, data, cb_fn){
			if(cb_fn == undefined){ cb_fn = Env.render; }
			$.post(_this.get_absolute_path(rel_path), data, cb_fn);
		};
	}
})(window, jQuery);

(function(Env, $, undefined){
	Env.Router = {
		set: function(url){
			if(history.pushState){
				history.pushState({}, "", url);
				Env.Router.trigger();
			}else{
				document.location = url;
			}
		},
		cache: {
			url: undefined
		},
		_listeners: {},
		bind: function(pattern, cb_fn){
			if(typeof(patterm) == "object" && pattern.source){
				// If pattern is a RegExp object, retrieve the string
				pattern = pattern.source;
			}
			Env.Router._listeners[pattern] = Env.Router._listeners[pattern] || [];
			Env.Router._listeners[pattern].push(cb_fn);
		},
		trigger: function(){
			var url = document.location.pathname;
			if( Env.Router.cache.url == url){
				return;
			}else{
				Env.Router.cache.url = url;
			}
			for(pattern in Env.Router._listeners){
				var regex = RegExp(pattern);
				if(regex.test(url)){
					var callbacks = Env.Router._listeners[pattern];
					var matches = regex.exec(url);
					// Ignore full match
					matches.shift();
					for(var i = 0; i < callbacks.length; i++){
						callbacks[i].apply({}, matches);
					}
				}
			}
		},
		poll: function(){
			Env.Router.trigger()
			setTimeout(Env.Router.poll, 50);
		}
	}
	Env.Router.bind("^/?$", function(){
		Env.render("App");
	});
	$(Env.Router.poll);
})(Environment, jQuery);

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
		_this.load = function(rel_path){
			// Load app into environment
			Env.cache.current_app = _this;
			_this.get(rel_path);
		};

		_this.post = function(rel_path, data, cb_fn){
			if(cb_fn == undefined){ cb_fn = Env.render; }
			return _this.prototype.post(rel_path, data, cb_fn);
		};
	}

	// Add Env::cache slots, if necesary
	Env.cache.apps = Env.cache.apps || undefined;
	Env.cache.current_app = Env.cache.current_app || undefined;
	// Add Env::config slots, if neccary
	var config = Env.config.apps = Env.config.apps || {}
	config.api = config.api || {};
	config.api.list = config.api.list || undefined;
	config.api.details = config.api.details || undefined;
	config.api.router = config.api.router || undefined;
	// Define Env::apps function to retrieve all App instances, if necessary
	Env.apps = Env.apps || function(cb_fn){
		if(cb_fn == undefined){
			return Env.cache.apps
		}else if( Env.cache.apps ){
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
	Env.app = Env.app || function(){
		if( arguments.length == 1 ){
			app_id = arguments[0];
			if( Env.cache.apps ){
				var apps = Env.cache.apps;
				for(var i = 0; i < apps.length; i++){
					if( apps[i].get_id() == parseInt(app_id) ){
						return apps[i];
					}
				}
			}else{
				return undefined;
			}
		}else if(arguments.length == 2){
			// Call: app(app_id, cb_fn)
			// -> Retrieve details for app_id and call cb_fn with app object.
			app_id = arguments[0];
			cb_fn = arguments[1];
			if( Env.cache.apps ){
				var apps = Env.cache.apps;
				for(var i = 0; i < apps.length; i++){
					if( apps[i].get_id() == parseInt(app_id) ){
						if(cb_fn == undefined){
							return apps[i]
						}else{
							cb_fn(apps[i]);
						}
					}
				}
			}else{
				Env.apps(function(apps){
					for(var i = 0; i < apps.length; i++){
						if( apps[i].get_id() == parseInt(app_id) ){
							cb_fn(apps[i]);
						}
					}
				});
			}
		}else if( arguments.length == 0 ){
			// Call: app()
			// -> Return App instance of currently loaded app, or undefined.
			return Env.cache.current_app
		}
	}
	// Bind app view
	Env.Router.bind("/app/([0-9]+)(/.*)", function(app_id, path){
		Env.app(app_id, function(app){ app.load(path); });
	});
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
		if(cb_fn == undefined){
			return Env.cache.services
		}else if( Env.cache.services ){
			cb_fn(Env.cache.services);
		}else{
			$.get(config.api.list, function(data, statusText, jqXhr){
				Env.cache.services = {};
				for(var i = 0; i < data.length; i++){
					d = data[i];
					Env.cache.services[d['name']] = new Service(
						d['name'],
						d['title'],
						config.api.router.replace("--$id--", d['id'])
					);
				}
				cb_fn(Env.cache.services);
			});
		}
	}
	// Define Env::service function to retrieve a Service instance
	Env.service = Env.service || function(service_name, cb_fn){
		if(cb_fn == undefined){
			if(Env.cache.services != undefined &&
					service_name in Env.cache.services){
				return Env.cache.services[service_name];
			}else{
				return undefined
			}
		}else if( Env.cache.services ){
			cb_fn(Env.cache.services[service_name]);
		}else{
			Env.services(function(services){
				cb_fn(services[service_name]);
			});
		}
	}
})(Environment, jQuery);
