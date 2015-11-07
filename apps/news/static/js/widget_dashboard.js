$.widget( "readmore.dashboard", {
	// Default options
	options: {
//		controlwidget: "articleviewer",
		cover: null,
		carddecks: [{ 'url': '/widgets/dictionary/', 'params': {'word':"%%PARAM%%"}}]
	},
	_create: function(){
		var _self = this;
		_self.load()
		// Find any instance of the controlwidget and
		// bind to the `wordclick' event
	},
	decks: function(param){
		decks = []
		for(var i = 0; i < this.options.carddecks.length ; i++){
			var url = this.options.carddecks[i].url;
			var params = {};
			for(key in this.options.carddecks[i].params){
				params[key] = this.options.carddecks[i].params[key]
					.replace("%%PARAM%%", param);
			}
			decks.push({'url':url, 'params':params});
		}
		return decks;
	},
    load: function(param){
        var _self = this;
		if(this.options.cover){
			if($(this.options.cover).hasClass('open')){
				this.carddeck.close();
			}else{
				$(this.options.cover).addClass('open');
				$(this.options.cover).find("#closeCover").click(
						function(){ window.history.back(); });
				$(this.options.cover).find("#closeOnBackground").click(
						function(){ window.history.back(); });
			}
		}
		this.carddeck = new DashboardCardDeck(this.element, this.decks(param));
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
