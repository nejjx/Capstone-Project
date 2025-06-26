

document.addEventListener("DOMContentLoaded", () => {
  const cropLabels = ["Maize", "Potatoes", "Rice, paddy", "Sorghum", "Soybeans", "Sweet potatoes", "Wheat"];
  let currentCropIndex = -1;
  let pesticideAmounts = [];
  let isAskingForInfo = false;

  appendMessage("Chatbot", "Please enter your address.");

  // Function to send user input to the backend
  function sendUserInput(userInput, endpoint, callback) {
    fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ user_input: userInput })
    })
    .then(response => response.json())
    .then(data => {
      appendMessage("Chatbot", data.message);
      if (callback) callback();
    })
    .catch(error => console.error('Error processing user input:', error));
  }

  // Function to ask for the next pesticide amount
  function askForNextPesticideAmount() {
    currentCropIndex++;
    if (currentCropIndex < cropLabels.length) {
      appendMessage("Chatbot", `Please enter the pesticide amount for ${cropLabels[currentCropIndex]}.`);
    } else {
      // Send the collected pesticide amounts to the backend
      sendUserInput(pesticideAmounts, '/process_pesticides_input', askForAdditionalInfo);
    }
  }

  // Function to ask for additional information
  function askForAdditionalInfo() {
    appendMessage("Chatbot", "Choose one of the options (Soil, Pests, Irrigation, Agricultural Practices) to get additional information.");
    isAskingForInfo = true;
  }

  // Function to process user input
  function processUserInput() {
    const userInput = document.getElementById("user-input").value;
    appendMessage("User", userInput);

    if (currentCropIndex === -1 && !isAskingForInfo) {
      // Address input
      sendUserInput(userInput, '/process_user_input', askForNextPesticideAmount);
    } else if (!isAskingForInfo) {
      // Pesticide amount input
      pesticideAmounts.push({ crop: cropLabels[currentCropIndex], amount: userInput });
      askForNextPesticideAmount();
    } else {
      // Information request input
      sendUserInput(userInput, '/process_information_request_input', () => { isAskingForInfo = false; });
    }

    document.getElementById("user-input").value = ''; // Clear input field
  }

  // Function to handle key press event
  function handleKeyPress(event) {
    if (event.key === 'Enter') {
      processUserInput();
    }
  }

  // Attach event listener to input field for Enter key press
  document.getElementById("user-input").addEventListener("keypress", handleKeyPress);

  // Attach event listener to the send button for click event
  document.getElementById("send-button").addEventListener("click", processUserInput);
});

function appendMessage(sender, message) {
  var chatBox = document.getElementById("chat-box");
  var messageElement = document.createElement("div");
  messageElement.innerHTML = "<strong>" + sender + ":</strong> " + message;
  chatBox.appendChild(messageElement);
  // Automatically scroll to the bottom of the chat box
  chatBox.scrollTop = chatBox.scrollHeight;
}



