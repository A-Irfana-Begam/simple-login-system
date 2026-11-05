
const loginTab = document.getElementById("loginTab");
const registerTab = document.getElementById("registerTab");
const loginForm = document.getElementById("loginForm");
const registerForm = document.getElementById("registerForm");
const message = document.getElementById("message");

const registerPassword = document.getElementById("registerPassword");
const registerButton = document.getElementById("registerButton");
const strengthBar = document.getElementById("strengthBar");
const strengthLabel = document.getElementById("strengthLabel");

function showMessage(text, type = "") {
    message.textContent = text;
    message.className = type;
}

function switchTab(mode) {
    const isLogin = mode === "login";

    loginForm.classList.toggle("hidden", !isLogin);
    registerForm.classList.toggle("hidden", isLogin);

    loginTab.classList.toggle("active", isLogin);
    registerTab.classList.toggle("active", !isLogin);

    document.getElementById("formTitle").textContent =
        isLogin ? "Welcome back" : "Create account";

    document.getElementById("formSubtitle").textContent =
        isLogin
            ? "Sign in securely to continue."
            : "Choose a strong password to protect your account.";

    showMessage("");
}

loginTab.addEventListener("click", () => switchTab("login"));
registerTab.addEventListener("click", () => switchTab("register"));

function checkPassword(password) {
    const sequencePattern =
        /12345|23456|34567|45678|56789|98765|87654|76543|65432|54321|qwerty|asdfgh|zxcvbn|password/i;

    const repeatedPattern = /(.)\1{3,}/;

    return {
        length: password.length >= 10,
        upper: /[A-Z]/.test(password),
        lower: /[a-z]/.test(password),
        number: /[0-9]/.test(password),
        special: /[^A-Za-z0-9]/.test(password),
        sequence: password.length > 0 &&
            !sequencePattern.test(password) &&
            !repeatedPattern.test(password)
    };
}

function updatePasswordStrength() {
    const password = registerPassword.value;
    const rules = checkPassword(password);
    const passed = Object.values(rules).filter(Boolean).length;

    document.querySelectorAll("#passwordRules li").forEach(item => {
        item.classList.toggle("valid", rules[item.dataset.rule]);
    });

    const percentage = (passed / 6) * 100;
    strengthBar.style.width = percentage + "%";

    if (!password) {
        strengthLabel.textContent = "Password strength: Not entered";
        strengthBar.style.background = "#c66d75";
    } else if (passed <= 3) {
        strengthLabel.textContent = "Password strength: Weak";
        strengthBar.style.background = "#c66d75";
    } else if (passed < 6) {
        strengthLabel.textContent = "Password strength: Medium";
        strengthBar.style.background = "#d19b54";
    } else {
        strengthLabel.textContent = "Password strength: Strong";
        strengthBar.style.background = "#368366";
    }

    registerButton.disabled = passed !== 6;
    return passed === 6;
}

registerPassword.addEventListener("input", updatePasswordStrength);

document.getElementById("togglePassword").addEventListener("click", () => {
    const isHidden = registerPassword.type === "password";
    registerPassword.type = isHidden ? "text" : "password";
    document.getElementById("togglePassword").textContent =
        isHidden ? "Hide" : "Show";
});

function secureRandomIndex(max) {
    const values = new Uint32Array(1);
    crypto.getRandomValues(values);
    return values[0] % max;
}

function generateStrongPassword() {
    const upper = "ABCDEFGHJKLMNPQRSTUVWXYZ";
    const lower = "abcdefghijkmnopqrstuvwxyz";
    const numbers = "23456789";
    const symbols = "!@#$%&*?";
    const all = upper + lower + numbers + symbols;

    let password = [
        upper[secureRandomIndex(upper.length)],
        lower[secureRandomIndex(lower.length)],
        numbers[secureRandomIndex(numbers.length)],
        symbols[secureRandomIndex(symbols.length)]
    ];

    while (password.length < 14) {
        password.push(all[secureRandomIndex(all.length)]);
    }

    for (let i = password.length - 1; i > 0; i--) {
        const j = secureRandomIndex(i + 1);
        [password[i], password[j]] = [password[j], password[i]];
    }

    return password.join("");
}

document.getElementById("suggestPassword").addEventListener("click", () => {
    registerPassword.value = generateStrongPassword();
    registerPassword.type = "text";
    document.getElementById("togglePassword").textContent = "Hide";
    updatePasswordStrength();
    showMessage("Strong password suggested. Save it somewhere safe.", "success");
});

async function sendRequest(endpoint, username, password, button) {
    button.disabled = true;
    button.textContent = "Please wait...";
    showMessage("Connecting securely...", "info");

    try {
        const response = await fetch(endpoint, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (!response.ok) {
            showMessage(data.message || "Something went wrong.", "error");
            return;
        }

        if (endpoint === "/api/login") {
            window.location.href = "success.html";
            return;
        }

        showMessage(data.message || "Account created successfully!", "success");
        registerForm.reset();
        updatePasswordStrength();

    } catch (error) {
        showMessage("Unable to connect to server. Please try again.", "error");
    } finally {
        button.disabled = false;

        if (endpoint === "/api/login") {
            button.innerHTML = 'Sign In <span>→</span>';
        } else {
            button.innerHTML = 'Create Account <span>→</span>';
        }

        if (endpoint === "/api/register") {
            updatePasswordStrength();
        }
    }
}

loginForm.addEventListener("submit", event => {
    event.preventDefault();

    const username = document.getElementById("loginUsername").value.trim();
    const password = document.getElementById("loginPassword").value;

    sendRequest(
        "/api/login",
        username,
        password,
        document.getElementById("loginButton")
    );
});

registerForm.addEventListener("submit", event => {
    event.preventDefault();

    const username = document.getElementById("registerUsername").value.trim();
    const password = registerPassword.value;

    if (!updatePasswordStrength()) {
        showMessage(
            "Weak password! Follow all the password suggestions.",
            "error"
        );
        return;
    }

    sendRequest("/api/register", username, password, registerButton);
});

updatePasswordStrength();
