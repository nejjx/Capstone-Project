function sendMessage() {
  var userInput = document.getElementById("user-input");
  var message = userInput.value.trim();
  if (message !== "") {
    appendMessage("You", message);
    userInput.value = "";
  }
}

function handleKeyPress(event) {
  if (event.keyCode === 13) { // Check if Enter key is pressed
    sendMessage();
  }
}

function appendMessage(sender, message) {
  var chatBox = document.getElementById("chat-box");
  var messageElement = document.createElement("div");
  messageElement.innerHTML = "<strong>" + sender + ":</strong> " + message;
  chatBox.appendChild(messageElement);
  // Automatically scroll to the bottom of the chat box
  chatBox.scrollTop = chatBox.scrollHeight;
}
