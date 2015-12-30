$ ->
	url_base = "http://localhost:8002"

	insertWines = (wines) ->
		wines_div = $ "#wines"
		wines_div.empty() 
		for w in wines
			# row = $ "<div class='row'></div>"
			row = $.parseHTML "<div class='row'>
									<div class='panel panel-primary'>
										<div class='panel-body' id='panel-#{w.url}'->
										</div>
									</div>
								</div>"
			wines_div.append row
			panel_div = $ "#panel-#{w.url}"
			panel_div.append "<input type='checkbox' name='vehicle' value='#{w.url}'> <b >#{w.name}</b> "
			panel_div.append "- #{w.grade} grados " if w.grade
			panel_div.append "- #{w.size} centilitros " if w.size
			panel_div.append "- #{w.price} € " if w.price
			panel_div.append "- Denominación de Origen La Mancha " if w.do
			panel_div.append "- #{w.cask} años de envejecimiento en barrica " if w.cask
			panel_div.append "- #{w.bottle} años de envejecimiento en botella " if w.bottle

	# AJAX functions
	$.ajaxSetup
	  contentType: "application/json; charset=utf-8"

	filter = (type=null) ->
		if type?
			$.get url_base+"/filterByType/#{type}", (data) ->
				insertWines data['all'] 
		else
			$.get url_base+"/allWines", (data) ->
				insertWines data['all'] 

	do filter
	$("#pink-wines").on "click", filter.bind(@, "pink")
	$("#red-wines").on "click", filter.bind(@, "red")
	$("#white-wines").on "click", filter.bind(@, "white")
	$("#all-wines").on "click", filter.bind(@, null)

	$("#filter-name").on "click", ->
		name = do $("#name").val
		if not name
			$("#name-filter").addClass "has-error" 
			return
		$(".has-error").removeClass("has-error")
		$.get url_base+"/filterByName/#{name}", (data) ->
			insertWines data['all']

	$("#filter-prices").on "click", ->
		min = parseFloat do $("#minimo").val
		max = parseFloat do $("#maximo").val
		if isNaN(min) or isNaN(max)
			$("#prices-filter").addClass "has-error" 
			return
		$(".has-error").removeClass("has-error")
		values = JSON.stringify({"min":min,"max":max})

		$.post url_base+"/filterByPrices", values, (data)->
			insertWines data['all']


	$("#create-cart").on "click", ->
		name = do $("#cart-name").val
		wines = $("input:checkbox:checked").map -> $(@).val()
		values = "items":wines.get()
		values['name'] = name if name
		values = JSON.stringify(values)

		$.post url_base+"/postCart", values, (data) ->
			$("#big-title").after "
				<div class='alert alert-success'> 
				<button class='close' data-dismiss='alert'><span>&times;</span></button> 
				Carrito '#{data['created']}' creado 
				</div>"


