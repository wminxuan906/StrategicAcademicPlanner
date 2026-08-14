console.log("Strategic Academic Planner loaded.");

document.querySelectorAll(".js-height-bar").forEach(function (bar) {
    bar.style.height = bar.dataset.height + "%";
});

document.querySelectorAll(".js-width-bar").forEach(function (bar) {
    bar.style.width = bar.dataset.width + "%";
});

// Reset expected marks in the What-if Calculator
const resetButton = document.getElementById("resetScenarioInputs");

if (resetButton) {
    resetButton.addEventListener("click", function () {
        const expectedMarkInputs =
            document.querySelectorAll('input[name^="expected_"]');

        expectedMarkInputs.forEach(function (input) {
            input.value = "";
        });
    });
}