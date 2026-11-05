document.addEventListener("DOMContentLoaded", function () {
    const addButton = document.getElementById("add-variant");
    const rowsContainer = document.getElementById("variant-rows");
    const emptyFormTemplate = document.getElementById("empty-form-template");
    const totalFormsInput = document.querySelector("[name='variants-TOTAL_FORMS']");

    addButton.addEventListener("click", function () {
        const formIndex = parseInt(totalFormsInput.value, 10);

        const newRowHtml = emptyFormTemplate.innerHTML.replace(/__prefix__/g, formIndex);

        const wrapper = document.createElement("div");
        wrapper.innerHTML = newRowHtml;
        rowsContainer.appendChild(wrapper.firstElementChild);

        totalFormsInput.value = formIndex + 1;
    });
});