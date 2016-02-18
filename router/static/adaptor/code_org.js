jQuery.ajaxPrefilter(function(options){ if(options.url.startsWith("https://studio.code.org/")){ options.url = options.url.replace("https://studio.code.org/","/"); } });
jQuery("a").each(function(){ this.href = this.href.replace("https://studio.code.org/", "/"); });
jQuery("form").each(function(){ this.action = this.action.replace("https://studio.code.org/", "/"); })
