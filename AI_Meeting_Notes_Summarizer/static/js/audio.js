//Refrences 
//Drag and Drop HTML: https://www.w3schools.com/html/html5_draganddrop.asp
// Drag and Drop Image Uploader : https://www.youtube.com/watch?v=5Fws9daTtIs
//JSON Parse: https://www.w3schools.com/js/js_json_parse.asp
//Form Data : https://developer.mozilla.org/en-US/docs/Web/API/FormData/FormData
//Javascript Tenerary Operater: https://www.w3schools.com/jsref/jsref_oper_conditional.asp

// These lines retrieve specific elements from the HTML document by their IDs.
// They allow JavaScript to read content, modify content, or attach behaviors to these comments 
const dropArea = document.getElementById("drop-area");
const inputFile = document.getElementById("audio-file");
const fileView = document.getElementById("file-view");

const startbutton = document.getElementById("start-btn")

// When the user selects a file manually using the file input, the "change"
// event fires. We call handleUpload() to process the newly selected file.
inputFile.addEventListener("change", handleUpload);

// This function runs whenever the user selects a file (manually or via drag/drop).
// It reads the selected file, shows its name, and displays the Start Processing button.
function handleUpload() {
    const file = inputFile.files[0];

    // If no file was selected (e.g., dialog closed), exit early
    if (!file) return;

    // Display the selected file's name inside the fileView area.
    // Using template literals allows easy insertion of HTML structure.
    fileView.innerHTML = `
        <p><strong>Selected File:</strong></p>
        <p>${file.name}</p>
    `;

    // Reveal the button that starts audio processing
    //Intially the button is hidden to prevent any accidental processing by the user.
    startbutton.style.display = "block";
}
// The browser’s default behavior is to open files when dropped.
// We prevent that so the user experience feels smooth and expected.
dropArea.addEventListener("dragover", (e) => {
    e.preventDefault();
});

// When the user releases a file over the drop area, this event fires. We capture
// the dropped files, assign them to the inputFile element so the rest of the
// code can treat them normally, and then call handleUpload().
dropArea.addEventListener("drop", (e) => {
    //Blocks default behavior 
    e.preventDefault();
    // Assign the dropped files to the input element’s files list.
    // This keeps the upload flow consistent whether the user drags or browses.
    inputFile.files = e.dataTransfer.files;
    //Calls on the handleUpload function to process the uploaded file
    handleUpload();
});
// When the user clicks the Start Processing button, we verify a file exists,
startbutton.addEventListener("click", () => {
    //Retreieves the file once more to ensure file exsists 
    const file = inputFile.files[0];
    // If no file is selected, prompt user to upload a file first
    if (!file) {
        alert("Please upload a file first.");
        return;
    }
    // Update button UI to indicate the process has begun
    startbutton.textContent = "Processing...";
    startbutton.disabled = true;
    //Calling the process Audio function to send the audio file to the backend to begin processing. 
    processAudio(file);
});

// This function sends the uploaded audio file to the backend server using a POST
// request. The server processes the file (transcription and analysis) and returns JSON
// containing results such as transcript, summary, decisions, and action items.
async function processAudio(file) {
    try {
        // Create a FormData object to package the audio file for sending
        const formData = new FormData();
        // The server expects "audio" as the field name
        formData.append("audio", file);

        // Send the POST request to the backend API
        const response = await fetch("http://127.0.0.1:5000/fileUpload/upload", {
            method: "POST",
            body: formData
        });
        // Convert server response to JSON
        const data = await response.json();
        // If server sends an error field, display it to the user
        if (data.error) {
            alert("Error: " + data.error);
            return;
        }

        document.getElementById("result").style.display = "block";
        // Insert the transcript text from the server into the UI
        document.getElementById("transcript").textContent = data.transcript;
        // Extract JSON object embedded inside the analysis text
        const analysis = extractJSON(data.analysis);
         // Populate UI with summary, decisions, and action items
        document.getElementById("summary").textContent = analysis.summary;
        // Join arrays with newline characters for readable display
        document.getElementById("decisions").textContent = analysis.decisions.join("\n");
        document.getElementById("actions").textContent = analysis.action_items.join("\n");

    } finally {
        // Regardless of an sucessfull output or errors the button will reset to its original state. 
        startbutton.textContent = "Begin Processing Audio File";
        startbutton.disabled = false;
    }
}

// This function attempts to find and parse a JSON object embedded inside a
// larger string which also converts it into a Java Script Object.
function extractJSON(text) {
    const match = text.match(/\{[\s\S]*\}/);
    return match ? JSON.parse(match[0]) : null;
}
