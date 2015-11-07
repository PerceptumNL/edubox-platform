$.widget( "readmore.carddeck", {
	// Default options
	options: {
		controlwidget: "articleviewer",
		cover: null,
		carddecks: [{ 'url': '/widgets/dictionary/', 'params': {'word':"%%WORD%%"}}]
	},
	_create: function(){
		var _self = this
		// Find any instance of the controlwidget and
		// bind to the `wordclick' event
		$(":readmore-"+this.options.controlwidget).bind(
			this.options.controlwidget+"wordclick",
			function(event, data){
				location.hash = "#cover-"+data['word'];
			}
		)
		$(window).hashchange(function(){
			if(location.hash == ''){
				_self.close(_self.options.cover);
			}else{
				hash_parts = location.hash.split("-");
				if(hash_parts[0] == '#cover'){
					_self.load(hash_parts[1])
				}
			}
		});
		$(this.options.cover).find("#closeCover").click(
				function(){
					window.history.back();
					return false;
				});
		$(this.options.cover).find("#closeOnBackground").click(
				function(){
					window.history.back();
					return false;
				});
	},
	decks: function(word){
		decks = []
		for(var i = 0; i < this.options.carddecks.length ; i++){
			var url = this.options.carddecks[i].url;
			var params = {};
			for(key in this.options.carddecks[i].params){
				params[key] = this.options.carddecks[i].params[key]
					.replace("%%WORD%%", word);
			}
			decks.push({'url':url, 'params':params});
		}
        $.post( "/add_to_history/", {
                article: location.pathname.split('/')[3],
                value: word,
                type: 'word',
                csrfmiddlewaretoken: getCookie('csrftoken'),
        });
		return decks;
	},
    load: function(word){
        var _self = this;
		if(this.options.cover){
			if($(this.options.cover).hasClass('open')){
				this.carddeck.close();
			}else{
				$(this.options.cover).addClass('open');
			}
		}
		this.carddeck = new CardDeck(this.element, this.decks(word));
	},
    close: function(cover){
		if(cover){
		    $(cover).removeClass('open');
        }
        $('.lastSelected.prevSelected').removeClass('lastSelected');
        $('#selected').addClass('lastSelected');
        $('#selected').addClass('prevSelected');
        $('#selected').removeAttr('id');
        this.carddeck.close();
    }
})
