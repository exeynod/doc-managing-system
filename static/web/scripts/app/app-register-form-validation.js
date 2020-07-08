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
	if (p1.value === p2.value && p1.value.toString().trim() !== '')
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
	var firstSelect = document.getElementById('select-1');
	var date = document.getElementById('Deadline');
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
	if (firstSelect.value === 'Выберите пользователя') {
		errorSelect.style.display = 'block';
		return false;
	}
	if (!moment(date.value, 'YYYY-MM-DD',true).isValid()) {
		errorDeadline.style.display = 'block';
		return false;
	}

	if (fileId.files.length === 0) {
		emptyFileId.style.display = 'block';
		return false;
	}

	var parts = fileId.files[0].name.split('.');
	var ext = 'undefined';
	if (parts.length > 1) ext = parts.pop();

	if (ext === 'pdf' || ext === 'docx') {
		emptyFileId.style.display = 'none';
	}
	else {
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

var select_counter = 1;

function more_recipients() {
	select_counter += 1;
	var select_name = "selectUser-" + select_counter.toString();
	var select_id = document.getElementById(select_name);
	var more_recipients_button_id = document.getElementById("more_recipients_button");
	if (select_id !== null)
		select_id.style.display = "flex";

	var next_recipient = select_counter + 1;
	if (document.getElementById("selectUser-" + next_recipient.toString()) === null)
		more_recipients_button_id.style.display = "none";
	return false;
}

function hideRecipient() {
	// Сделаем все опции видимыми
	var visible_counter = 1;
	while(true) {
		var s_name = "select-" + visible_counter.toString();
		var s_id = document.getElementById(s_name);
		if (s_id === null)
			break;
		var len = s_id.options.length;
		for (let i = 0; i < len; i++)
			s_id.options[i].style.display = 'block';
		visible_counter++;
	}
	// Удалим выбранные элементы
	var counter = 1;
	while(true) {
		var select_name = "select-" + counter.toString();
		var select_id = document.getElementById(select_name);
		if (select_id === null)
			break;
		counter++;
		if (select_id.value === 'Выберите пользователя')
			continue;
		var sel_index = select_id.selectedIndex;
		var other_counter = 1;
		while(true) {
			var sel_name = "select-" + other_counter.toString();
			var sel_id = document.getElementById(sel_name);
			if (sel_id === null)
				break;
			other_counter++;
			if (sel_id === select_id)
				continue;
			sel_id.options[sel_index].style.display = 'none';
		}
	}
	return false;
}

function less_users(num) {
	while(true) {
		var current_select = document.getElementById("select-" + num.toString());
		num++;
		var next_select = document.getElementById("select-" + num.toString());
		var next_li = document.getElementById("selectUser-" + num.toString());
		if (next_select === null) {
			num--;
			current_select.options.selectedIndex = 0;
			var select_li = document.getElementById("selectUser-" + num.toString());
			select_li.style.display = 'none';
			select_counter--;
			break;
		}
		else {
			if (next_li.style.display === 'none') {
			num--;
			current_select.options.selectedIndex = 0;
			var select_li = document.getElementById("selectUser-" + num.toString());
			select_li.style.display = 'none';
			select_counter--;
			break;
		}
		}
		current_select.options.selectedIndex = next_select.options.selectedIndex;
	}
	var more_recipients_button_id = document.getElementById("more_recipients_button");
	more_recipients_button_id.style.display = 'block';
	hideRecipient();
	return false;
}