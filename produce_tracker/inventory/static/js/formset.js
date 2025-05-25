document.addEventListener('DOMContentLoaded', function() {
    const container = document.getElementById('formset-container');
    const addButton = document.getElementById('add-form');
    const totalForms = document.getElementById('id_form-TOTAL_FORMS');
    let formCount = parseInt(totalForms.value);

    addButton.addEventListener('click', function() {
        const newForm = container.querySelector('.formset-form').cloneNode(true);
        const formRegex = /form-(\d+)-/g;

        // Update all names/IDs
        newForm.innerHTML = newForm.innerHTML.replace(formRegex, `form-${formCount}-`);

        // Clear values
        newForm.querySelectorAll('input, select').forEach(input => {
            if (input.name && !input.name.includes('DELETE')) {
                input.value = '';
                if (input.checked) input.checked = false;
            }
        });

        container.appendChild(newForm);
        formCount++;
        totalForms.value = formCount;
    });
});