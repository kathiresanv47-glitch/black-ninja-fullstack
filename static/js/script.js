// Food Quantity Increase / Decrease
function changeQty(id, change) {

    let quantity = document.getElementById(id);

    let current = parseInt(quantity.innerText) || 0;

    current = current + change;

    if (current < 0) {
        current = 0;
    }

    quantity.innerText = current;

    calculateTotal();
}


// Show / Hide QR Code
document.getElementById("payment").addEventListener("change", function () {

    if (this.value === "Online Payment") {
        document.getElementById("qrSection").style.display = "block";
    } else {
        document.getElementById("qrSection").style.display = "none";
    }

});


// Calculate Total
function calculateTotal() {

    let regular =
        parseInt(document.getElementById("regularQty").innerText) || 0;

    let king =
        parseInt(document.getElementById("kingQty").innerText) || 0;

    let maggi =
        parseInt(document.getElementById("maggieQty").innerText) || 0;


    let foodTotal =
        (regular * 100) +
        (king * 150) +
        (maggi * 50);

    let deliveryCharge = 20;

    let total = foodTotal + deliveryCharge;


    document.getElementById("foodTotal").innerText =
        "₹" + foodTotal;

    document.getElementById("deliveryCharge").innerText =
        "₹" + deliveryCharge;

    document.getElementById("grandTotal").innerText =
        "₹" + total;


    let totalItems =
        regular + king + maggi;

    document.getElementById("cartItems").innerText =
        totalItems;

    document.getElementById("cartTotal").innerText =
        "₹" + total;
}


// Place Order
document.getElementById("placeOrderBtn").addEventListener("click", async function (event) {

    // Stop normal form submission
    event.preventDefault();

    let name =
        document.getElementById("name").value.trim();

    let phone =
        document.getElementById("phone").value.trim();

    let address =
        document.getElementById("address").value.trim();

    let payment =
        document.getElementById("payment").value;


    let regular =
        parseInt(document.getElementById("regularQty").innerText) || 0;

    let king =
        parseInt(document.getElementById("kingQty").innerText) || 0;

    let maggi =
        parseInt(document.getElementById("maggieQty").innerText) || 0;


    // Customer validation
    if (name === "" || phone === "" || address === "") {

        alert("Please fill all customer details.");

        return;
    }


    // Food validation
    if (regular === 0 && king === 0 && maggi === 0) {

        alert("Please select at least one item.");

        return;
    }


    // Calculate total
    let foodTotal =
        (regular * 100) +
        (king * 150) +
        (maggi * 50);

    let deliveryCharge = 20;

    let total = foodTotal + deliveryCharge;


    // WhatsApp Message
    let message =
`BLACK NINJA SHAWARMA

Customer : ${name}

Phone : ${phone}

Address :
${address}

Regular Shawarma : ${regular}

King Plate : ${king}

Maggi Soup : ${maggi}

Food Total : ₹${foodTotal}

Delivery Charge : ₹${deliveryCharge}

Total : ₹${total}

Payment : ${payment}

Thank You`;


    // WhatsApp URL
    let whatsappUrl =
        "https://wa.me/919360796776?text=" +
        encodeURIComponent(message);


    try {

        // Save order in Flask
        let response = await fetch("/save_order", {

            method: "POST",

            headers: {
                "Content-Type":
                    "application/x-www-form-urlencoded"
            },

            body:
                "name=" +
                encodeURIComponent(name) +

                "&phone=" +
                encodeURIComponent(phone) +

                "&address=" +
                encodeURIComponent(address) +

                "&regular_qty=" +
                regular +

                "&king_qty=" +
                king +

                "&maggi_qty=" +
                maggi +

                "&total=" +
                total +

                "&payment=" +
                encodeURIComponent(payment)
        });


        // Check Flask response
        if (response.ok) {

    // Open WhatsApp
    window.open(whatsappUrl, "_blank");

    // Open automatic tracking page
    window.location.href = response.url;

}else {

            alert("Order could not be saved.");

        }

    } catch (error) {

        console.log(error);

        alert("Something went wrong while placing the order.");

    }

});


// Scroll to Order
function scrollToOrder() {

    document.getElementById("order").scrollIntoView({
        behavior: "smooth"
    });

}
function trackMyOrder() {

    let orderId = document.getElementById("trackOrderId").value.trim();

    if (orderId === "") {
        alert("Please enter your Order ID.");
        return;
    }

    window.location.href = "/track/" + orderId;
}