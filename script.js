
const loginTab = document.getElementById("loginTab");
const registerTab = document.getElementById("registerTab");
const loginForm = document.getElementById("loginForm");
const registerForm = document.getElementById("registerForm");
const message = document.getElementById("message");

const formTitle = document.getElementById("formTitle");
const formSubtitle = document.getElementById("formSubtitle");

function showMessage(text, type = "info") {
    message.textContent = text;
    message.className = type;
}

function switchTab(mode) {
    const isLogin = mode === "login";

    loginForm.classList.toggle("hidden", !isLogin);
    registerForm.classList.toggle("hidden", isLogin);

    loginTab.classList.toggle("active", isLogin);
    registerTab.classList.toggle("active", !isLogin);

    formTitle.textContent = isLogin ? "Welcome back" : "Create account";
    formSubtitle.textContent = isLogin
        ? "Sign in to continue to your account."
        : "Create your account to get started.";

    showMessage("");
}

loginTab.addEventListener("click", () => switchTab("login"));
registerTab.addEventListener("click", () => switchTab("register"));

async function sendRequest(endpoint, username, password, button) {
    button.disabled = true;
    button.textContent = "Please wait...";
    showMessage("Connecting securely...", "info");

    try {
        const response = await fetch(endpoint, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (!response.ok) {
            showMessage(data.message || "Something went wrong.", "error");
        } else {
            showMessage(data.message || "Success!", "success");

            if (endpoint === "/api/register") {
                registerForm.reset();
            }
        }
    } catch (error) {
        showMessage("Unable to connect to server. Please try again.", "error");
    } finally {
        button.disabled = false;

        if (endpoint === "/api/login") {
            button.innerHTML = 'Sign In <span>→</span>';
        } else {
            button.innerHTML = 'Create Account <span>→</span>';
        }
    }
}

loginForm.addEventListener("submit", (event) => {
    event.preventDefault();

    const username = document.getElementById("loginUsername").value.trim();
    const password = document.getElementById("loginPassword").value;
    const button = document.getElementById("loginButton");

    sendRequest("/api/login", username, password, button);
});

registerForm.addEventListener("submit", (event) => {
    event.preventDefault();

    const username = document.getElementById("registerUsername").value.trim();
    const password = document.getElementById("registerPassword").value;
    const button = document.getElementById("registerButton");

    sendRequest("/api/register", username, password, button);
});
