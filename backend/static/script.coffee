$ ->
	url_base = "http://localhost:8080"
	params = {}

	$.ajaxSetup
	  contentType: "application/json; charset=utf-8"

	$("#wine-form").on "submit", (e) ->
		do e.preventDefault
		form = new FormData
		has = (i) -> i.val() isnt '' 
		info = {}
		info['name'] = $("#wine-name").val()
		info['do'] = $("#wine-do").is(":checked")
		type = $ "#wine-type"
		info['type'] = type.val()
		if do type.val is "red"
			cask = $ "#wine-cask"
			info['cask'] = parseFloat cask.val() if has cask
			bottle = $ "#wine-bottle"
			info['bottle'] = parseFloat bottle.val() if has bottle
		grade = $ "#wine-grade"
		info['grade'] = parseFloat grade.val() if has grade
		price = $ "#wine-price"
		info['price'] = parseFloat price.val() if has price
		size = $ "#wine-size"
		info['size'] = parseFloat size.val() if has size
		varietals = $ "#wine-varietals"
		info['varietals'] = varietals.val().split(/\s*,+\s*/) if has varietals
		file = $ "#wine-file"
		path = file.val().split('\\')

		form.append 'data', JSON.stringify(info)
		form.append 'photo', file.prop('files')[0], path[path.length-1] if has file

		$.ajax
			type: 'POST'
			url: params.upload_url
			headers: {"Authorization": "Basic #{params.auth_basic}"}
			data: form
			contentType: off
			# cache: off
			# processData: off
			success: (data) ->
				$('#wine-form').addClass("hide")
				$("#big-title").after "
					<div class='alert alert-success'> 
					Vino '#{data.created}' añadido
					</div>"

	$('#auth-form').on "submit", (e) ->
		do e.preventDefault
		vals = do $(@).serializeArray
		json = {}
		for v in vals
			json[v.name] = v.value
		json = JSON.stringify(json)

		$.post "#{url_base}/submit_wine", json, (data) ->
			params.auth_basic = data.auth_basic
			params.upload_url = data.upload_url
			$('#auth-form, #wine-form').toggleClass("hide")

		.fail ->
			$("input[type=text], input[type=password]").val ''
			$("#big-title").after "
				<div class='alert alert-danger'> 
				<button class='close' data-dismiss='alert'><span>&times;</span></button> 
				Error de autenticación 
				</div>"

	$("select").on "change", ->
		val = do $("select option:selected").val
		if val isnt "red"
			$("#red-options").addClass("hide")
		else
			$("#red-options").removeClass("hide")

	$("label").css("margin-top","10px")