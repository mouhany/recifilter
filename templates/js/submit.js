// Submit
form.onsubmit = function(event){
    event.preventDefault();
    
    let myFormData = new FormData(form);
    let formDataObject = Object.fromEntries(myFormData.entries());

    formDataObject.dietLabels = myFormData.getAll('dietLabels');
    formDataObject.healthLabels = myFormData.getAll('healthLabels');
    formDataObject.cuisineType = myFormData.getAll('cuisineType');
    formDataObject.ingredients = myFormData.getAll('ingredients');
    

    myFormData.forEach(function(value) {
        if (value.trim() == "") { // If user add input field but not typed in anything
            formDataObject.ingredients.pop(value); // Do not include that field in the array
        }
    });

    console.log(formDataObject); // Object { ingredients: (2) […], dietLabels: (1) […], healthLabels: (2) […] }

    const myJSON = JSON.stringify(formDataObject);

    $.ajax({
        url: '/result',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(formDataObject),
        success: function(response){document.write(response);}
    });

    console.log(myJSON); // String { "ingredients": ["banana", "cheese"], "dietLabels": ["balanced"], "healthLabels": ["kidney-friendly", "low-sugar"] }

    }