$ ->
	url_base = "http://localhost:8080"
	params = {}

	$.ajaxSetup
	  contentType: "application/json; charset=utf-8"

	$("#wine-form").on "submit", (e) ->
		do e.preventDefault
		form = new FormData
		has = (i) -> i.val() isnt '' 
		# name
		name = $ "#wine-name"
		return if not has name
		form.append 'name', name.val()
		# dor
		dor = $ "#wine-do"
		form.append 'do', dor.is(":checked")
		# type
		type = $ "#wine-type"
		form.append 'type', type.val()
		if do type.val is "red"
			# cask
			cask = $ "#wine-cask"
			form.append 'cask', cask.val() if has cask
			# bottle
			bottle = $ "#wine-bottle"
			form.append 'bottle', bottle.val() if has bottle
		# grade
		grade = $ "#wine-grade"
		form.append 'grade', grade.val() if has grade
		# price
		price = $ "#wine-price"
		form.append 'price', price.val() if has price
		# size
		size = $ "#wine-size"
		form.append 'size', size.val() if has size
		# varietals
		varietals = $ "#wine-varietals"
		form.append 'varietals', varietals.val().split(/[\s,]+/) if has varietals
		# file
		file = $ "#wine-file"
		form.append 'photo', file.prop('files')[0], file.val() if has file

		$.ajax
			type: 'POST'
			url: "#{url_base}/fake"
			contentType: 'multipart/form-data'
			headers: {"Authorization": "Basic #{params.auth_basic}"}
			data: form
			cache: off
			processData: off
			success: (data) ->
			    alert(data)

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