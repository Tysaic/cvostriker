// Password site validation script
// /configuration/confirm_password/<option>

var passwordField = document.getElementById('password');
var confirmField = document.getElementById('confirm');
var new_passwordField = document.getElementById('new_password');
var _error = document.getElementById('password-error');
var special_chars = /[!_@#$%^&*(),.?":{}|<>]/;
var passwordForm = document.getElementById('password-form');
function ValidateForm(){

    if (passwordField.value.length <= 12){
        _error.textContent = "Password must be at least 12 characters long.";
        _error.style.color="red";
        return false;
    }
    if(!special_chars.test(passwordField.value) || !special_chars.test(new_passwordField.value)){
        _error.textContent = "Password must contain at least one special character.";
        _error.style.color="red";
        return false;
    }else if(passwordField.value !== confirmField.value){
        _error.textContent = "Passwords do not match."
        _error.style.color="red";
        return false;
    }else{
        _error.textContent =  "-";
        _error.style.color="";
        return true;
    }

}  
function togglePasswords(){
    if (passwordField.type == 'password'){
        passwordField.type = 'text';
        confirmField.type = 'text';
        new_passwordField.type='text';
    }else{
        passwordField.type = 'password';
        confirmField.type = 'password';
        new_passwordField.type='password';
    }
    
}
passwordField.addEventListener('keyup', ValidateForm);
confirmField.addEventListener('keyup', ValidateForm);
passwordForm.addEventListener('submit', function(event){
    if (!ValidateForm()){
        event.preventDefault();
        _error.textContent = "Please fix the errors before submitting.";
        _error.style.color = "red";
    }
})