// Dynamic text field
let form = document.forms[0];
let ingredientsWrapper = document.getElementById('ingredientsWrapper');

// Add
function addField(element) {
  if (element.previousElementSibling.value.trim() === '') {
    return false;
  }

  let div = document.createElement('div');
  div.setAttribute(
    'class',
    'px-lg-5 px-sm-0 field d-flex flex-row gap-2 gap-md-3'
  );

  let input = document.createElement('input');
  input.setAttribute('type', 'text');
  input.setAttribute('class', 'form-control form-control-sm');
  input.setAttribute('name', 'ingredients');
  input.setAttribute('id', 'ingredients');
  input.setAttribute('placeholder', 'Enter query or ingredient');

  let plus = document.createElement('span');
  plus.setAttribute('onclick', 'addField(this)');
  plus.setAttribute('class', 'btn px-3 btn-primary');
  let plusText = document.createTextNode('+');
  plus.appendChild(plusText);

  let minus = document.createElement('span');
  minus.setAttribute('onclick', 'removeField(this)');
  minus.setAttribute('class', 'btn px-3 btn-primary');
  let minusText = document.createTextNode('−');
  minus.appendChild(minusText);

  ingredientsWrapper.insertBefore(div, ingredientsWrapper.lastChild);
  div.appendChild(input).focus();
  div.appendChild(plus);
  div.appendChild(minus);

  element.nextElementSibling.style.display = 'block';

  element.style.display = 'none';
}

// Remove
function removeField(element) {
  element.parentElement.remove();
}
