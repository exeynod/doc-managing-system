function formValidation()
{
var emailid = document.getElementById('registerEmail')
var passid = document.getElementById('registerInputPassword');
var repeatPassid = document.getElementById('repeatPassword');
var erremailid = document.getElementById('errorEmail');
var errpassid = document.getElementById('errorPass');
var selectCompanyId = document.getElementById('selectCompany');
var selectError = document.getElementById('errorSelect');
var usernameId = document.getElementById('registerUsername');
var errorUsername = document.getElementById('errorUsername');

erremailid.style.display = 'none';
errpassid.style.display = 'none';
selectError.style.display = 'none';
errorUsername.style.display = 'none';

if (usernameId.value === '') {
	errorUsername.style.display = 'block';
	return false;
}

if (!correctEmail(emailid)) {
	erremailid.style.display = "block";
	return false;
}
else {
	erremailid.style.display = "none";
}
if(!matchesPasswords(passid, repeatPassid)) {
	errpassid.style.display = "block";
	return false;
}
else {
	errpassid.style.display = "none";
}
if (!companyChoosed(selectCompanyId)) {
	selectError.style.display = "block";
	return false;
}
return true;
}

function correctEmail(emailId) {
	if (emailId.value.includes("@"))
		return true;
	return false;
}

function matchesPasswords(p1, p2) {
	if (p1.value === p2.value)
		return true;
	return false;
}

function companyChoosed(propertiesId) {
	if (propertiesId.selectedIndex !== 0) {
		return true;
	}
	return false;
}

function switchForms()
{
	var loginFormid = document.getElementById('loginForm');
	var loginFormButtonId = document.getElementById('loginButton');
	var registerFormId = document.getElementById('registerForm');
	var notAmemberHint = document.getElementById('registered');
	var alreadyRegisteredHint = document.getElementById('loginHint');

	if (loginFormid.style.display !== 'none') {
		loginFormid.style.display = 'none';
		notAmemberHint.style.display = 'none';

		registerFormId.style.display = 'block';
		alreadyRegisteredHint.style.display = 'flex';

		loginFormButtonId.value = "Register";
	}
	else {
		loginFormid.style.display = 'block';
		notAmemberHint.style.display = 'flex';
		registerForm.style.display = 'none';
		alreadyRegisteredHint.style.display = 'none';
		loginFormButtonId.value = "Log in";
	}
	return false;
}

function registerCompany() {
	var loginFormId = document.getElementById("loginForm");
	var registerCompanyId = document.getElementById("registerCompanyForm");

	if (registerCompanyId.style.display === "none") {
		loginFormId.style.display = "none";
		registerCompanyId.style.display = "block";
	}
	else {
		loginFormId.style.display = "block";
		registerCompanyId.style.display = "none";
	}
	return false;
}

function postValidation() {
	var filenameId = document.getElementById('Filename');
	var firstSelect = document.getElementById('selectUser-1');
	var date = new Date(document.getElementById('Deadline').value);
	var fileId = document.getElementById('File')

	var errorFilename = document.getElementById('emptyFilename');
	var errorSelect = document.getElementById('emptySelect');
	var errorDeadline = document.getElementById('emptyDeadline');
	var emptyFileId = document.getElementById('emptyFile');

	errorFilename.style.display = 'none';
	errorSelect.style.display = 'none';
	errorDeadline.style.display = 'none';
	emptyFileId.style.display = 'none';

	if (filenameId.value === '') {
		errorFilename.style.display = 'block';
		return false;
	}
	if (firstSelect.value === 'Choose recipients') {
		errorSelect.style.display = 'block';
		return false;
	}
	if (isNaN(date)) {
		errorDeadline.style.display = 'block';
		return false;
	}
	if (fileId.files.length === 0) {
		emptyFileId.style.display = 'block';
		return false;
	}
	add_hidden_input();
	return true;
}

function add_hidden_input() {
    var rows = document.getElementsByClassName('ql-editor')[0].getElementsByTagName('p');
    var data = String();
    for (let i = 0; i < rows.length; i++) {
    	data += rows[i].innerHTML;
	}
	var descriptionId = document.getElementById('description');
    descriptionId.value = data;
}

function add_note() {
	var form = document.getElementById('add-note');
	var publishButtonId = document.getElementById('publishButton');

	if (form.style.display === 'none') {
		form.style.display = 'block';
		publishButtonId.value = 'Cancel';
	}
	else {
		form.style.display = 'none';
		publishButtonId.value = 'Publish';
	}
	return false;
}