function openDialog(targetType, targetNum) {
	if (confirm("Are you sure you want to delete this " + targetType + "?")) {
		document.location.href = $("#URL_".concat("", targetNum)).attr("data-url");
	}
}

function goToTop() {
	window.scrollTo(0, 0);
}
