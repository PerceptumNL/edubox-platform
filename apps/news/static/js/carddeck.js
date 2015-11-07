function annotate_special_word(phrase){
	var phrase_parts = phrase.split("'''");
	var special_phrase;
	if(phrase_parts.length == 1){
		special_phrase = phrase;
	}else{
		for(var i = 1; i < phrase_parts.length; i+=2){
			phrase_parts[i] =
				"<span class='word'>"+phrase_parts[i]+"</span>";
		}
		special_phrase = phrase_parts.join("");
	}
	return special_phrase;
}


function CardDeck(container, decks, _self){
	_self = (_self == undefined ? this : _self);

	_self.create_empty_card = function(){
		return $("<div class='element-item col-lg-4 col-md-6 col-xs-12'>");
	}

	_self.load_deck = function(deck){
		for(var i = 0; i < deck.length; i++){
			if(deck[i]['type'] in window){
				var card = _self.create_empty_card();
				window[deck[i]['type']](card, deck[i]['data']);
				$(container).isotope('insert', card);
				$(container).isotope('updateSortData', card);
			}
		}
	}

	for(var i = 0; i < decks.length; i++){
		api_call(decks[i]['url'], decks[i]['params'], 'get', _self.load_deck)
	}

	_self.close = function(){
		elems = $(container).isotope('getItemElements');
		$(container).isotope('remove', elems);
	}
}

function DashboardCardDeck(container, decks, _self){
	_self = (_self == undefined ? this : _self);
	$.extend(_self, new CardDeck(container, decks, _self));

	_self.create_empty_card = function(){
		return $("<div class='element-item'>");
	}
}

function Card(container, order, title, _self){
	_self = (_self == undefined ? this : _self);

	_self.create_content_container = function(){
		content_container = $("<div class='well'></div>");
		content_container.append($("<div class='title'>"+title+"</div>"))
		container.append(content_container);
		return content_container;
	}
	container.attr("data-order", order);
}

function DictTermCard(container, data){
	var _parent = new Card(container, 0,
			"Betekenis van <b>"+data['word']+"</b>");
	container.addClass("dict_term_card");
	var content = _parent.create_content_container();
	content.append($('<div class="word">'+data['word']+'</div>'));
	content.append($('<div class="category">('+data['category']+')</div>'));
	if(!$.isEmptyObject(data['meanings'])){
		var meanings = $("<ol>");
		content.append(meanings);
		for(index in data['meanings']){
			var meaning = data['meanings'][index];
			var item = $('<li>')
			meanings.append(item);
			definition_phrase = annotate_special_word(meaning['definition'])
			item.append($('<div class="definition">').html(definition_phrase));
			if(meaning['example']){
				example_phrase = annotate_special_word(meaning['example'])
				item.append($('<div class="example">').html(example_phrase));
			}
			if(meaning['synonyms']){
				item.append($('<div class="synonyms">')
					.text(meaning['synonyms'].join(", ")));
			}
			if(meaning['antonyms']){
				item.append($('<div class="antonyms">')
					.text(meaning['antonyms'].join(", ")));
			}
		}
	}
}

function DictVerbConjCard(container, data){
	var _parent = new Card(container, 50, "Vervoegingen van <b>"+data['word']+"</b>");
	container.addClass("dict_verb_conj_card");
	var content = _parent.create_content_container();
	table_part1 = $("<table class='table verb_conj_table'>");
	table_part1.append($("<tr>").html(
			"<th></th><th>tegenwoordige tijd</th>"+
			"<th>verleden tijd</th>"));
	table_part1.append($("<tr>").html(
			"<td>ik</td><td>"+data['1ps']+"</td>"+
			"<td>"+data['past_single']+"</td></tr>"));
	table_part1.append($("<tr>").html(
			"<td>jij</td><td>"+data['2ps']+"</td>"+
			"<td>"+data['past_single']+"</td></tr>"));
	table_part1.append($("<tr>").html(
			"<td>hij/zij</td><td>"+data['2ps']+"</td>"+
			"<td>"+data['past_single']+"</td></tr>"));
	table_part1.append($("<tr>").html(
			"<td>wij</td><td>"+data['plural']+"</td>"+
			"<td>"+data['past_plural']+"</td>"));
	content.append(table_part1);
	table_part2 = $("<table class='table verb_conj_table'>");
	table_part2.append($("<tr>").html(
			"<th>voltooid deelwoord</th>"+
				"<td>"+data['auxiliary']+" "+data['past_participle']+
			"</td>"));
	content.append(table_part2);
}

function FormCard(container, data){
	var _parent = new Card(container, 100, data['title']);
	container.addClass("form_card");
	var content = _parent.create_content_container();
	content.append($("<textarea>").attr("placeholder",
				"Typ hier je bericht..."));
	submit_btn = $("<button>").addClass("btn btn-md btn-block");
	submit_btn.text("Verstuur je bericht");
	content.append(submit_btn);
}

function CustomCard(container, data){
	var _parent = new Card(container, 100, data['title']);
	container.addClass("custom_card");
	var content = _parent.create_content_container();
	content.append($("<p>").text(data['content']));
}

function DashboardCard(container, order, title, _self){
	_self = (_self == undefined ? this : _self);
	$.extend(_self, new Card(container, order, title, _self));

	_self.create_content_container = function(){
		var content_container = ($("<div class='statistics-card'></div>")
				.append($("<div class='title'>"+title+"</div>")));
		container.append($("<paper-shadow z='1'></paper-shadow>")
				.append(content_container));
		return content_container;
	}
}

function DashboardTotalCard(container, data, _self){
	_self = (_self == undefined ? this : _self);
	$.extend(_self, new DashboardCard(container, 100, data['title']));
	container.addClass("total_card");
	var content = _self.create_content_container();
	api_call(data['source'], {}, 'get', function(totals){
		var dlist = $('<dl>');
		dlist.append($('<dt>').text('Deze week'));
		dlist.append($('<dd>').text(totals['week']));
		dlist.append($('<dt>').text('Deze maand'));
		dlist.append($('<dd>').text(totals['month']));
		dlist.append($('<dt>').text('In totaal'));
		dlist.append($('<dd>').text(totals['all']));
		content.append(dlist);
	})
}

