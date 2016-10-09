
(function(window){
	var source = null; 
	var template = null;

	var response = {
		  "columns": [
		    "PATIENTID",
		    "UID1",
		    "DISEASE",
		    "SAMPLEID",
		    "PROBEID",
		    "EXP"
		  ],
		  "rows": [
		    [
		      "92978",
		      "40838030",
		      "AML",
		      "187508",
		      "10166204",
		      "9"
		    ],
		    [
		      "92978",
		      "79032664",
		      "AML",
		      "187508",
		      "12835461",
		      "161"
		    ],
		    [
		      "92978",
		      "83460852",
		      "AML",
		      "187508",
		      "74267188",
		      "163"
		    ]
		]}

	var querySuccess = function (data){
		$("#table-container").html(template(data));
		$("#table-name").html(data.tablename);
		attachListeners();
		$("button[type='submit']").removeClass("disabled");
	}

	var queryError = function (){
		alert("error");
		attachListeners();
	}

	var querySubmit = function (event){
		removeListeners();
		$("button[type='submit']").addClass("disabled");

		event.preventDefault();
		clearTable();
		$.get({
			url: $(this).attr("action"),
			dataType: "json",
			data: $(this).serialize(),
			success: querySuccess,
			error: queryError
		});

	}
	// Helpers
	var clearTable = function () {
		$("#table-container").empty();
		$("#table-name").empty();
	}

	var attachListeners = function (){
		$(".form-horizontal").off("submit").on("submit", querySubmit);
	}

	var removeListeners = function (){
		$(".form-horizontal").off("submit");
	}

	var initialize = function () {
		
		// var htmlString = template(response);

		// $("#table-container").html(htmlString);
		Handlebars.registerHelper("inc", function(value, options)
		{
		    return parseInt(value) + 1;
		});
		source = $("#table-template").html();
		template = Handlebars.compile(source);
		clearTable();
		attachListeners();
	}

	$(document).ready(initialize);	
})(window);
