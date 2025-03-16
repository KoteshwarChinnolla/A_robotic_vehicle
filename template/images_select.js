const API = "http://127.0.0.1:5000/";

const images = {
    "house": "../images/home_architecture.jpg",
    "Company": "../images/architecture_home.png"
};

let maze = []; // Store maze globally
const gridSize = 1;
const canvas = document.getElementById("mazeCanvas");
const ctx = canvas ? canvas.getContext("2d") : null;
let Thread_id = generateUniqueId();
let lastPosition = { x: 5, y: 5 };
let path = [];

function expandInput() {
    document.querySelector(".chat-input").classList.add("expanded");
}

function shrinkInput() {
    document.querySelector(".chat-input").classList.remove("expanded");
}

function generateUniqueId() {
    return 'id-' + Date.now() + '-' + Math.floor(Math.random() * 1000);
}


function speak(text) {
    const utterance = new SpeechSynthesisUtterance(text);
    window.speechSynthesis.speak(utterance);
    }
console.log(Thread_id);

fetch("../lastpossition.json")
  .then(response => response.json())
  .then(data => {
    lastPosition = data;
    last=lastPosition.lastPosition.split(" ");

    path.push(last); // Now it's updated correctly
  })
  .catch(error => console.error("Error loading JSON:", error));

  console.log(path);

function openPopup() {
    const grid = document.getElementById("imageGrid");
    grid.innerHTML = "";
    for (let name in images) {
        let img = document.createElement("img");
        img.src = images[name];
        img.alt = name;
        img.onclick = () => selectImage(name, images[name]);
        grid.appendChild(img);
    }
    document.getElementById("popup").style.display = "block";
}

function closePopup() {
    document.getElementById("popup").style.display = "none";
}

function selectImage(name, path) {
    document.getElementById("selectedText").innerText = "Selected: " + name;
    let img = document.getElementById("selectedImage");
    img.src = path;
    img.style.display = "block";
    document.getElementById("proceedBtn").style.display = "inline-block";
    closePopup();
}

function proceed() {
    let img = document.getElementById("selectedImage");
    let canvas = document.getElementById("mazeCanvas");
    let proceedBtn = document.getElementById("proceedBtn");
    let chatInput = document.getElementById("chatInput");
    const outputDiv = document.getElementById("out-put-test");
    let chatInput_2 = document.getElementById("chatInput_2");
    chatInput_2.style.display = "none";
    outputDiv.style.display = "block";
    proceedBtn.style.display = "none";
    chatInput.style.display = "flex";

    // Hide the selected image and show the canvas
    img.style.display = "none";
    canvas.style.display = "block";
    console.log((img.src).replace("http://127.0.0.1:5500/", ""));
    fetch(API + "plot_maze", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ image_link: (img.src).replace("http://127.0.0.1:5500/", "") }) // Pass image src
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        maze = data.maze; // Store maze globally
        drawMaze(maze);
    })
    .catch(error => {
        console.error("Error fetching maze data:", error);
    });

    // if (img.src) {
    //     alert("Proceeding with image: " + img.src);
    // } else {
    //     alert("No image selected. Please select an image first.");
    // }
}

function drawMaze(maze) {
    if (!ctx) return;;
    const rows = maze.length;
    const cols = maze[0].length;
    console.log(rows, cols);

    // Dynamically adjust gridSize
    const gridSize = 256 / rows;  // Since it's 256x256, gridSize will be 2.8125

    // Set canvas size dynamically
    canvas.width = 256;
    canvas.height = 256;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    for (let y = 0; y < rows; y++) {
        for (let x = 0; x < cols; x++) {
            ctx.fillStyle = maze[y][x] === 0 ? "black" : "white";
            ctx.fillRect(x, y, gridSize, gridSize);
            // ctx.strokeRect(x * gridSize, y * gridSize, gridSize, gridSize);
        }
    }

    // Draw last position in red
    ctx.fillStyle = "red";
    ctx.beginPath();
    ctx.arc(path[path.length - 1][0], path[path.length - 1][1], 3, 0, 2 * Math.PI);
    ctx.fill();
}


canvas.addEventListener("click", function(event) {
    if (!maze.length) return; // Ensure maze is loaded
    const x = Math.floor(event.offsetX / gridSize);
    const y = Math.floor(event.offsetY / gridSize);
    console.log(maze[y][x]);
    if (maze[y][x] === 1) {
        ctx.fillStyle = "green";
        ctx.fillRect(x * gridSize, y * gridSize, 3, 3);
        path.push([x * gridSize, y * gridSize]);
        console.log("here is the paths");
        console.log(path);
        if (path.length >= 1) {
            findShortestPath(maze, path[path.length - 2], path[path.length - 1]);
        }
        lastPosition = { x, y };
        }
    });

    async function sendMessage(event) {
        
        if (event) event.preventDefault(); // Prevents page refresh if inside a form
    
        const inputField = document.getElementById("user-input");
        const message = inputField.value.trim();
        if (!message) return;
        console.log("Sending message:", message);
        updateText(message);
        inputField.value = "";
    
        try {
            const response = await fetch(API + "chatInput", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text: message, name: "User", id: Thread_id })
            });
    
            const responseData = await response.json();
            let data = responseData.response;
            await send_path(data);
            delay(5000);
            await turn_on_status();
        }
        catch (error) {
            console.error("Error finding path:", error);
        }
    }

    async function turn_on_status() {
        try {
            const response = await fetch(API + "status_on", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ thread_id: Thread_id, name: "User" })
            });
    
            const responseData = await response.json();
            let data = responseData.response;
            await send_path(data);
        }
        catch (error) {
            console.error("Error finding path:", error);
        }
    }

    async function send_path(data) {
        console.log(data);
        if (typeof data === "string") { 
            updateText(data);
            speak(data);
        } else {
            for (let i = 0; i < data.length; i++) {
                console.log(typeof data[i]);
                if (typeof data[i] === "string") {
                    console.log("Processing message:", data[i]);
                    await mid_text(data[i]);  // Ensure mid_text completes before moving forward
                } else {  
                    console.log("Processing route:", data[i]);
                    let start = data[i].A.split(" ");
                    let end = data[i].B.split(" ");
                    path.push(end);
                    await findShortestPath(maze, start, end);  // Wait for pathfinding to complete
                }
            }
            console.log("All routes processed successfully!");
            let chatInput_2 = document.getElementById("chatInput_2");
            chatInput_2.style.display = "none";
            let chatInput_1 = document.getElementById("chatInput");
            chatInput_1.style.display = "flex";
        }
    }
    function updateText(text) {
        const outputDiv = document.getElementById("out-put-test");
        if (outputDiv) outputDiv.textContent = text;
    }
    async function mid_text(text) {
        speak(text);
        updateText(text);
        let chatInput = document.getElementById("chatInput");
        chatInput.style.display = "none";
        let chatInput_2 = document.getElementById("chatInput_2");
        chatInput_2.style.display = "flex";
        const response1 = await fetch(API + "question_for_user", {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: text, user_response: "", thread_id: Thread_id, name: "User" })
        });
    
        const data = await response1.json(); // Extract response text
        console.log("Response from API:", data.response[0]);
    
        let result1 = data.response[0];
    
        if (result1 === "wait") {
            console.log("Waiting for user input...");
            let result2 = await wait_until_fun(text);
            while (result2 === "wait") {
                result2 = await wait_until_fun(text);
            }
            document.getElementById("user-input").value = "";  // Clear input field after use
        } else if (result1 === "move") {
            updateText(result1);
        }
    }
    
    function waitForUserInput() {
        return new Promise(resolve => {
            let inputField = document.getElementById("userInput");
            inputField.classList.add("waiting");
            inputField.focus();
            window.resolveInput = function() {
                let value = inputField.value.trim();
                if (value) {
                    inputField.classList.remove("waiting");
                    inputField.value = ""; // Clear input
                    resolve(value);
                } else {
                    alert("Please enter a message before submitting.");
                }
            };
        });
    }
    
    async function wait_until_fun(text) {

        const message = await waitForUserInput();
    
        console.log("Sending message:", message);
        updateText(message);
    
        const response2 = await fetch(API + "user_response", {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: text, user_response: message, thread_id: Thread_id, name: "User" })
        });
    
        const data = await response2.json();
        console.log("User response result:", data.response);
        if( data.response[0][0] === "location" ){
            await send_path(data.response[1]);
        }
        let chatInput_2 = document.getElementById("chatInput_2");
        chatInput_2.style.display = "none";
        let chatInput_1 = document.getElementById("chatInput");
        chatInput_1.style.display = "flex";
        return data.response[0];  // Extract response text
    }
    
    
    async function findShortestPath(maze, start, end) {
        try {
            const response = await fetch(API + "a_star_algo", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ maze: maze, start: { x: start[1], y: start[0] }, end: { x: end[1], y: end[0] } })
            });
    
            const data = await response.json();
            console.log(data);
    
            await plotPath(data);  // Wait for plotting to complete before continuing
        } catch (error) {
            console.error("Error finding path:", error);
        }
    }
    function drawArrow(ctx, fromX, fromY, toX, toY) {
        const headLength = 4; // Arrowhead size
        const angle = Math.atan2(toY - fromY, toX - fromX); // Angle of direction
    
        ctx.strokeStyle = "blue";
        ctx.lineWidth = 4;
    
        // Draw line
        ctx.beginPath();
        ctx.lineTo(fromX, fromY);
        ctx.moveTo(toX, toY);
        ctx.stroke();
    
        // Draw arrowhead
        ctx.beginPath();
        ctx.moveTo(toX, toY);
        ctx.lineTo(toX - headLength * Math.cos(angle - Math.PI / 6), toY - headLength * Math.sin(angle - Math.PI / 6));
        ctx.lineTo(toX - headLength * Math.cos(angle + Math.PI / 6), toY - headLength * Math.sin(angle + Math.PI / 6));
        ctx.lineTo(toX, toY);
        ctx.fillStyle = "blue";
        ctx.fill();
    }
    
    
    async function plotPath(path) {
        console.log("here is the paths");
        path = path.path;
        console.log(path);
    
        ctx.beginPath();
        ctx.moveTo(path[0].x, path[0].y);
    
        for (let i = 1; i < path.length; i++) {
            console.log(path[i][0], path[i][1]);
            await delay(100); // Wait for 100ms before drawing the next line
            drawArrow(ctx, path[i - 1][1], path[i - 1][0], path[i][1], path[i][0]);
        }
    
        return true; // Ensure the function completes properly
    }
    
    function delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    

window.addEventListener("beforeunload", function(event) {
    fetch(API + "saveLastPath", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ end: String(path[path.length - 1][0] + " " + path[path.length - 1][1]) })
    });

    // Optional: Display a warning before closing (not always reliable in modern browsers)
    event.preventDefault();
    event.returnValue = ''; // Some browsers require this for a confirmation dialog
});

function resetMaze() {
    path = [];
    localStorage.removeItem("lastPosition");
    lastPosition = { x: 5, y: 5 };
    if (maze.length) drawMaze(maze); // Ensure maze is available
}

// Draw initial maze
canvas.style.display = "none";
