/* =====================================================
   SMART CAR SERVICE
   FRONTEND JAVASCRIPT
===================================================== */


/* =====================================================
   API CONFIGURATION
===================================================== */

const API_BASE_URL = "http://127.0.0.1:8000/api";


/* =====================================================
   GLOBAL VARIABLES
===================================================== */

let accessToken = localStorage.getItem("accessToken");
let currentUser = null;

let vehicles = [];
let selectedVehicle = null;

let conversationHistory = [];

let pendingAIAction = null;


/* =====================================================
   DOM READY
===================================================== */

document.addEventListener("DOMContentLoaded", () => {

    initializeApp();

});


/* =====================================================
   INITIALIZE
===================================================== */

async function initializeApp() {

    setupNavigation();
    setupAuthentication();
    setupVehicleEvents();
    setupAssistant();
    setupTheme();
    setupLogout();

    if (accessToken) {

        const valid = await loadCurrentUser();

        if (valid) {

            showApp();

            await loadVehicles();

            checkBackendStatus();

        } else {

            showLoginScreen();

        }

    } else {

        showLoginScreen();

    }

}


/* =====================================================
   AUTHENTICATION
===================================================== */

function setupAuthentication() {

    const loginForm =
        document.getElementById("loginForm");

    const registerForm =
        document.getElementById("registerForm");

    const showRegisterBtn =
        document.getElementById("showRegisterBtn");

    const showLoginBtn =
        document.getElementById("showLoginBtn");


    if (showRegisterBtn) {

        showRegisterBtn.addEventListener(
            "click",
            () => showAuthTab("register")
        );

    }


    if (showLoginBtn) {

        showLoginBtn.addEventListener(
            "click",
            () => showAuthTab("login")
        );

    }


    if (loginForm) {

        loginForm.addEventListener(
            "submit",
            handleLogin
        );

    }


    if (registerForm) {

        registerForm.addEventListener(
            "submit",
            handleRegister
        );

    }

}


/* =====================================================
   SWITCH LOGIN / REGISTER
===================================================== */

function showAuthTab(tab) {

    const loginBox =
        document.getElementById("loginBox");

    const registerBox =
        document.getElementById("registerBox");


    if (tab === "register") {

        loginBox.classList.add("hidden");
        registerBox.classList.remove("hidden");

    } else {

        registerBox.classList.add("hidden");
        loginBox.classList.remove("hidden");

    }

}


/* =====================================================
   LOGIN
===================================================== */

async function handleLogin(event) {

    event.preventDefault();

    const username =
        document.getElementById("loginUsername").value.trim();

    const password =
        document.getElementById("loginPassword").value;


    if (!username || !password) {

        showToast(
            "Please enter username and password.",
            "error"
        );

        return;
    }


    try {

        showToast("Logging in...", "success");


        const response = await fetch(
            `${API_BASE_URL}/auth/login/`,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    username,
                    password
                })
            }
        );


        const data = await response.json();


        if (!response.ok) {

            throw new Error(
                getAPIError(data, "Login failed.")
            );

        }


        accessToken =
            data.access ||
            data.access_token ||
            data.token;


        if (!accessToken) {

            throw new Error(
                "Login succeeded but no access token was returned."
            );

        }


        localStorage.setItem(
            "accessToken",
            accessToken
        );


        if (data.refresh) {

            localStorage.setItem(
                "refreshToken",
                data.refresh
            );

        }


        await loadCurrentUser();

        showApp();

        await loadVehicles();

        checkBackendStatus();

        showToast(
            "Login successful!",
            "success"
        );


    } catch (error) {

        console.error(error);

        showToast(
            error.message,
            "error"
        );

    }

}


/* =====================================================
   REGISTER
===================================================== */

async function handleRegister(event) {

    event.preventDefault();


    const firstName =
        document.getElementById("registerFirstName").value.trim();

    const lastName =
        document.getElementById("registerLastName").value.trim();

    const username =
        document.getElementById("registerUsername").value.trim();

    const email =
        document.getElementById("registerEmail").value.trim();

    const password =
        document.getElementById("registerPassword").value;

    const password2 =
        document.getElementById("registerPassword2").value;


    if (password !== password2) {

        showToast(
            "Passwords do not match.",
            "error"
        );

        return;
    }


    try {

        const response = await fetch(
            `${API_BASE_URL}/auth/register/`,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    first_name: firstName,
                    last_name: lastName,
                    username,
                    email,
                    password,
                    password2
                })
            }
        );


        const data = await response.json();


        if (!response.ok) {

            throw new Error(
                getAPIError(
                    data,
                    "Registration failed."
                )
            );

        }


        showToast(
            "Account created successfully!",
            "success"
        );


        showAuthTab("login");


        document.getElementById(
            "loginUsername"
        ).value = username;


    } catch (error) {

        console.error(error);

        showToast(
            error.message,
            "error"
        );

    }

}


/* =====================================================
   CURRENT USER
===================================================== */

async function loadCurrentUser() {

    try {

        const data = await apiRequest(
            "/auth/me/"
        );

        currentUser = data;

        updateUserAvatar();

        return true;

    } catch (error) {

        console.error(error);

        logout(false);

        return false;

    }

}


/* =====================================================
   USER AVATAR
===================================================== */

function updateUserAvatar() {

    const avatar =
        document.getElementById("userAvatar");

    if (!avatar) return;


    let letter = "U";


    if (currentUser) {

        const name =
            currentUser.first_name ||
            currentUser.username ||
            "U";

        letter =
            name.charAt(0).toUpperCase();

    }


    avatar.textContent = letter;

}


/* =====================================================
   SHOW APP
===================================================== */

function showApp() {

    document
        .getElementById("authArea")
        .classList.add("hidden");

    document
        .getElementById("appArea")
        .classList.remove("hidden");

}


/* =====================================================
   SHOW LOGIN
===================================================== */

function showLoginScreen() {

    document
        .getElementById("appArea")
        .classList.add("hidden");

    document
        .getElementById("authArea")
        .classList.remove("hidden");

}


/* =====================================================
   LOGOUT
===================================================== */

function setupLogout() {

    const button =
        document.getElementById("logoutBtn");

    if (button) {

        button.addEventListener(
            "click",
            () => logout(true)
        );

    }

}


function logout(showMessage = true) {

    localStorage.removeItem("accessToken");
    localStorage.removeItem("refreshToken");

    accessToken = null;
    currentUser = null;

    vehicles = [];
    selectedVehicle = null;

    conversationHistory = [];

    showLoginScreen();


    if (showMessage) {

        showToast(
            "Logged out successfully.",
            "success"
        );

    }

}


/* =====================================================
   API REQUEST
===================================================== */

async function apiRequest(
    endpoint,
    options = {}
) {

    const headers = {
        "Content-Type": "application/json",
        ...(options.headers || {})
    };


    if (accessToken) {

        headers.Authorization =
            `Bearer ${accessToken}`;

    }


    const response = await fetch(
        `${API_BASE_URL}${endpoint}`,
        {
            ...options,
            headers
        }
    );


    if (response.status === 204) {
        return null;
    }


    const data =
        await response.json().catch(
            () => ({})
        );


    if (!response.ok) {

        if (response.status === 401) {

            logout(false);

        }

        throw new Error(
            getAPIError(
                data,
                `Request failed (${response.status})`
            )
        );

    }


    return data;

}


/* =====================================================
   API ERROR
===================================================== */

function getAPIError(
    data,
    fallback
) {

    if (!data) return fallback;


    if (typeof data.detail === "string") {
        return data.detail;
    }


    if (typeof data.message === "string") {
        return data.message;
    }


    const errors = [];


    Object.keys(data).forEach(key => {

        const value = data[key];

        if (Array.isArray(value)) {

            errors.push(
                `${key}: ${value.join(", ")}`
            );

        } else if (typeof value === "string") {

            errors.push(
                `${key}: ${value}`
            );

        }

    });


    return errors.length
        ? errors.join(" | ")
        : fallback;

}


/* =====================================================
   NAVIGATION
===================================================== */

function setupNavigation() {

    document
        .querySelectorAll(".nav-btn")
        .forEach(button => {

            button.addEventListener(
                "click",
                () => {

                    const page =
                        button.dataset.page;

                    showPage(page);

                }
            );

        });

}


/* =====================================================
   SHOW PAGE
===================================================== */

function showPage(pageName) {

    document
        .querySelectorAll(".page")
        .forEach(page => {

            page.classList.remove("active");

        });


    document
        .querySelectorAll(".nav-btn")
        .forEach(button => {

            button.classList.remove("active");

        });


    const page =
        document.getElementById(
            `page-${pageName}`
        );


    if (page) {

        page.classList.add("active");

    }


    const button =
        document.querySelector(
            `.nav-btn[data-page="${pageName}"]`
        );


    if (button) {

        button.classList.add("active");

    }


    const titles = {

        dashboard: "Dashboard",
        cars: "My Cars",
        details: "Car Details",
        maintenance: "Maintenance",
        appointments: "Appointments",
        services: "Services",
        assistant: "AI Assistant"

    };


    const pageTitle =
        document.getElementById("pageTitle");


    if (pageTitle) {

        pageTitle.textContent =
            titles[pageName] || "Smart Car Service";

    }


    if (pageName === "details") {

        renderSelectedVehicle();

    }

}


/* =====================================================
   OPEN PAGE
===================================================== */

function openPage(pageName) {

    showPage(pageName);

}


/* =====================================================
   VEHICLE EVENTS
===================================================== */

function setupVehicleEvents() {

    const addButton =
        document.getElementById("addVehicleBtn");

    const form =
        document.getElementById("vehicleForm");

    const closeButton =
        document.getElementById("closeVehicleModal");

    const cancelButton =
        document.getElementById("cancelVehicleBtn");


    if (addButton) {

        addButton.addEventListener(
            "click",
            () => openVehicleModal()
        );

    }


    if (form) {

        form.addEventListener(
            "submit",
            saveVehicle
        );

    }


    if (closeButton) {

        closeButton.addEventListener(
            "click",
            closeVehicleModal
        );

    }


    if (cancelButton) {

        cancelButton.addEventListener(
            "click",
            closeVehicleModal
        );

    }


    const modal =
        document.getElementById("vehicleModal");


    if (modal) {

        modal.addEventListener(
            "click",
            event => {

                if (event.target === modal) {

                    closeVehicleModal();

                }

            }
        );

    }

}


/* =====================================================
   LOAD VEHICLES
===================================================== */

async function loadVehicles() {

    try {

        const data =
            await apiRequest("/vehicles/");


        if (Array.isArray(data)) {

            vehicles = data;

        } else if (Array.isArray(data.results)) {

            vehicles = data.results;

        } else {

            vehicles = [];

        }


        renderVehicles();

        updateDashboard();


    } catch (error) {

        console.error(
            "Loading vehicles failed:",
            error
        );

        vehicles = [];

        renderVehicles();

        updateDashboard();

    }

}


/* =====================================================
   RENDER VEHICLES
===================================================== */

function renderVehicles() {

    const carsList =
        document.getElementById("carsList");

    const dashboardVehicles =
        document.getElementById(
            "dashboardVehicles"
        );


    if (vehicles.length === 0) {

        const emptyHTML = `
            <div class="empty-state">
                <span>🚗</span>
                <h3>No vehicles found</h3>
                <p>Add your first vehicle to get started.</p>
            </div>
        `;


        if (carsList) {
            carsList.innerHTML = emptyHTML;
        }


        if (dashboardVehicles) {
            dashboardVehicles.innerHTML = emptyHTML;
        }


        return;

    }


    if (carsList) {

        carsList.innerHTML =
            vehicles
                .map(vehicleCardHTML)
                .join("");

    }


    if (dashboardVehicles) {

        dashboardVehicles.innerHTML =
            vehicles
                .slice(0, 3)
                .map(vehicleListHTML)
                .join("");

    }

}


/* =====================================================
   VEHICLE CARD
===================================================== */

function vehicleCardHTML(vehicle) {

    const id =
        vehicle.id ||
        vehicle.pk;


    const make =
        vehicle.make || "Unknown";

    const model =
        vehicle.model || "Vehicle";

    const year =
        vehicle.year || "N/A";

    const plate =
        vehicle.plate_number ||
        vehicle.plate ||
        "N/A";


    return `

        <div class="vehicle-card">

            <div class="vehicle-top">

                <div>
                    <div class="vehicle-icon">
                        🚗
                    </div>
                </div>

            </div>

            <h3>
                ${escapeHTML(make)}
                ${escapeHTML(model)}
            </h3>

            <p>
                Your registered vehicle
            </p>

            <div class="vehicle-meta">

                <div>
                    <span>Year</span>
                    <strong>
                        ${escapeHTML(String(year))}
                    </strong>
                </div>

                <div>
                    <span>Plate</span>
                    <strong>
                        ${escapeHTML(String(plate))}
                    </strong>
                </div>

            </div>

            <div class="vehicle-actions">

                <button
                    class="edit-btn"
                    onclick="editVehicle(${id})"
                >
                    Edit
                </button>

                <button
                    class="secondary-btn"
                    onclick="viewVehicle(${id})"
                >
                    Details
                </button>

                <button
                    class="danger-btn"
                    onclick="deleteVehicle(${id})"
                >
                    Delete
                </button>

            </div>

        </div>

    `;

}


/* =====================================================
   VEHICLE LIST
===================================================== */

function vehicleListHTML(vehicle) {

    const id =
        vehicle.id ||
        vehicle.pk;

    const make =
        vehicle.make || "Unknown";

    const model =
        vehicle.model || "Vehicle";

    const year =
        vehicle.year || "N/A";


    return `

        <div class="vehicle-item">

            <div class="vehicle-info">

                <div class="vehicle-info-icon">
                    🚗
                </div>

                <div>

                    <h3>
                        ${escapeHTML(make)}
                        ${escapeHTML(model)}
                    </h3>

                    <p>
                        ${escapeHTML(String(year))}
                    </p>

                </div>

            </div>

            <button
                class="small-btn"
                onclick="viewVehicle(${id})"
            >
                View
            </button>

        </div>

    `;

}


/* =====================================================
   DASHBOARD
===================================================== */

function updateDashboard() {

    const count =
        document.getElementById(
            "vehicleCount"
        );


    if (count) {

        count.textContent =
            vehicles.length;

    }

}


/* =====================================================
   OPEN ADD VEHICLE MODAL
===================================================== */

function openVehicleModal(vehicle = null) {

    const modal =
        document.getElementById(
            "vehicleModal"
        );


    const title =
        document.getElementById(
            "vehicleModalTitle"
        );


    const id =
        document.getElementById(
            "vehicleId"
        );


    const make =
        document.getElementById(
            "vehicleMake"
        );


    const model =
        document.getElementById(
            "vehicleModel"
        );


    const year =
        document.getElementById(
            "vehicleYear"
        );


    const plate =
        document.getElementById(
            "vehiclePlate"
        );


    if (vehicle) {

        title.textContent =
            "Edit Vehicle";

        id.value =
            vehicle.id || vehicle.pk || "";

        make.value =
            vehicle.make || "";

        model.value =
            vehicle.model || "";

        year.value =
            vehicle.year || "";

        plate.value =
            vehicle.plate_number ||
            vehicle.plate ||
            "";

    } else {

        title.textContent =
            "Add Vehicle";

        id.value = "";

        make.value = "";
        model.value = "";
        year.value = "";
        plate.value = "";

    }


    modal.classList.remove("hidden");

}


/* =====================================================
   CLOSE VEHICLE MODAL
===================================================== */

function closeVehicleModal() {

    document
        .getElementById("vehicleModal")
        .classList.add("hidden");

}


/* =====================================================
   SAVE VEHICLE
===================================================== */

async function saveVehicle(event) {

    event.preventDefault();


    const id =
        document.getElementById(
            "vehicleId"
        ).value;


    const data = {

        make:
            document.getElementById(
                "vehicleMake"
            ).value.trim(),

        model:
            document.getElementById(
                "vehicleModel"
            ).value.trim(),

        year:
            Number(
                document.getElementById(
                    "vehicleYear"
                ).value
            ),

        license_plate:
            document.getElementById(
                "vehiclePlate"
            ).value.trim()

    };


    try {

        if (id) {

            await apiRequest(
                `/vehicles/${id}/`,
                {
                    method: "PUT",
                    body: JSON.stringify(data)
                }
            );

            showToast(
                "Vehicle updated successfully.",
                "success"
            );

        } else {

            await apiRequest(
                "/vehicles/",
                {
                    method: "POST",
                    body: JSON.stringify(data)
                }
            );

            showToast(
                "Vehicle added successfully.",
                "success"
            );

        }


        closeVehicleModal();

        await loadVehicles();


    } catch (error) {

        console.error(error);

        showToast(
            error.message,
            "error"
        );

    }

}


/* =====================================================
   EDIT VEHICLE
===================================================== */

function editVehicle(id) {

    const vehicle =
        findVehicle(id);


    if (!vehicle) {

        showToast(
            "Vehicle not found.",
            "error"
        );

        return;

    }


    openVehicleModal(vehicle);

}


/* =====================================================
   VIEW VEHICLE
===================================================== */

function viewVehicle(id) {

    selectedVehicle =
        findVehicle(id);


    if (!selectedVehicle) {

        showToast(
            "Vehicle not found.",
            "error"
        );

        return;

    }


    renderSelectedVehicle();

    showPage("details");

}


/* =====================================================
   FIND VEHICLE
===================================================== */

function findVehicle(id) {

    return vehicles.find(
        vehicle =>
            String(vehicle.id || vehicle.pk)
            === String(id)
    );

}


/* =====================================================
   DELETE VEHICLE
===================================================== */

async function deleteVehicle(id) {

    const vehicle =
        findVehicle(id);


    if (!vehicle) return;


    const confirmed =
        confirm(
            `Delete ${vehicle.make || ""} ${vehicle.model || ""}?`
        );


    if (!confirmed) return;


    try {

        await apiRequest(
            `/vehicles/${id}/`,
            {
                method: "DELETE"
            }
        );


        if (
            selectedVehicle &&
            String(
                selectedVehicle.id ||
                selectedVehicle.pk
            ) === String(id)
        ) {

            selectedVehicle = null;

        }


        showToast(
            "Vehicle deleted successfully.",
            "success"
        );


        await loadVehicles();


    } catch (error) {

        console.error(error);

        showToast(
            error.message,
            "error"
        );

    }

}


/* =====================================================
   RENDER SELECTED VEHICLE
===================================================== */

function renderSelectedVehicle() {

    const container =
        document.getElementById(
            "carDetailsContent"
        );


    if (!container) return;


    if (!selectedVehicle) {

        container.innerHTML = `

            <div class="empty-state">

                <span>📋</span>

                <h3>No car selected</h3>

                <p>
                    Select a vehicle from My Cars.
                </p>

            </div>

        `;

        return;

    }


    const make =
        selectedVehicle.make || "Unknown";

    const model =
        selectedVehicle.model || "Vehicle";

    const year =
        selectedVehicle.year || "N/A";

    const plate =
        selectedVehicle.plate_number ||
        selectedVehicle.plate ||
        "N/A";


    container.innerHTML = `

        <div class="details-card">

            <div class="details-header">

                <div class="details-icon">
                    🚗
                </div>

                <div>

                    <h2>
                        ${escapeHTML(make)}
                        ${escapeHTML(model)}
                    </h2>

                    <p>
                        Vehicle information
                    </p>

                </div>

            </div>


            <div class="details-grid">

                <div class="detail-item">

                    <span>Make</span>

                    <strong>
                        ${escapeHTML(make)}
                    </strong>

                </div>


                <div class="detail-item">

                    <span>Model</span>

                    <strong>
                        ${escapeHTML(model)}
                    </strong>

                </div>


                <div class="detail-item">

                    <span>Year</span>

                    <strong>
                        ${escapeHTML(String(year))}
                    </strong>

                </div>


                <div class="detail-item">

                    <span>Plate Number</span>

                    <strong>
                        ${escapeHTML(String(plate))}
                    </strong>

                </div>

            </div>

        </div>

    `;

}


/* =====================================================
   AI ASSISTANT
===================================================== */

function setupAssistant() {

    const sendButton =
        document.getElementById(
            "sendChatBtn"
        );


    const input =
        document.getElementById(
            "chatInput"
        );


    const confirmButton =
        document.getElementById(
            "confirmAIAction"
        );


    const cancelButton =
        document.getElementById(
            "hideConfirmationButton"
        );


    if (sendButton) {

        sendButton.addEventListener(
            "click",
            sendAIMessage
        );

    }


    if (input) {

        input.addEventListener(
            "keydown",
            event => {

                if (
                    event.key === "Enter" &&
                    !event.shiftKey
                ) {

                    event.preventDefault();

                    sendAIMessage();

                }

            }
        );

    }


    if (confirmButton) {

        confirmButton.addEventListener(
            "click",
            confirmAIAction
        );

    }


    if (cancelButton) {

        cancelButton.addEventListener(
            "click",
            hideConfirmation
        );

    }

}


/* =====================================================
   SEND QUICK PROMPT
===================================================== */

function sendAIQuickPrompt(text) {

    const input =
        document.getElementById(
            "chatInput"
        );


    showPage("assistant");


    input.value = text;

    sendAIMessage();

}


/* =====================================================
   SEND AI MESSAGE
===================================================== */

async function sendAIMessage() {

    const input =
        document.getElementById(
            "chatInput"
        );


    const text =
        input.value.trim();


    if (!text) return;


    addUserMessage(text);

    input.value = "";


    conversationHistory.push({

        role: "user",
        content: text

    });


    const typing =
        showTypingIndicator();


    try {

        const response =
            await apiRequest(
                "/assistant/chat/",
                {
                    method: "POST",

                    body: JSON.stringify({

                        message: text,

                        conversation:
                            conversationHistory,

                        confirm: false

                    })

                }
            );


        removeTypingIndicator(typing);


        const answer =
            response.response ||
            response.message ||
            response.reply ||
            "I couldn't generate a response.";


        addAIMessage(answer);


        conversationHistory.push({

            role: "assistant",

            content: answer

        });


        if (
            response.requires_confirmation
        ) {

            pendingAIAction =
                response.pending_action ||
                response.action ||
                null;


            showConfirmation(
                response.confirmation_message ||
                "The AI wants to perform an action. Do you want to continue?"
            );

        }


    } catch (error) {

        removeTypingIndicator(typing);


        console.error(
            "AI request failed:",
            error
        );


        addAIMessage(
            "Sorry, I couldn't connect to the AI assistant. Please make sure the backend is running."
        );


        showToast(
            error.message,
            "error"
        );

    }

}


/* =====================================================
   CONFIRM AI ACTION
===================================================== */

async function confirmAIAction() {

    const typing =
        showTypingIndicator();


    try {

        const response =
            await apiRequest(
                "/assistant/chat/",
                {
                    method: "POST",

                    body: JSON.stringify({

                        conversation:
                            conversationHistory,

                        confirm: true,

                        pending_action:
                            pendingAIAction

                    })

                }
            );


        removeTypingIndicator(typing);


        const answer =
            response.response ||
            response.message ||
            response.reply ||
            "Action completed.";


        addAIMessage(answer);


        conversationHistory.push({

            role: "assistant",

            content: answer

        });


        hideConfirmation();

        pendingAIAction = null;


        await loadVehicles();


    } catch (error) {

        removeTypingIndicator(typing);


        console.error(error);


        addAIMessage(
            "I couldn't complete the requested action."
        );


        showToast(
            error.message,
            "error"
        );

    }

}


/* =====================================================
   SHOW CONFIRMATION
===================================================== */

function showConfirmation(text) {

    const container =
        document.getElementById(
            "confirmationContainer"
        );


    const message =
        document.getElementById(
            "confirmationText"
        );


    message.textContent = text;

    container.classList.remove("hidden");

}


/* =====================================================
   HIDE CONFIRMATION
===================================================== */

function hideConfirmation() {

    const container =
        document.getElementById(
            "confirmationContainer"
        );


    container.classList.add("hidden");

    pendingAIAction = null;

}


/* =====================================================
   ADD USER MESSAGE
===================================================== */

function addUserMessage(text) {

    addMessage(
        text,
        "user"
    );

}


/* =====================================================
   ADD AI MESSAGE
===================================================== */

function addAIMessage(text) {

    addMessage(
        text,
        "ai"
    );

}


/* =====================================================
   ADD MESSAGE
===================================================== */

function addMessage(
    text,
    type
) {

    const container =
        document.getElementById(
            "chatMessages"
        );


    const message =
        document.createElement("div");


    message.className =
        `message ${type}`;


    const avatar =
        document.createElement("div");


    avatar.className =
        "message-avatar";


    avatar.textContent =
        type === "ai"
            ? "🤖"
            : "👤";


    const content =
        document.createElement("div");


    content.className =
        "message-content";


    content.innerHTML =
        formatAIText(text);


    message.appendChild(avatar);

    message.appendChild(content);


    container.appendChild(message);


    container.scrollTop =
        container.scrollHeight;

}


/* =====================================================
   TYPING INDICATOR
===================================================== */

function showTypingIndicator() {

    const container =
        document.getElementById(
            "chatMessages"
        );


    const message =
        document.createElement("div");


    message.className =
        "message ai";

    message.id =
        "typingIndicator";


    message.innerHTML = `

        <div class="message-avatar">
            🤖
        </div>

        <div class="message-content">

            <div class="typing">

                <span></span>
                <span></span>
                <span></span>

            </div>

        </div>

    `;


    container.appendChild(message);


    container.scrollTop =
        container.scrollHeight;


    return message;

}


/* =====================================================
   REMOVE TYPING
===================================================== */

function removeTypingIndicator(element) {

    if (element) {

        element.remove();

    }

}


/* =====================================================
   MAINTENANCE
===================================================== */

function askMaintenance() {

    showPage("assistant");

    sendAIQuickPrompt(
        "What maintenance does my car need?"
    );

}


/* =====================================================
   APPOINTMENTS
===================================================== */

function askAppointments() {

    showPage("assistant");

    sendAIQuickPrompt(
        "Help me with my car service appointment."
    );

}


/* =====================================================
   SERVICES
===================================================== */

function askServices() {

    showPage("assistant");

    sendAIQuickPrompt(
        "What car services are available?"
    );

}


/* =====================================================
   THEME
===================================================== */

function setupTheme() {

    const button =
        document.getElementById(
            "themeBtn"
        );


    const savedTheme =
        localStorage.getItem(
            "theme"
        );


    if (savedTheme === "dark") {

        document.body.classList.add("dark");

    }


    if (button) {

        button.addEventListener(
            "click",
            toggleTheme
        );

    }

}


function toggleTheme() {

    document.body.classList.toggle(
        "dark"
    );


    const dark =
        document.body.classList.contains(
            "dark"
        );


    localStorage.setItem(
        "theme",
        dark ? "dark" : "light"
    );

}


/* =====================================================
   BACKEND STATUS
===================================================== */

async function checkBackendStatus() {

    const dot =
        document.getElementById(
            "statusDot"
        );


    const text =
        document.getElementById(
            "statusText"
        );


    try {

        const response =
            await fetch(
                "http://127.0.0.1:8000/",
                {
                    method: "GET"
                }
            );


        if (response) {

            dot.classList.add("online");
            dot.classList.remove("offline");

            text.textContent =
                "Backend online";

        }

    } catch (error) {

        dot.classList.remove("online");
        dot.classList.add("offline");

        text.textContent =
            "Backend offline";

    }

}


/* =====================================================
   TOAST
===================================================== */

let toastTimer;


function showToast(
    message,
    type = "success"
) {

    const toast =
        document.getElementById(
            "toast"
        );


    const toastMessage =
        document.getElementById(
            "toastMessage"
        );


    const toastIcon =
        document.getElementById(
            "toastIcon"
        );


    toastMessage.textContent =
        message;


    if (type === "error") {

        toastIcon.textContent = "✕";

        toastIcon.style.color =
            "var(--danger)";

    } else {

        toastIcon.textContent = "✓";

        toastIcon.style.color =
            "var(--success)";

    }


    toast.classList.add("show");


    clearTimeout(toastTimer);


    toastTimer =
        setTimeout(
            () => {
                toast.classList.remove("show");
            },
            3000
        );

}


/* =====================================================
   FORMAT AI TEXT
===================================================== */

function formatAIText(text) {

    if (text === null || text === undefined) {
        return "";
    }


    let safe =
        escapeHTML(String(text));


    safe =
        safe.replace(
            /\*\*(.*?)\*\*/g,
            "<strong>$1</strong>"
        );


    safe =
        safe.replace(
            /\n/g,
            "<br>"
        );


    return safe;

}


/* =====================================================
   ESCAPE HTML
===================================================== */

function escapeHTML(value) {

    return String(value)

        .replace(
            /&/g,
            "&amp;"
        )

        .replace(
            /</g,
            "&lt;"
        )

        .replace(
            />/g,
            "&gt;"
        )

        .replace(
            /"/g,
            "&quot;"
        )

        .replace(
            /'/g,
            "&#039;"
        );

}


/* =====================================================
   GLOBAL FUNCTIONS
   Needed by HTML onclick
===================================================== */

window.openPage =
    openPage;

window.editVehicle =
    editVehicle;

window.deleteVehicle =
    deleteVehicle;

window.viewVehicle =
    viewVehicle;

window.sendAIQuickPrompt =
    sendAIQuickPrompt;

window.askMaintenance =
    askMaintenance;

window.askAppointments =
    askAppointments;

window.askServices =
    askServices;

window.showPage =
    showPage;