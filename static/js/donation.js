let frequency = "once";

function selectAmount(amount) {

    const input =
        document.getElementById("amountInput");

    input.value = amount;


    document
        .querySelectorAll(".amount-button")
        .forEach(button => {

            button.classList.remove("selected");

        });


    event.target.classList.add("selected");


    updateDonateButton();
}


function setFrequency(type) {

    frequency = type;


    const onceButton =
        document.getElementById("onceButton");

    const monthlyButton =
        document.getElementById("monthlyButton");


    onceButton.classList.remove("active");

    monthlyButton.classList.remove("active");


    if (type === "once") {

        onceButton.classList.add("active");

    } else {

        monthlyButton.classList.add("active");

    }


    updateDonateButton();
}



/* =========================
    update boutton
========================== */

function updateDonateButton() {

    const amount =
        document.getElementById("amountInput").value || 0;


    const button =
        document.getElementById("donateButton");


    if (frequency === "monthly") {

        button.textContent =
            "Support us monthly — " +
            amount +
            " DA";

    } else {

        button.textContent =
            "Support us — " +
            amount +
            " DA";
    }
}



/* =========================
    custom 
========================== */

document
    .getElementById("amountInput")
    .addEventListener(
        "input",
        updateDonateButton
    );



/* =========================
    donation
========================== */

function donate() {

    const amount =
        document.getElementById("amountInput").value;


    if (!amount || amount < 50) {

        alert(
            "Please enter an amount of at least 50 DA."
        );

        return;
    }


    document
        .getElementById("successMessage")
        .style.display = "block";



    console.log({
        amount: amount,
        currency: "DZD",
        frequency: frequency
    });
}