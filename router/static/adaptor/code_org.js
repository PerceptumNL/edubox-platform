jQuery.ajaxPrefilter(function(options){ if(options.url.startsWith("https://studio.code.org/")){ options.url = options.url.replace("https://studio.code.org/","/"); } })
