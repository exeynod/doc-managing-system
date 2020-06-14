function formValidation()
{
var emailid = document.getElementById('registerEmail')
var passid = document.getElementById('registerInputPassword');
var repeatPassid = document.getElementById('repeatPassword');
var erremailid = document.getElementById('errorEmail');
var errpassid = document.getElementById('errorPass');
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